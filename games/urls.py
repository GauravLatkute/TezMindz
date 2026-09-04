from django.urls import path
from games.views import (
    dream_house_builder_player_view,
    dream_house_builder_result_view,
    GameListAPIView,
    GameDetailAPIView,
    GameLevelsListAPIView,
    GameStartBySlugAPIView,
    GameSessionSubmitAPIView,
    GameSessionHintAPIView,
    GameSessionCompleteAPIView,
    GameProgressAPIView,
    GameStartView,
    GameSubmitView,
    GameCompleteView,
    MistakesListView,
)

app_name = "games"

urlpatterns = [
    # ── Reusable HTML Game Engine Views ──────────────────────────────────────
    path("dream-house-builder/", dream_house_builder_player_view, name="dream_house_builder"),
    path("dream-house-builder/result/<int:session_id>/", dream_house_builder_result_view, name="dream_house_builder_result"),

    # ── Reusable Game Engine REST API Endpoints (mounted at /api/games/) ─────
    path("", GameListAPIView.as_view(), name="api_game_list"),
    path("progress/", GameProgressAPIView.as_view(), name="api_game_progress"),
    path("<slug:slug>/", GameDetailAPIView.as_view(), name="api_game_detail"),
    path("<slug:slug>/levels/", GameLevelsListAPIView.as_view(), name="api_game_levels"),
    path("<slug:slug>/start/", GameStartBySlugAPIView.as_view(), name="api_game_start_by_slug"),
    path("sessions/<int:session_id>/submit/", GameSessionSubmitAPIView.as_view(), name="api_session_submit"),
    path("sessions/<int:session_id>/hint/", GameSessionHintAPIView.as_view(), name="api_session_hint"),
    path("sessions/<int:session_id>/complete/", GameSessionCompleteAPIView.as_view(), name="api_session_complete"),

    # ── Legacy Endpoints Preserved for Backward Compatibility ────────────────
    path("mistakes/", MistakesListView.as_view(), name="mistakes_list"),
    path("<int:id>/start/", GameStartView.as_view(), name="game_start"),
    path("<int:session_id>/submit/", GameSubmitView.as_view(), name="game_submit"),
    path("<int:session_id>/complete/", GameCompleteView.as_view(), name="game_complete"),
]
