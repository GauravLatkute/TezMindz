from django.urls import path
from rewards.views import (
    RewardsSummaryView,
    XPTransactionListView,
    CoinTransactionListView,
    BadgeListView,
    AchievementsListView,
    StreakDetailsView,
    BuyCourseView
)

app_name = "rewards"

urlpatterns = [
    path("", RewardsSummaryView.as_view(), name="summary"),
    path("buy-course/", BuyCourseView.as_view(), name="buy_course"),
    path("xp/", XPTransactionListView.as_view(), name="xp"),
    path("coins/", CoinTransactionListView.as_view(), name="coins"),
    path("badges/", BadgeListView.as_view(), name="badges"),
    path("achievements/", AchievementsListView.as_view(), name="achievements"),
    path("streak/", StreakDetailsView.as_view(), name="streak"),
]
