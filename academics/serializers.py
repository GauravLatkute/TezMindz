from rest_framework import serializers
from academics.models import Class, Subject, ClassSubject, Chapter, Concept

class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ["id", "grade_number", "name", "class_label", "stage", "age_group", "category"]


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id", "title", "subtitle", "olympiad_code", "icon_type", "color_theme"]


class ClassSubjectSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    
    class Meta:
        model = ClassSubject
        fields = ["id", "subject", "total_modules"]


class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ["id", "name", "order"]


class ConceptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concept
        fields = ["id", "name", "description", "real_world_example", "order"]
