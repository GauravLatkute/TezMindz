"""
Scoring Service for Tezz-Mindz Game Engine.
Server-side source of truth for points, bonuses, and penalties.
"""


def calculate_attempt_score(
    base_points: int,
    is_correct: bool,
    time_taken: int,
    time_limit: int,
    hints_used: int = 0,
    difficulty: str = "medium"
) -> dict:
    """
    Calculates the score for a single attempt.
    Considers:
      - Correctness (100% of base points if correct, 0 if wrong)
      - Speed Bonus (up to +20% if answered in under half the time limit)
      - Hint Penalty (-15 points per hint used)
    """
    if not is_correct:
        return {
            "points": 0,
            "speed_bonus": 0,
            "hint_penalty": 0,
            "total_points": 0
        }

    points = base_points

    # Speed bonus: If answered under 50% of time limit, grant bonus
    speed_bonus = 0
    if time_limit > 0 and time_taken < (time_limit * 0.5):
        speed_bonus = int(points * 0.2)  # 20% bonus

    # Hint penalty: 15 points per hint
    hint_penalty = min(points, hints_used * 15)

    total = max(10, points + speed_bonus - hint_penalty)

    return {
        "points": points,
        "speed_bonus": speed_bonus,
        "hint_penalty": hint_penalty,
        "total_points": total
    }


def calculate_session_summary(attempts: list, total_contents: int, total_time: int) -> dict:
    """
    Calculates overall session score, accuracy percentage, and passed status.
    """
    correct_count = sum(1 for a in attempts if a.is_correct)
    total_score = sum(a.points_earned for a in attempts)
    accuracy = round((correct_count / len(attempts) * 100), 2) if attempts else 0.0

    return {
        "score": total_score,
        "correct_count": correct_count,
        "total_attempts": len(attempts),
        "accuracy": accuracy,
        "time_spent": total_time,
        "is_perfect": correct_count == len(attempts) and len(attempts) >= total_contents
    }
