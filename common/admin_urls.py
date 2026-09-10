from django.urls import path
from common import admin_views

app_name = "tezadmin"

urlpatterns = [
    # ── Executive Dashboard ───────────────────────────────────────────────────
    path("", admin_views.admin_dashboard_view, name="dashboard"),
    path("audit-logs/", admin_views.admin_audit_logs_view, name="audit_logs"),

    # ── Academic Hierarchy & Curriculum ───────────────────────────────────────
    path("academic/", admin_views.admin_academic_hierarchy_view, name="academic_hierarchy"),
    path("api/hierarchy/", admin_views.api_hierarchy_cascading, name="api_hierarchy_cascading"),
    path("api/classes/save/", admin_views.api_class_save, name="api_class_save"),
    path("api/chapters/save/", admin_views.api_chapter_save, name="api_chapter_save"),
    path("api/topics/save/", admin_views.api_topic_save, name="api_topic_save"),

    # ── Game Management & ZIP Uploader ────────────────────────────────────────
    path("games/", admin_views.admin_game_library_view, name="game_library"),
    path("games/add/", admin_views.admin_game_form_view, name="game_add"),
    path("games/<int:game_id>/edit/", admin_views.admin_game_form_view, name="game_edit"),
    path("games/<int:game_id>/toggle-status/", admin_views.admin_game_toggle_status_view, name="game_toggle_status"),
    path("games/<int:game_id>/duplicate/", admin_views.admin_game_duplicate_view, name="game_duplicate"),
    path("games/<int:game_id>/analytics/", admin_views.admin_game_analytics_view, name="game_analytics"),

    # ── Students & Gamification ───────────────────────────────────────────────
    path("students/", admin_views.admin_student_list_view, name="student_list"),
    path("students/<int:student_id>/", admin_views.admin_student_detail_view, name="student_detail"),
    path("students/<int:student_id>/toggle-active/", admin_views.admin_student_toggle_active_view, name="student_toggle_active"),
    path("gamification/", admin_views.admin_gamification_view, name="gamification"),
]
