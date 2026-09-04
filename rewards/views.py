from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.utils import timezone
from rewards.models import XPTransaction, CoinTransaction, Badge, StudentBadge, DailyMission, StudentMission
from rewards.serializers import (
    XPTransactionSerializer,
    CoinTransactionSerializer,
    StudentBadgeSerializer,
    BadgeSerializer,
    StudentMissionSerializer
)

class RewardsSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        
        badge_count = StudentBadge.objects.filter(student=profile).count()
        today = timezone.now().date()
        
        # Get active daily missions assigned to student today
        missions = StudentMission.objects.filter(student=profile, assigned_date=today)
        mission_serializer = StudentMissionSerializer(missions, many=True)

        return Response({
            "success": True,
            "message": "Rewards summary retrieved successfully",
            "data": {
                "xp": profile.xp,
                "coins": profile.coins,
                "badges_unlocked": badge_count,
                "streak": profile.streak,
                "daily_missions": mission_serializer.data
            }
        })


class XPTransactionListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        txs = XPTransaction.objects.filter(student=request.user.profile).order_by("-created_at")
        serializer = XPTransactionSerializer(txs, many=True)
        return Response({
            "success": True,
            "message": "XP transaction ledger retrieved successfully",
            "data": serializer.data
        })


class CoinTransactionListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        txs = CoinTransaction.objects.filter(student=request.user.profile).order_by("-created_at")
        serializer = CoinTransactionSerializer(txs, many=True)
        return Response({
            "success": True,
            "message": "Coin transaction ledger retrieved successfully",
            "data": serializer.data
        })


class BadgeListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        
        # Unlocked badges
        unlocked = StudentBadge.objects.filter(student=profile)
        unlocked_serializer = StudentBadgeSerializer(unlocked, many=True)
        
        # Get ids of unlocked badges
        unlocked_ids = unlocked.values_list("badge_id", flat=True)
        
        # Locked badges (all other badges in system)
        locked = Badge.objects.exclude(id__in=unlocked_ids)
        locked_serializer = BadgeSerializer(locked, many=True)

        return Response({
            "success": True,
            "message": "Badges status retrieved successfully",
            "data": {
                "unlocked": unlocked_serializer.data,
                "locked": locked_serializer.data
            }
        })


class AchievementsListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Alias for badges lists
        unlocked = StudentBadge.objects.filter(student=request.user.profile)
        serializer = StudentBadgeSerializer(unlocked, many=True)
        return Response({
            "success": True,
            "message": "Achievements list retrieved successfully",
            "data": serializer.data
        })


class StreakDetailsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        return Response({
            "success": True,
            "message": "Streak details retrieved successfully",
            "data": {
                "current_streak": profile.streak,
                "last_active_date": profile.last_activity_date,
                "longest_streak": max(profile.streak, 7) # Fallback / placeholder value
            }
        })


class BuyCourseView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        profile = request.user.profile
        if profile.is_premium:
            return Response({
                "success": False,
                "message": "You have already unlocked the Premium Pass!"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Cost is 100 Coins
        cost = 100
        if profile.coins < cost:
            return Response({
                "success": False,
                "message": f"Insufficient Coins! You need {cost} Coins to buy this course. Play more game challenges to earn coins!"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Deduct coins and save
        profile.coins -= cost
        profile.is_premium = True
        profile.save()

        # Log coin transaction
        CoinTransaction.objects.create(
            student=profile,
            coins=-cost,
            reason="Purchased Olympiad Premium Syllabus Pass"
        )

        return Response({
            "success": True,
            "message": "Congratulations! You have unlocked the Olympiad Premium Syllabus Pass!",
            "data": {
                "coins": profile.coins,
                "is_premium": profile.is_premium
            }
        })
