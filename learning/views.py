from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from learning.models import Lesson
from learning.serializers import LessonSerializer

class LessonDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, id):
        try:
            lesson = Lesson.objects.get(id=id)
        except Lesson.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Lesson not found",
                    "errors": {"detail": "Lesson does not exist."}
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = LessonSerializer(lesson)
        return Response({
            "success": True,
            "message": "Lesson details retrieved successfully",
            "data": serializer.data
        })
