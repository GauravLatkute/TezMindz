from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Sum, Q
from django.utils import timezone
from accounts.models import StudentProfile
from rewards.models import XPTransaction

class LeaderboardBaseView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_leaderboard_data(self, days=None):
        if days:
            start_date = timezone.now() - timezone.timedelta(days=days)
            # Aggregate XP transactions in the timeframe
            profiles = StudentProfile.objects.annotate(
                timeframe_xp=Sum("xp_transactions__points", filter=Q(xp_transactions__created_at__gte=start_date))
            ).filter(timeframe_xp__gt=0).order_by("-timeframe_xp")[:50]
        else:
            # Fallback to total cumulative XP
            profiles = StudentProfile.objects.order_by("-xp")[:50]

        data = []
        for index, profile in enumerate(profiles):
            xp_value = getattr(profile, "timeframe_xp", None)
            if xp_value is None:
                xp_value = profile.xp

            data.append({
                "rank": index + 1,
                "student_id": profile.id,
                "display_name": profile.user.first_name or profile.user.username,
                "avatar": profile.avatar,
                "xp": xp_value,
                "is_me": profile.user == self.request.user
            })
        return data


class WeeklyLeaderboardView(LeaderboardBaseView):
    def get(self, request):
        data = self.get_leaderboard_data(days=7)
        return Response({
            "success": True,
            "message": "Weekly leaderboard retrieved successfully",
            "data": data
        })


class MonthlyLeaderboardView(LeaderboardBaseView):
    def get(self, request):
        data = self.get_leaderboard_data(days=30)
        return Response({
            "success": True,
            "message": "Monthly leaderboard retrieved successfully",
            "data": data
        })


class MyLeaderboardRankView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        
        # Calculate overall rank
        overall_rank = StudentProfile.objects.filter(xp__gt=profile.xp).count() + 1
        
        # Calculate weekly rank
        start_week = timezone.now() - timezone.timedelta(days=7)
        my_weekly_xp = XPTransaction.objects.filter(
            student=profile, created_at__gte=start_week
        ).aggregate(Sum("points"))["points__sum"] or 0
        
        better_weekly_students = StudentProfile.objects.annotate(
            weekly_xp=Sum("xp_transactions__points", filter=Q(xp_transactions__created_at__gte=start_week))
        ).filter(weekly_xp__gt=my_weekly_xp).count()
        
        weekly_rank = better_weekly_students + 1

        return Response({
            "success": True,
            "message": "My ranking stats retrieved successfully",
            "data": {
                "username": profile.user.username,
                "display_name": profile.user.first_name or profile.user.username,
                "avatar": profile.avatar,
                "overall_xp": profile.xp,
                "overall_rank": overall_rank,
                "weekly_xp": my_weekly_xp,
                "weekly_rank": weekly_rank
            }
        })
