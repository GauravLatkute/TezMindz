from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend

from .models import Grade, Subject, Topic, Concept
from .serializers import (
    GradeSerializer,
    SubjectSerializer,
    TopicDetailSerializer,
    TopicListSerializer,
    TopicCreateUpdateSerializer,
    ConceptSerializer,
)


class GradeViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Grade objects.
    
    Endpoints:
    - GET /api/curriculum/grades/          → List all grades
    - POST /api/curriculum/grades/         → Create new grade
    - GET /api/curriculum/grades/{id}/     → Retrieve grade
    - PUT /api/curriculum/grades/{id}/     → Update grade
    - PATCH /api/curriculum/grades/{id}/   → Partial update
    - DELETE /api/curriculum/grades/{id}/  → Delete grade
    """
    
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["name"]
    ordering_fields = ["order", "name", "created_at"]
    ordering = ["order"]
    
    def get_permissions(self):
        """Allow authenticated users to list/retrieve, admin-only for write operations."""
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]


class SubjectViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Subject objects.
    
    Endpoints:
    - GET /api/curriculum/subjects/          → List all subjects
    - POST /api/curriculum/subjects/         → Create new subject
    - GET /api/curriculum/subjects/{id}/     → Retrieve subject
    - PUT /api/curriculum/subjects/{id}/     → Update subject
    - PATCH /api/curriculum/subjects/{id}/   → Partial update
    - DELETE /api/curriculum/subjects/{id}/  → Delete subject
    """
    
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["name"]
    search_fields = ["name", "slug"]
    ordering_fields = ["order", "name", "created_at"]
    ordering = ["order"]
    
    def get_permissions(self):
        """Allow authenticated users to list/retrieve, admin-only for write operations."""
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]


class TopicViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Topic objects with filtering and publishing support.
    
    Endpoints:
    - GET /api/curriculum/topics/                  → List all topics
    - POST /api/curriculum/topics/                 → Create new topic
    - GET /api/curriculum/topics/{id}/             → Retrieve topic
    - PUT /api/curriculum/topics/{id}/             → Update topic
    - PATCH /api/curriculum/topics/{id}/           → Partial update
    - DELETE /api/curriculum/topics/{id}/          → Delete topic
    - POST /api/curriculum/topics/{id}/publish/    → Publish topic
    - GET /api/curriculum/topics/published/        → List only published topics
    """
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["grade", "subject", "difficulty", "status"]
    search_fields = ["title", "description"]
    ordering_fields = ["order", "created_at", "published_at"]
    ordering = ["grade__order", "subject__order", "order"]
    
    def get_queryset(self):
        """
        Return all topics for admins/staff; only published topics for students.
        """
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Topic.objects.all()
        return Topic.published.all()
    
    def get_serializer_class(self):
        """Use different serializers for different actions."""
        if self.action == "retrieve":
            return TopicDetailSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return TopicCreateUpdateSerializer
        return TopicListSerializer
    
    def get_permissions(self):
        """Allow authenticated users to list/retrieve, admin-only for write operations."""
        if self.action in ["create", "update", "partial_update", "destroy", "publish"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser()])
    def publish(self, request, pk=None):
        """
        Publish a topic by setting its status to PUBLISHED.
        
        POST /api/curriculum/topics/{id}/publish/
        """
        topic = self.get_object()
        topic.publish()
        serializer = TopicDetailSerializer(topic)
        return Response(
            {"message": "Topic published successfully", "topic": serializer.data},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=["get"])
    def published(self, request):
        """
        Retrieve only published topics (alias for standard filtering).
        
        GET /api/curriculum/topics/published/
        """
        queryset = Topic.published.all()
        queryset = self.filter_queryset(queryset)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TopicListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = TopicListSerializer(queryset, many=True)
        return Response(serializer.data)


class ConceptViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Concept objects.
    
    Endpoints:
    - GET /api/curriculum/concepts/          → List all concepts
    - POST /api/curriculum/concepts/         → Create new concept
    - GET /api/curriculum/concepts/{id}/     → Retrieve concept
    - PUT /api/curriculum/concepts/{id}/     → Update concept
    - PATCH /api/curriculum/concepts/{id}/   → Partial update
    - DELETE /api/curriculum/concepts/{id}/  → Delete concept
    - POST /api/curriculum/concepts/{id}/publish/ → Publish concept
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = ConceptSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["topic", "status"]
    search_fields = ["title", "content_body"]
    ordering_fields = ["order", "created_at", "published_at"]
    ordering = ["topic", "order"]
    
    def get_queryset(self):
        """
        Return all concepts for admins/staff; only published concepts for students.
        """
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Concept.objects.all()
        return Concept.published.all()
    
    def get_permissions(self):
        """Allow authenticated users to list/retrieve, admin-only for write operations."""
        if self.action in ["create", "update", "partial_update", "destroy", "publish"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser()])
    def publish(self, request, pk=None):
        """
        Publish a concept by setting its status to PUBLISHED.
        
        POST /api/curriculum/concepts/{id}/publish/
        """
        concept = self.get_object()
        concept.status = "published"
        from django.utils import timezone
        concept.published_at = timezone.now()
        concept.save()
        serializer = ConceptSerializer(concept)
        return Response(
            {"message": "Concept published successfully", "concept": serializer.data},
            status=status.HTTP_200_OK
        )

