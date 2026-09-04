from django.urls import path
from progress.views import (
    ProgressOverviewView,
    SubjectProgressView,
    ChapterProgressView,
    ConceptProgressView,
    ConceptMasteryListView,
    StudentDashboardView
)

app_name = "progress"

urlpatterns = [
    path("", ProgressOverviewView.as_view(), name="overview"),
    path("dashboard/", StudentDashboardView.as_view(), name="student_dashboard"),
    path("subjects/", SubjectProgressView.as_view(), name="subjects"),
    path("chapters/", ChapterProgressView.as_view(), name="chapters"),
    path("concepts/", ConceptProgressView.as_view(), name="concepts"),
    path("mastery/", ConceptMasteryListView.as_view(), name="mastery"),
]
