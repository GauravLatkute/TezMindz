from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import GradeViewSet, SubjectViewSet, TopicViewSet, ConceptViewSet

app_name = "curriculum"

# Initialize the router and register viewsets
router = DefaultRouter()
router.register(r"grades", GradeViewSet, basename="grade")
router.register(r"subjects", SubjectViewSet, basename="subject")
router.register(r"topics", TopicViewSet, basename="topic")
router.register(r"concepts", ConceptViewSet, basename="concept")

# URL patterns
urlpatterns = [
    path("", include(router.urls)),
]
