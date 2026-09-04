from django.urls import path
from learning.views import LessonDetailView

app_name = "learning"

urlpatterns = [
    path("lessons/<int:id>/", LessonDetailView.as_view(), name="lesson_detail"),
]
