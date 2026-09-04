from rest_framework import serializers
from learning.models import Lesson

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "concept", "title", "content_markdown", "illustration_url", "order"]
