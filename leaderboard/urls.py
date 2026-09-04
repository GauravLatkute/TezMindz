from django.urls import path
from leaderboard.views import (
    WeeklyLeaderboardView,
    MonthlyLeaderboardView,
    MyLeaderboardRankView
)

app_name = "leaderboard"

urlpatterns = [
    path("weekly/", WeeklyLeaderboardView.as_view(), name="weekly"),
    path("monthly/", MonthlyLeaderboardView.as_view(), name="monthly"),
    path("me/", MyLeaderboardRankView.as_view(), name="me"),
]
