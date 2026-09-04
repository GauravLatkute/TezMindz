from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from academics.models import Class, Subject, ClassSubject, Chapter, Concept
from accounts.models import StudentProfile
from progress.models import ConceptMastery

class ProgressAPITests(APITestCase):
    def setUp(self):
        self.class_obj = Class.objects.create(
            grade_number=5,
            name="Grade 5",
            class_label="Class 5",
            stage="Olympiad Challenger",
            age_group="Age 10-11",
            category="middle"
        )
        
        self.user = User.objects.create_user(username="progstudent", email="prog@example.com", password="password")
        self.profile = StudentProfile.objects.create(user=self.user, student_class=self.class_obj, xp=100, coins=50)
        
        self.subject = Subject.objects.create(title="Math", subtitle="Math", olympiad_code="IMO", icon_type="math", color_theme={})
        self.class_subject = ClassSubject.objects.create(student_class=self.class_obj, subject=self.subject)
        self.chapter = Chapter.objects.create(class_subject=self.class_subject, name="Ch 1", order=1)
        self.concept = Concept.objects.create(chapter=self.chapter, name="Concept 1", description="desc", order=1)
        
        # Seed concept mastery
        self.mastery = ConceptMastery.objects.create(
            student=self.profile,
            concept=self.concept,
            mastery_score=85.50,
            accuracy=90.00,
            attempts_count=5,
            completed_games_count=2
        )

        self.client.force_authenticate(user=self.user)

    def test_progress_overview(self):
        url = reverse("progress:overview")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["overall_mastery"], 85.50)

    def test_subject_progress(self):
        url = reverse("progress:subjects")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["subject_title"], "Math")
        self.assertEqual(response.data["data"][0]["total_concepts"], 1)

    def test_chapter_progress(self):
        url = reverse("progress:chapters")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["chapter_name"], "Ch 1")

    def test_concept_progress(self):
        url = reverse("progress:concepts")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["concept_name"], "Concept 1")
        self.assertEqual(response.data["data"][0]["mastery_score"], 85.50)

    def test_concept_mastery_list(self):
        url = reverse("progress:mastery")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]), 1)

    def test_student_dashboard(self):
        url = reverse("progress:student_dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["student"]["name"], "progstudent")
        self.assertEqual(response.data["data"]["stats"]["level"], 1)
        self.assertEqual(len(response.data["data"]["subjects"]), 1)
        self.assertEqual(len(response.data["data"]["daily_missions"]), 4)
