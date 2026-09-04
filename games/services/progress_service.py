"""
Progress Service for Tezz-Mindz Game Engine.
Tracks game level unlocking, persistent game progress, and student topic mastery.
"""
from django.utils import timezone
from games.models import GameProgress, GameSession, GameLevel
from progress.models import StudentTopicProgress


def update_student_game_progress(student_profile, game, current_level_num: int, score: int, is_game_completed: bool = False) -> GameProgress:
    """
    Updates or creates persistent GameProgress for the student.
    """
    total_levels = game.levels.count() or 5
    progress, _ = GameProgress.objects.get_or_create(
        student=student_profile,
        game=game,
        defaults={
            "current_level": 1,
            "highest_level": 1,
            "best_score": 0,
            "completion_percentage": 0.0,
            "is_completed": False
        }
    )

    # Calculate completion percentage
    completion_pct = round((min(current_level_num, total_levels) / total_levels * 100), 2)
    if is_game_completed:
        completion_pct = 100.0
        progress.is_completed = True

    progress.current_level = min(current_level_num, total_levels)
    progress.highest_level = max(progress.highest_level, current_level_num)
    progress.best_score = max(progress.best_score, score)
    progress.completion_percentage = max(progress.completion_percentage, completion_pct)
    progress.last_played_at = timezone.now()
    progress.save()

    # Also update StudentTopicProgress if concept exists
    if is_game_completed and game.concept:
        try:
            topic_prog = StudentTopicProgress.objects.get(student=student_profile, concept=game.concept)
            topic_prog.mark_game_complete()
        except StudentTopicProgress.DoesNotExist:
            pass

    return progress
