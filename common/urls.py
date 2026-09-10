from django.urls import path, re_path
from django.views.generic import RedirectView
from common import views

app_name = "common"

urlpatterns = [
    # ── Public ────────────────────────────────────────────────────────────────
    path("", views.landing_page, name="landing"),
    path("about/", views.about_page, name="about"),
    path("subjects/", views.subjects_page, name="subjects"),
    path("how-it-works/", views.how_it_works_page, name="how_it_works"),
    path("login/", views.login_page, name="login"),
    path("register/", views.register_page, name="register"),
    path("logout/", views.logout_page, name="logout"),
    path("class/", views.class_select_page, name="class_select"),

    # ── Core App ──────────────────────────────────────────────────────────────
    path("dashboard/", views.dashboard_page, name="dashboard"),

    # Learning hierarchy
    path("learn/", views.learn_page, name="learn"),
    path("subject/<int:cs_id>/", views.subject_page, name="subject"),
    path("chapter/<int:chapter_id>/", views.chapter_page, name="chapter"),
    path("concept/<int:concept_id>/", views.concept_page, name="concept"),

    # Quiz
    path("quiz/<int:quiz_id>/", views.quiz_page, name="quiz"),
    path("quiz/result/<int:attempt_id>/", views.quiz_result_page, name="quiz_result"),

    # Games
    path("games/", views.games_page, name="games"),
    path("game/<int:game_id>/difficulty/", views.difficulty_page, name="difficulty"),
    path("game/<int:game_id>/play/", views.game_page, name="game_play"),
    path("result/", views.result_page, name="result"),

    # Progress / Rewards / Leaderboard
    path("progress/", views.progress_page, name="progress"),
    path("rewards/", views.rewards_page, name="rewards"),
    path("leaderboard/", views.leaderboard_page, name="leaderboard"),
    path("achievements/", views.achievements_page, name="achievements"),
    path("profile/", views.profile_page, name="profile"),

    # ── API Endpoints (JSON) ───────────────────────────────────────────────────
    path("api/learn/complete/", views.api_complete_lesson, name="api_complete_learn"),
    path("api/lesson/complete/", views.api_complete_lesson, name="api_complete_lesson"),
    path("api/quiz/submit/", views.api_submit_quiz, name="api_submit_quiz"),
    path("api/game/submit/", views.api_submit_game, name="api_submit_game"),
    path("api/explain/question/", views.api_explain_question, name="api_explain_question"),

    # ── Legacy HTML redirect fallbacks ────────────────────────────────────────
    re_path(r".*index\.html$", RedirectView.as_view(url="/", permanent=True)),
    re_path(r".*about\.html$", RedirectView.as_view(url="/about/", permanent=True)),
    re_path(r".*subjects\.html$", RedirectView.as_view(url="/subjects/", permanent=True)),
    re_path(r".*how-it-works\.html$", RedirectView.as_view(url="/how-it-works/", permanent=True)),
    re_path(r".*login\.html$", RedirectView.as_view(url="/login/", permanent=True)),
    re_path(r".*register\.html$", RedirectView.as_view(url="/register/", permanent=True)),
    re_path(r".*class\.html$", RedirectView.as_view(url="/class/", permanent=True)),
    re_path(r".*dashboard\.html$", RedirectView.as_view(url="/dashboard/", permanent=True)),
    re_path(r".*learn\.html$", RedirectView.as_view(url="/learn/", permanent=True)),
    re_path(r".*chapter\.html$", RedirectView.as_view(url="/chapter/1/", permanent=True)),
    re_path(r".*concept\.html$", RedirectView.as_view(url="/concept/1/", permanent=True)),
    re_path(r".*difficulty\.html$", RedirectView.as_view(url="/game/1/difficulty/", permanent=True)),
    re_path(r".*games\.html$", RedirectView.as_view(url="/games/", permanent=True)),
    re_path(r".*game\.html$", RedirectView.as_view(url="/game/1/play/", permanent=True)),
    re_path(r".*result\.html$", RedirectView.as_view(url="/result/", permanent=True)),
    re_path(r".*progress\.html$", RedirectView.as_view(url="/progress/", permanent=True)),
    re_path(r".*rewards\.html$", RedirectView.as_view(url="/rewards/", permanent=True)),
    re_path(r".*leaderboard\.html$", RedirectView.as_view(url="/leaderboard/", permanent=True)),
    re_path(r".*profile\.html$", RedirectView.as_view(url="/profile/", permanent=True)),
]
