from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from academics.models import Class, Subject, ClassSubject, Chapter, Concept
from academics.serializers import (
    ClassSerializer,
    SubjectSerializer,
    ClassSubjectSerializer,
    ChapterSerializer,
    ConceptSerializer
)
from learning.models import Lesson
from learning.serializers import LessonSerializer
from games.models import Game
from games.serializers import GameSerializer

class ClassListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        classes = Class.objects.all().order_by("grade_number")
        serializer = ClassSerializer(classes, many=True)
        return Response({
            "success": True,
            "message": "Classes retrieved successfully",
            "data": serializer.data
        })


class ClassSubjectListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, class_id):
        class_subjects = ClassSubject.objects.filter(student_class_id=class_id)
        serializer = ClassSubjectSerializer(class_subjects, many=True)
        return Response({
            "success": True,
            "message": "Subjects for class retrieved successfully",
            "data": serializer.data
        })


class ChapterListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, subject_id):
        class_id = request.query_params.get("class_id")
        if not class_id:
            return Response(
                {
                    "success": False,
                    "message": "Missing required query parameter: class_id",
                    "errors": {"class_id": ["This parameter is required."]}
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        chapters = Chapter.objects.filter(
            class_subject__student_class_id=class_id,
            class_subject__subject_id=subject_id
        ).order_by("order")
        
        serializer = ChapterSerializer(chapters, many=True)
        return Response({
            "success": True,
            "message": "Chapters retrieved successfully",
            "data": serializer.data
        })


class ConceptListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, chapter_id):
        concepts = Concept.objects.filter(chapter_id=chapter_id).order_by("order")
        serializer = ConceptSerializer(concepts, many=True)
        return Response({
            "success": True,
            "message": "Concepts retrieved successfully",
            "data": serializer.data
        })


class ConceptDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, id):
        try:
            concept = Concept.objects.get(id=id)
        except Concept.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Concept not found",
                    "errors": {"detail": "Concept does not exist."}
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ConceptSerializer(concept)
        return Response({
            "success": True,
            "message": "Concept details retrieved successfully",
            "data": serializer.data
        })


class ConceptLessonListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, id):
        lessons = Lesson.objects.filter(concept_id=id).order_by("order")
        serializer = LessonSerializer(lessons, many=True)
        return Response({
            "success": True,
            "message": "Lessons retrieved successfully",
            "data": serializer.data
        })


class ConceptGameListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, id):
        games = Game.objects.filter(concept_id=id)
        serializer = GameSerializer(games, many=True)
        return Response({
            "success": True,
            "message": "Games retrieved successfully",
            "data": serializer.data
        })
