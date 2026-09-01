from rest_framework import serializers
from .models import Grade, Subject, Topic, Concept


class GradeSerializer(serializers.ModelSerializer):
    """Serializer for Grade model."""
    
    class Meta:
        model = Grade
        fields = ["id", "name", "order", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class SubjectSerializer(serializers.ModelSerializer):
    """Serializer for Subject model."""
    
    class Meta:
        model = Subject
        fields = ["id", "name", "slug", "order", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class TopicListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Topic list views."""
    
    grade = serializers.StringRelatedField()
    subject = serializers.StringRelatedField()
    
    class Meta:
        model = Topic
        fields = [
            "id",
            "title",
            "grade",
            "subject",
            "difficulty",
            "status",
            "published_at",
            "order",
            "created_at",
        ]
        read_only_fields = ["created_at", "updated_at", "published_at"]


class TopicDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Topic with nested relationships."""
    
    grade_name = serializers.CharField(source="grade.name", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    prerequisites = TopicListSerializer(many=True, read_only=True)
    prerequisite_ids = serializers.PrimaryKeyRelatedField(
        queryset=Topic.objects.all(),
        many=True,
        write_only=True,
        source="prerequisites"
    )
    
    class Meta:
        model = Topic
        fields = [
            "id",
            "title",
            "description",
            "grade",
            "grade_name",
            "subject",
            "subject_name",
            "difficulty",
            "learning_objectives",
            "prerequisites",
            "prerequisite_ids",
            "estimated_minutes",
            "order",
            "status",
            "published_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "published_at"]


class ConceptSerializer(serializers.ModelSerializer):
    """Serializer for Concept model with topic details."""
    
    topic_title = serializers.CharField(source="topic.title", read_only=True)
    topic_grade = serializers.CharField(source="topic.grade.name", read_only=True)
    
    class Meta:
        model = Concept
        fields = [
            "id",
            "topic",
            "topic_title",
            "topic_grade",
            "title",
            "content_body",
            "order",
            "status",
            "published_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "published_at"]


class TopicCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer specifically for creating/updating Topic with nested prerequisites."""
    
    prerequisite_ids = serializers.PrimaryKeyRelatedField(
        queryset=Topic.objects.all(),
        many=True,
        source="prerequisites",
        required=False
    )
    
    class Meta:
        model = Topic
        fields = [
            "id",
            "title",
            "description",
            "grade",
            "subject",
            "difficulty",
            "learning_objectives",
            "prerequisite_ids",
            "estimated_minutes",
            "order",
        ]
