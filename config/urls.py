"""
URL configuration for TezMindz project.
Includes base path routing for modular components under /api/ namespaces.
"""

from django.contrib import admin
from django.urls import path, include
from games.views import (
    dream_house_builder_player_view,
    dream_house_builder_result_view,
    GameSessionSubmitAPIView,
    GameSessionHintAPIView,
    GameSessionCompleteAPIView,
    GameProgressAPIView,
    QuestionHintView
)

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # ── Page views ────────────────────────────────────────────────────────────
    path("tezadmin/", include("common.admin_urls")),
    path("", include("common.urls")),
    path("games/dream-house-builder/", dream_house_builder_player_view, name="dream_house_builder"),
    path("games/dream-house-builder/result/<int:session_id>/", dream_house_builder_result_view, name="dream_house_builder_result"),

    # ── Modular App APIs ──────────────────────────────────────────────────────
    path("api/auth/", include("accounts.urls")),
    path("api/academics/", include("academics.urls")),
    path("api/learning/", include("learning.urls")),
    path("api/games/", include("games.urls")),
    path("api/game-progress/", GameProgressAPIView.as_view(), name="api_game_progress_root"),
    path("api/game-sessions/<int:session_id>/submit/", GameSessionSubmitAPIView.as_view(), name="api_session_submit_root"),
    path("api/game-sessions/<int:session_id>/hint/", GameSessionHintAPIView.as_view(), name="api_session_hint_root"),
    path("api/game-sessions/<int:session_id>/complete/", GameSessionCompleteAPIView.as_view(), name="api_session_complete_root"),
    path("api/progress/", include("progress.urls")),
    path("api/rewards/", include("rewards.urls")),
    path("api/leaderboard/", include("leaderboard.urls")),
    path("api/ai/", include("ai.urls")),
    path("api/notifications/", include("notifications.urls")),
    
    # Questions Hint routing
    path("api/questions/<int:id>/hint/", QuestionHintView.as_view(), name="question_hint"),
]
