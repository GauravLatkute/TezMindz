from django.contrib import admin
from games.models import (
    GameTemplate,
    Game,
    GameLevel,
    GameContent,
    GameHint,
    GameReward,
    GameSession,
    GameAttempt,
    GameProgress,
)


class GameLevelInline(admin.TabularInline):
    model = GameLevel
    extra = 1
    fields = ("level_number", "title", "difficulty", "time_limit", "points", "xp_reward", "coin_reward", "is_locked")


class GameContentInline(admin.TabularInline):
    model = GameContent
    extra = 1
    fields = ("level", "content_type", "question", "points", "display_order")


class GameHintInline(admin.TabularInline):
    model = GameHint
    extra = 1


@admin.register(GameTemplate)
class GameTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "game_type", "concept", "difficulty", "xp_reward", "coin_reward", "is_active")
    list_filter = ("game_type", "difficulty", "is_active")
    search_fields = ("title", "slug", "concept__name")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [GameLevelInline, GameContentInline]


@admin.register(GameLevel)
class GameLevelAdmin(admin.ModelAdmin):
    list_display = ("game", "level_number", "title", "difficulty", "time_limit", "points", "xp_reward", "coin_reward", "is_locked")
    list_filter = ("game", "difficulty", "is_locked")
    search_fields = ("title", "game__title")
    inlines = [GameContentInline, GameHintInline]


@admin.register(GameContent)
class GameContentAdmin(admin.ModelAdmin):
    list_display = ("game", "level", "content_type", "question", "points", "difficulty", "display_order")
    list_filter = ("game", "content_type", "difficulty")
    search_fields = ("question", "game__title")
    inlines = [GameHintInline]


@admin.register(GameHint)
class GameHintAdmin(admin.ModelAdmin):
    list_display = ("content", "level", "order", "text", "cost_points")
    list_filter = ("order",)


@admin.register(GameReward)
class GameRewardAdmin(admin.ModelAdmin):
    list_display = ("game", "reward_type", "title", "xp_reward", "coin_reward", "badge_icon")
    list_filter = ("reward_type", "game")


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "game", "current_level", "status", "score", "accuracy", "time_spent", "hints_used", "xp_earned", "coins_earned", "started_at")
    list_filter = ("status", "game", "difficulty")
    search_fields = ("student__user__username", "game__title")
    readonly_fields = ("started_at", "completed_at")


@admin.register(GameAttempt)
class GameAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "level", "content", "is_correct", "time_taken", "hints_used", "points_earned", "created_at")
    list_filter = ("is_correct", "created_at")


@admin.register(GameProgress)
class GameProgressAdmin(admin.ModelAdmin):
    list_display = ("student", "game", "current_level", "highest_level", "best_score", "completion_percentage", "is_completed", "last_played_at")
    list_filter = ("is_completed", "game")
    search_fields = ("student__user__username", "game__title")
