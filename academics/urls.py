from django.urls import path
from academics.views import (
    ClassListView,
    ClassSubjectListView,
    ChapterListView,
    ConceptListView,
    ConceptDetailView,
    ConceptLessonListView,
    ConceptGameListView
)

app_name = "academics"

urlpatterns = [
    path("classes/", ClassListView.as_view(), name="class_list"),
    path("classes/<int:class_id>/subjects/", ClassSubjectListView.as_view(), name="class_subject_list"),
    path("subjects/<int:subject_id>/chapters/", ChapterListView.as_view(), name="chapter_list"),
    path("chapters/<int:chapter_id>/concepts/", ConceptListView.as_view(), name="concept_list"),
    path("concepts/<int:id>/", ConceptDetailView.as_view(), name="concept_detail"),
    path("concepts/<int:id>/lessons/", ConceptLessonListView.as_view(), name="concept_lessons"),
    path("concepts/<int:id>/games/", ConceptGameListView.as_view(), name="concept_games"),
]
