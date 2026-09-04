from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from academics.models import Class, Subject, ClassSubject, Chapter, Concept
from learning.models import Lesson

class LearningAPITests(APITestCase):
    def setUp(self):
        # Create dependencies
        self.class_obj = Class.objects.create(
            grade_number=5,
            name="Grade 5",
            class_label="Class 5",
            stage="Olympiad Challenger",
            age_group="Age 10-11",
            category="middle"
        )
        self.subject = Subject.objects.create(
            title="Mathematics",
            subtitle="Numbers and Logic",
            olympiad_code="IMO",
            icon_type="math",
            color_theme={"bg": "bg-amber-100"}
        )
        self.class_subject = ClassSubject.objects.create(
            student_class=self.class_obj,
            subject=self.subject,
            total_modules=5
        )
        self.chapter = Chapter.objects.create(
            class_subject=self.class_subject,
            name="Fractions",
            order=1
        )
        self.concept = Concept.objects.create(
            chapter=self.chapter,
            name="Understanding Fractions",
            description="Concept description",
            order=1
        )
        self.lesson = Lesson.objects.create(
            concept=self.concept,
            title="Introduction to Fractions",
            content_markdown="This is markdown content.",
            illustration_url="http://example.com/image.png",
            order=1
        )

    def test_lesson_detail_success(self):
        url = reverse("learning:lesson_detail", kwargs={"id": self.lesson.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["title"], "Introduction to Fractions")
        self.assertEqual(response.data["data"]["content_markdown"], "This is markdown content.")

    def test_lesson_detail_not_found(self):
        url = reverse("learning:lesson_detail", kwargs={"id": 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["success"])
