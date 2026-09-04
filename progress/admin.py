from django.contrib import admin
from progress.models import ConceptMastery, LessonProgress, QuizAttempt, StudentTopicProgress


@admin.register(StudentTopicProgress)
class StudentTopicProgressAdmin(admin.ModelAdmin):
    list_display = [
        "student", "concept", "is_unlocked",
        "learn_completed", "game_unlocked", "game_completed", "game_score",
        "quiz_unlocked", "quiz_completed", "quiz_score",
        "is_mastered", "mastery_percentage", "updated_at"
    ]
    list_filter = ["is_unlocked", "learn_completed", "game_completed", "quiz_completed", "is_mastered"]
    search_fields = ["student__user__username", "concept__name"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(ConceptMastery)
class ConceptMasteryAdmin(admin.ModelAdmin):
    list_display = ["student", "concept", "mastery_score", "accuracy", "completed_games_count", "last_attempt_date"]
    list_filter = ["concept__chapter__class_subject__subject", "concept__chapter__class_subject__student_class"]
    search_fields = ["student__user__username", "concept__name"]
    readonly_fields = ["last_attempt_date", "created_at", "updated_at"]


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ["student", "lesson", "completed", "completed_at", "xp_earned"]
    list_filter = ["completed", "lesson__concept__chapter__class_subject__student_class"]
    search_fields = ["student__user__username", "lesson__title"]
    readonly_fields = ["created_at"]


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ["student", "quiz", "score", "total_marks", "percentage", "passed", "xp_earned", "started_at"]
    list_filter = ["passed", "quiz__concept__chapter__class_subject__student_class"]
    search_fields = ["student__user__username", "quiz__title"]
    readonly_fields = ["started_at", "completed_at"]
