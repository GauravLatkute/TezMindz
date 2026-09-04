"""
Game Service for Tezz-Mindz Game Engine.
Coordinates session lifecycle, question validation, scoring, and level transitions.
"""
from django.utils import timezone
from games.models import Game, GameLevel, GameContent, GameSession, GameAttempt, GameHint
from games.services.scoring_service import calculate_attempt_score, calculate_session_summary
from games.services.reward_service import calculate_and_award_rewards
from games.services.progress_service import update_student_game_progress
from games.utils.indian_number_system import format_indian_number


def start_or_resume_session(student_profile, game: Game) -> GameSession:
    """
    Finds an existing in-progress session or creates a new one.
    """
    session = GameSession.objects.filter(
        student=student_profile,
        game=game,
        status__in=["STARTED", "IN_PROGRESS"]
    ).order_by("-started_at").first()

    if not session:
        session = GameSession.objects.create(
            student=student_profile,
            game=game,
            current_level=1,
            difficulty=game.difficulty,
            status="STARTED",
            session_data={"levels_completed": [], "house_stage": 0}
        )
    return session


def validate_content_answer(content: GameContent, student_answer) -> bool:
    """
    Validates a student's answer against the database content record.
    Never trusts client-provided correctness.
    """
    content_type = content.content_type
    correct_data = content.correct_answer or {}

    # Extract target correct value
    target_val = correct_data.get("value") or correct_data.get("number") or correct_data.get("answer") or correct_data.get("order")

    if content_type == "read_number":
        # Can be matching string, option text, or normalized string
        student_val = str(student_answer.get("value", "")).strip().lower()
        target_str = str(target_val).strip().lower()
        return student_val == target_str

    elif content_type == "build_number":
        # Can be numeric or string of digits
        try:
            student_num = int(str(student_answer.get("number", student_answer.get("value", ""))).replace(",", "").strip())
            target_num = int(str(target_val).replace(",", "").strip())
            return student_num == target_num
        except (ValueError, TypeError):
            return False

    elif content_type == "place_value":
        student_val = str(student_answer.get("value", "")).replace(",", "").strip().lower()
        target_str = str(target_val).replace(",", "").strip().lower()
        return student_val == target_str

    elif content_type == "compare_order":
        # Check if comparing operator or ordering list
        if "operator" in correct_data:
            return str(student_answer.get("operator", "")).strip() == str(correct_data["operator"]).strip()
        elif "order" in correct_data or isinstance(target_val, list):
            student_order = student_answer.get("order", [])
            target_order = correct_data.get("order", target_val)
            # Normalize to integer lists
            try:
                s_list = [int(str(x).replace(",", "")) for x in student_order]
                t_list = [int(str(x).replace(",", "")) for x in target_order]
                return s_list == t_list
            except (ValueError, TypeError):
                return False

    elif content_type == "budget_verification":
        if "is_correct_budget" in correct_data and "is_correct_budget" in student_answer:
            return bool(student_answer["is_correct_budget"]) == bool(correct_data["is_correct_budget"])
        student_val = student_answer.get("value", "")
        target_val = correct_data.get("value", "")
        return str(student_val).strip().lower() == str(target_val).strip().lower()

    # Default fallback
    return str(student_answer.get("value", "")).strip().lower() == str(target_val).strip().lower()


def process_level_submission(
    session: GameSession,
    level_id: int,
    content_id: int,
    student_answer: dict,
    time_taken: int,
    hints_used: int
) -> dict:
    """
    Processes and scores an attempt on backend.
    """
    try:
        content = GameContent.objects.get(id=content_id, game=session.game)
    except GameContent.DoesNotExist:
        return {"success": False, "message": "Content not found."}

    level = content.level

    # Server-side answer validation
    is_correct = validate_content_answer(content, student_answer)

    # Server-side score calculation
    time_limit = level.time_limit if level else 60
    base_points = content.points or 100
    score_result = calculate_attempt_score(
        base_points=base_points,
        is_correct=is_correct,
        time_taken=time_taken,
        time_limit=time_limit,
        hints_used=hints_used
    )

    # Record Attempt
    attempt = GameAttempt.objects.create(
        session=session,
        level=level,
        content=content,
        student_answer=student_answer,
        is_correct=is_correct,
        time_taken=time_taken,
        hints_used=hints_used,
        points_earned=score_result["total_points"]
    )

    # Update session metrics
    session.score += score_result["total_points"]
    session.hints_used += hints_used
    session.time_spent += time_taken
    session.status = "IN_PROGRESS"

    # Track level completion in session_data
    session_data = session.session_data or {}
    completed_levels = session_data.get("levels_completed", [])
    if is_correct and level and level.level_number not in completed_levels:
        completed_levels.append(level.level_number)
        session_data["levels_completed"] = completed_levels
        session_data["house_stage"] = max(session_data.get("house_stage", 0), level.level_number)
        session.current_level = min(level.level_number + 1, 5)

    session.session_data = session_data
    session.save()

    # Update persistent progress
    update_student_game_progress(
        student_profile=session.student,
        game=session.game,
        current_level_num=session.current_level,
        score=session.score,
        is_game_completed=False
    )

    return {
        "success": True,
        "is_correct": is_correct,
        "points_earned": score_result["total_points"],
        "speed_bonus": score_result["speed_bonus"],
        "hint_penalty": score_result["hint_penalty"],
        "current_score": session.score,
        "current_level": session.current_level,
        "house_stage": session_data.get("house_stage", 0),
        "explanation": content.explanation or "Well done! Construction stage unlocked."
    }


def complete_game_session(session: GameSession) -> dict:
    """
    Finalizes the game session, calculates metrics, and distributes rewards.
    """
    attempts = list(session.game_attempts.all())
    total_contents = session.game.contents.count() or 5
    summary = calculate_session_summary(attempts, total_contents, session.time_spent)

    session.status = "COMPLETED"
    session.completed_at = timezone.now()
    session.score = summary["score"]
    session.accuracy = summary["accuracy"]
    session.save()

    # Award rewards
    rewards = calculate_and_award_rewards(
        student_profile=session.student,
        game=session.game,
        session=session,
        is_completed=True,
        accuracy=session.accuracy
    )

    # Finalize progress
    update_student_game_progress(
        student_profile=session.student,
        game=session.game,
        current_level_num=5,
        score=session.score,
        is_game_completed=True
    )

    return {
        "success": True,
        "session_id": session.id,
        "score": session.score,
        "accuracy": session.accuracy,
        "time_spent": session.time_spent,
        "attempts_count": len(attempts),
        "correct_count": summary["correct_count"],
        "xp_earned": session.xp_earned,
        "coins_earned": session.coins_earned,
        "is_completed": True
    }
