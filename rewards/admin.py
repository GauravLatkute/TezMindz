from django.contrib import admin
from rewards.models import (
    XPTransaction, CoinTransaction,
    Badge, StudentBadge,
    DailyMission, StudentMission,
    Achievement, StudentAchievement,
)


@admin.register(XPTransaction)
class XPTransactionAdmin(admin.ModelAdmin):
    list_display = ["student", "points", "reason", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["student__user__username", "reason"]
    readonly_fields = ["created_at"]


@admin.register(CoinTransaction)
class CoinTransactionAdmin(admin.ModelAdmin):
    list_display = ["student", "coins", "reason", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["student__user__username", "reason"]
    readonly_fields = ["created_at"]


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ["name", "icon", "description"]
    search_fields = ["name"]


@admin.register(StudentBadge)
class StudentBadgeAdmin(admin.ModelAdmin):
    list_display = ["student", "badge", "unlocked_at"]
    list_filter = ["unlocked_at"]
    readonly_fields = ["unlocked_at"]


@admin.register(DailyMission)
class DailyMissionAdmin(admin.ModelAdmin):
    list_display = ["title", "target_type", "target_value", "xp_reward", "coin_reward"]
    list_filter = ["target_type"]


@admin.register(StudentMission)
class StudentMissionAdmin(admin.ModelAdmin):
    list_display = ["student", "mission", "progress", "is_completed", "assigned_date"]
    list_filter = ["is_completed", "assigned_date"]


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ["icon", "name", "condition_type", "condition_value", "xp_reward", "coin_reward", "is_active"]
    list_filter = ["condition_type", "is_active"]
    search_fields = ["name", "description"]


@admin.register(StudentAchievement)
class StudentAchievementAdmin(admin.ModelAdmin):
    list_display = ["student", "achievement", "unlocked_at"]
    list_filter = ["unlocked_at"]
    search_fields = ["student__user__username", "achievement__name"]
    readonly_fields = ["unlocked_at"]
