import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from games.models import (
    Game,
    GameLevel,
    GameContent,
    GameSession,
    GameProgress,
    GameHint,
    Question,
    QuestionOption,
    Attempt,
)
from games.serializers import (
    GameSerializer,
    GameDetailSerializer,
    GameLevelSafeSerializer,
    GameContentSafeSerializer,
    GameProgressSerializer,
    GameSessionSerializer,
    QuestionSafeSerializer,
)
from games.services.game_service import (
    start_or_resume_session,
    process_level_submission,
    complete_game_session,
)
from games.permissions import IsStudentOwner
from common.views import get_user_data_context, _get_profile, _get_student_class


# ══════════════════════════════════════════════════════════════════════════════
# HTML GAME ENGINE & MODULAR RUNNER VIEWS
# ══════════════════════════════════════════════════════════════════════════════

@login_required
def modular_game_runner_view(request, game_id=None, slug=None, grade=None, subject_slug=None, chapter_num=None, topic_num=None, game_slug=None):
    """
    Unified, dynamic game runner view that loads any educational game from its
    isolated folder under games/ with standardized HUD and TezMindzGameBridge SDK.
    Supports hierarchical URLs (/class/5/mathematics/chapter/1/topic/1/game/number-builder/)
    as well as ID/slug lookups.
    """
    profile = _get_profile(request)
    
    # 1. Resolve Game instance
    target_slug = game_slug or slug
    if str(target_slug).lower() in ["none", "null", "undefined", ""]:
        target_slug = None

    if str(game_id).lower() in ["none", "null", "undefined", ""]:
        game_id = None

    if target_slug and grade and subject_slug and chapter_num and topic_num:
        game = Game.objects.select_related(
            "concept__chapter__class_subject__student_class", "concept__chapter__class_subject__subject"
        ).filter(
            slug=target_slug,
            concept__chapter__class_subject__student_class__grade_number=grade,
            concept__chapter__order=chapter_num,
            concept__order=topic_num,
            is_active=True
        ).first()
    elif target_slug:
        game = Game.objects.select_related(
            "concept__chapter__class_subject__student_class", "concept__chapter__class_subject__subject"
        ).filter(
            slug=target_slug,
            is_active=True
        ).first()
    elif game_id:
        try:
            game = Game.objects.select_related(
                "concept__chapter__class_subject__student_class", "concept__chapter__class_subject__subject"
            ).filter(
                id=int(game_id),
                is_active=True
            ).first()
        except (ValueError, TypeError):
            game = None
    else:
        game = None

    # Fallback to the student's class games or any active game
    if not game:
        student_class = _get_student_class(profile) if profile else None
        if student_class:
            game = Game.objects.filter(
                concept__chapter__class_subject__student_class=student_class,
                is_active=True
            ).first()
        if not game:
            game = Game.objects.filter(is_active=True).first()
        if not game:
            return redirect("common:games")

    concept = game.concept
    chapter = concept.chapter
    cs = chapter.class_subject
    student_class = cs.student_class

    # 2. Retrieve or start active session & progress
    session = start_or_resume_session(profile, game)
    progress, _ = GameProgress.objects.get_or_create(
        student=profile,
        game=game,
        defaults={"current_level": 1, "highest_level": 1}
    )

    # 3. Resolve relative game path & static folder
    game_path = game.game_path.strip("/\\") if game.game_path else ""
    if not game_path:
        # Fallback default path based on educational hierarchy
        subj_name = cs.subject.title.lower().replace(" ", "_")
        game_path = f"class_{student_class.grade_number}/{subj_name}/chapter_{chapter.order:02d}_{chapter.slug or 'ch'}/topic_{concept.order:02d}_{concept.slug or 'top'}/{game.slug}"

    game_static_base = f"/static/games/{game_path}/"
    
    # Check if dedicated HTML template exists in games/ directory
    full_html_path = settings.BASE_DIR / "games" / game_path / "index.html"
    has_dedicated_template = full_html_path.exists()
    game_template_rel = f"{game_path}/index.html" if has_dedicated_template else None

    # 4. Serialize level contents for client SDK
    levels = game.levels.order_by("level_number")
    levels_data = []
    for lvl in levels:
        contents = lvl.contents.all().order_by("display_order")
        levels_data.append({
            "id": lvl.id,
            "level_number": lvl.level_number,
            "title": lvl.title,
            "instructions": lvl.instructions,
            "difficulty": lvl.difficulty,
            "time_limit": lvl.time_limit,
            "points": lvl.points,
            "xp_reward": lvl.xp_reward,
            "coin_reward": lvl.coin_reward,
            "configuration": lvl.configuration,
            "is_locked": lvl.is_locked,
            "contents": [
                {
                    "id": c.id,
                    "content_type": c.content_type,
                    "question": c.question,
                    "data": c.data,
                    "points": c.points,
                    "hint": c.hint,
                    "explanation": c.explanation,
                }
                for c in contents
            ]
        })

    game_context = {
        "game": {
            "id": game.id,
            "title": game.title,
            "slug": game.slug,
            "game_type": game.game_type,
            "difficulty": game.difficulty,
            "xp_reward": game.xp_reward,
            "coin_reward": game.coin_reward,
            "game_path": game_path,
            "static_base": game_static_base,
        },
        "session": {
            "id": session.id,
            "current_level": session.current_level,
            "difficulty": session.difficulty,
            "score": session.score,
            "status": session.status,
        },
        "student": {
            "id": profile.id if profile else 0,
            "name": request.user.first_name or request.user.username,
            "xp": profile.xp if profile else 0,
            "coins": profile.coins if profile else 0,
            "streak": profile.streak if profile else 0,
            "class_grade": student_class.grade_number,
        },
        "levels": levels_data,
    }

    context = get_user_data_context(request)
    context.update({
        "game": game,
        "concept": concept,
        "chapter": chapter,
        "class_subject": cs,
        "student_class": student_class,
        "session": session,
        "progress": progress,
        "levels": levels,
        "game_path": game_path,
        "game_static_base": game_static_base,
        "has_dedicated_template": has_dedicated_template,
        "game_template_rel": game_template_rel,
        "game_context_json": json.dumps(game_context),
    })

    return render(request, "games/modular_runner.html", context)

@login_required
def dream_house_builder_player_view(request):
    """
    Renders the unified GamePlayer arena for Dream House Builder.
    """
    profile = _get_profile(request)
    game = get_object_or_404(Game, slug="dream-house-builder", is_active=True)
    
    # Check student progress
    prog, _ = GameProgress.objects.get_or_create(
        student=profile,
        game=game,
        defaults={"current_level": 1, "highest_level": 1}
    )

    context = get_user_data_context(request)
    context.update({
        "game": game,
        "progress": prog,
        "levels": game.levels.order_by("level_number"),
    })
    return render(request, "games/game_player.html", context)


@login_required
def dream_house_builder_result_view(request, session_id):
    """
    Renders the celebratory Game Result screen for Dream House Builder.
    """
    profile = _get_profile(request)
    session = get_object_or_404(GameSession, id=session_id, student=profile)
    attempts = session.game_attempts.all()

    context = get_user_data_context(request)
    context.update({
        "game": session.game,
        "session": session,
        "attempts": attempts,
        "total_attempts": attempts.count(),
        "correct_count": attempts.filter(is_correct=True).count(),
    })
    return render(request, "games/game_result.html", context)


# ══════════════════════════════════════════════════════════════════════════════
# REST API ENDPOINTS FOR REUSABLE GAME ENGINE
# ══════════════════════════════════════════════════════════════════════════════

class GameListAPIView(APIView):
    """List active games for student's class."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        student_class = _get_student_class(profile)
        games = Game.objects.filter(
            concept__chapter__class_subject__student_class=student_class,
            is_active=True
        ).select_related("concept")
        serializer = GameSerializer(games, many=True)
        return Response({"success": True, "data": serializer.data})


class GameDetailAPIView(APIView):
    """Get details, levels, and progress for a specific game."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, slug):
        game = get_object_or_404(Game, slug=slug, is_active=True)
        serializer = GameDetailSerializer(game, context={"request": request})
        return Response({"success": True, "data": serializer.data})


class GameLevelsListAPIView(APIView):
    """Get all levels and safe contents for a game."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, slug):
        game = get_object_or_404(Game, slug=slug, is_active=True)
        levels = game.levels.prefetch_related("contents__hints").order_by("level_number")
        serializer = GameLevelSafeSerializer(levels, many=True)
        return Response({"success": True, "data": serializer.data})


class GameStartBySlugAPIView(APIView):
    """
    POST /api/games/{slug}/start/
    Starts a new session or resumes an active session for the student.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        profile = request.user.profile
        game = get_object_or_404(Game, slug=slug, is_active=True)
        
        session = start_or_resume_session(profile, game)
        
        # Fetch current level data
        current_level_num = session.current_level or 1
        level = game.levels.filter(level_number=current_level_num).first()
        level_data = GameLevelSafeSerializer(level).data if level else None

        return Response({
            "success": True,
            "message": f"Session started for {game.title}",
            "data": {
                "session_id": session.id,
                "game_slug": game.slug,
                "game_type": game.game_type,
                "current_level": current_level_num,
                "status": session.status,
                "score": session.score,
                "level": level_data
            }
        })


class GameSessionSubmitAPIView(APIView):
    """
    POST /api/game-sessions/{session_id}/submit/
    Submits a student's answer for a level content.
    Server performs all validation and score calculation.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, session_id):
        profile = request.user.profile
        session = get_object_or_404(GameSession, id=session_id, student=profile)

        level_id = request.data.get("level_id")
        content_id = request.data.get("content_id")
        student_answer = request.data.get("answer", {})
        time_taken = int(request.data.get("time_taken", 0))
        hints_used = int(request.data.get("hints_used", 0))

        if not content_id:
            return Response(
                {"success": False, "message": "Missing content_id in submission."},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = process_level_submission(
            session=session,
            level_id=level_id,
            content_id=content_id,
            student_answer=student_answer,
            time_taken=time_taken,
            hints_used=hints_used
        )

        return Response(result)


class GameSessionHintAPIView(APIView):
    """
    POST /api/game-sessions/{session_id}/hint/
    Requests a hint for the active level/content and logs hints used.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, session_id):
        profile = request.user.profile
        session = get_object_or_404(GameSession, id=session_id, student=profile)

        content_id = request.data.get("content_id")
        hint_order = int(request.data.get("hint_order", 1))

        hint_obj = GameHint.objects.filter(content_id=content_id, order=hint_order).first()
        if not hint_obj:
            # Fallback to level hints or default
            hint_obj = GameHint.objects.filter(level__game=session.game, order=hint_order).first()

        hint_text = hint_obj.text if hint_obj else "Inspect the place value positions carefully from right to left."
        cost = hint_obj.cost_points if hint_obj else 10

        session.hints_used += 1
        session.save(update_fields=["hints_used"])

        return Response({
            "success": True,
            "hint": hint_text,
            "order": hint_order,
            "cost_points": cost,
            "total_hints_used": session.hints_used
        })


class GameSessionCompleteAPIView(APIView):
    """
    POST /api/game-sessions/{session_id}/complete/
    Finalizes the game session and awards XP and Coins.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, session_id):
        profile = request.user.profile
        session = get_object_or_404(GameSession, id=session_id, student=profile)

        result = complete_game_session(session)
        return Response(result)


class GameProgressAPIView(APIView):
    """GET /api/game-progress/ — Retrieves student progress across games."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        progresses = GameProgress.objects.filter(student=profile).select_related("game")
        serializer = GameProgressSerializer(progresses, many=True)
        return Response({"success": True, "data": serializer.data})


# ══════════════════════════════════════════════════════════════════════════════
# LEGACY APIS PRESERVED FOR BACKWARD COMPATIBILITY
# ══════════════════════════════════════════════════════════════════════════════

class GameStartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        difficulty = request.data.get("difficulty", "easy").lower()
        game = get_object_or_404(Game, id=id)
        profile = request.user.profile

        session = GameSession.objects.create(
            student=profile,
            game=game,
            difficulty=difficulty,
            status="STARTED"
        )
        return Response({
            "success": True,
            "data": {"session_id": session.id, "config": game.config}
        })


class QuestionHintView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        return Response({"success": True, "hint": "Look at the comma groups in the Indian system."})


class GameSubmitView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, session_id):
        return Response({"success": True, "message": "Submitted"})


class GameCompleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, session_id):
        return Response({"success": True, "message": "Completed"})


class MistakesListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({"success": True, "mistakes": []})
