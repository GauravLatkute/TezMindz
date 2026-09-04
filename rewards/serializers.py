from rest_framework import serializers
from rewards.models import XPTransaction, CoinTransaction, Badge, StudentBadge, DailyMission, StudentMission

class XPTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = XPTransaction
        fields = ["points", "reason", "created_at"]


class CoinTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoinTransaction
        fields = ["coins", "reason", "created_at"]


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ["id", "name", "description", "icon", "criteria"]


class StudentBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)

    class Meta:
        model = StudentBadge
        fields = ["id", "badge", "unlocked_at"]


class DailyMissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyMission
        fields = ["id", "title", "description", "target_type", "target_value", "xp_reward", "coin_reward"]


class StudentMissionSerializer(serializers.ModelSerializer):
    mission = DailyMissionSerializer(read_only=True)

    class Meta:
        model = StudentMission
        fields = ["id", "mission", "progress", "is_completed", "assigned_date", "updated_at"]
