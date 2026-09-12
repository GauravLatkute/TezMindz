from rest_framework import serializers
from games.models import (
    Game,
    GameTemplate,
    GameLevel,
    GameContent,
    GameHint,
    GameReward,
    GameSession,
    GameAttempt,
    GameProgress,
    Question,
    QuestionOption,
    Attempt,
)


class GameHintSafeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameHint
        fields = ["id", "order", "text", "cost_points"]


class GameContentSafeSerializer(serializers.ModelSerializer):
    """Safe serializer that never exposes correct_answer to the frontend!"""
    hints = GameHintSafeSerializer(many=True, read_only=True)

    class Meta:
        model = GameContent
        fields = [
            "id",
            "content_type",
            "question",
            "data",
            "points",
            "difficulty",
            "display_order",
            "hints"
        ]


class GameLevelSafeSerializer(serializers.ModelSerializer):
    contents = GameContentSafeSerializer(many=True, read_only=True)
    is_locked = serializers.SerializerMethodField()

    class Meta:
        model = GameLevel
        fields = [
            "id",
            "level_number",
            "title",
            "instructions",
            "difficulty",
            "time_limit",
            "points",
            "xp_reward",
            "coin_reward",
            "configuration",
            "is_locked",
            "unlock_requirement",
            "contents"
        ]

    def get_is_locked(self, obj):
        return False


class GameProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameProgress
        fields = [
            "id",
            "game_id",
            "current_level",
            "highest_level",
            "best_score",
            "completion_percentage",
            "is_completed",
            "last_played_at"
        ]


class GameSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameSession
        fields = [
            "id",
            "game",
            "current_level",
            "difficulty",
            "started_at",
            "completed_at",
            "status",
            "score",
            "accuracy",
            "time_spent",
            "hints_used",
            "xp_earned",
            "coins_earned",
            "session_data"
        ]


class GameDetailSerializer(serializers.ModelSerializer):
    levels = GameLevelSafeSerializer(many=True, read_only=True)
    user_progress = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = [
            "id",
            "title",
            "slug",
            "game_type",
            "description",
            "instructions",
            "difficulty",
            "thumbnail",
            "estimated_time",
            "xp_reward",
            "coin_reward",
            "config",
            "levels",
            "user_progress"
        ]

    def get_user_progress(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated and hasattr(request.user, "profile"):
            prog = GameProgress.objects.filter(student=request.user.profile, game=obj).first()
            if prog:
                return GameProgressSerializer(prog).data
        return None


# ── Legacy Serializers Preserved for Backward Compatibility ─────────────────────
class QuestionOptionSafeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ["id", "text", "order"]


class QuestionSafeSerializer(serializers.ModelSerializer):
    options = QuestionOptionSafeSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "text", "image_url", "options"]


class AttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attempt
        fields = [
            "id", "session", "question", "selected_option",
            "is_correct", "time_taken", "hints_used", "points_earned", "created_at"
        ]


class GameTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameTemplate
        fields = ["id", "name", "slug", "description"]


class GameSerializer(serializers.ModelSerializer):
    template = GameTemplateSerializer(read_only=True)

    class Meta:
        model = Game
        fields = ["id", "concept", "template", "title", "slug", "game_type", "config"]
