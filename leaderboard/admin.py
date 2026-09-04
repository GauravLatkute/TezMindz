from django.contrib import admin
from leaderboard.models import LeaderboardEntry


@admin.register(LeaderboardEntry)
class LeaderboardEntryAdmin(admin.ModelAdmin):
    list_display = ["rank", "student", "student_class", "xp", "level", "games_played", "quizzes_passed", "updated_at"]
    list_filter = ["student_class"]
    search_fields = ["student__user__username"]
    readonly_fields = ["updated_at"]
    ordering = ["student_class", "rank"]
