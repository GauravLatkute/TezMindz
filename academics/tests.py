from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from academics.models import Class, Subject, ClassSubject, Chapter, Concept
from learning.models import Lesson
from games.models import Game, GameTemplate

class AcademicsAPITests(APITestCase):
    def setUp(self):
        # Create Class
        self.class_obj = Class.objects.create(
            grade_number=5,
            name="Grade 5",
            class_label="Class 5",
            stage="Olympiad Challenger",
            age_group="Age 10-11",
            category="middle"
        )
        
        # Create Subject
        self.subject_obj = Subject.objects.create(
            title="Mathematics",
            subtitle="Numbers and Logic",
            olympiad_code="IMO",
            icon_type="math",
            color_theme={"bg": "bg-amber-100", "badgeBg": "bg-amber-500"}
        )
        
        # Connect via ClassSubject
        self.class_subject = ClassSubject.objects.create(
            student_class=self.class_obj,
            subject=self.subject_obj,
            total_modules=10
        )
        
        # Create Chapter
        self.chapter = Chapter.objects.create(
            class_subject=self.class_subject,
            name="Fractions",
            order=1
        )
        
        # Create Concept
        self.concept = Concept.objects.create(
            chapter=self.chapter,
            name="Understanding Fractions",
            description="Basic introduction to parts of a whole.",
            real_world_example="Pizza slices",
            order=1
        )
        
        # Create Lesson
        self.lesson = Lesson.objects.create(
            concept=self.concept,
            title="What is a fraction?",
            content_markdown="Fraction explanation...",
            order=1
        )

        # Create Game Template & Game
        self.game_template = GameTemplate.objects.create(
            name="MCQ Quiz",
            slug="mcq",
            description="Multiple Choice Quiz Template"
        )
        self.game = Game.objects.create(
            concept=self.concept,
            template=self.game_template,
            title="Fraction Quest"
        )

    def test_class_list(self):
        url = reverse("academics:class_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["name"], "Grade 5")

    def test_class_subject_list(self):
        url = reverse("academics:class_subject_list", kwargs={"class_id": self.class_obj.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["subject"]["title"], "Mathematics")

    def test_chapter_list_success(self):
        url = reverse("academics:chapter_list", kwargs={"subject_id": self.subject_obj.id})
        response = self.client.get(url, {"class_id": self.class_obj.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["name"], "Fractions")

    def test_chapter_list_missing_class_id(self):
        url = reverse("academics:chapter_list", kwargs={"subject_id": self.subject_obj.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_concept_list(self):
        url = reverse("academics:concept_list", kwargs={"chapter_id": self.chapter.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["name"], "Understanding Fractions")

    def test_concept_detail(self):
        url = reverse("academics:concept_detail", kwargs={"id": self.concept.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["name"], "Understanding Fractions")

    def test_concept_lessons(self):
        url = reverse("academics:concept_lessons", kwargs={"id": self.concept.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["title"], "What is a fraction?")

    def test_concept_games(self):
        url = reverse("academics:concept_games", kwargs={"id": self.concept.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["title"], "Fraction Quest")
