from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from academics.models import Class, Subject, ClassSubject, Chapter, Concept
from accounts.models import StudentProfile
from games.models import GameTemplate, Game, GameLevel, Question, QuestionOption

class AIAPITests(APITestCase):
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
        
        self.user = User.objects.create_user(username="aistudent", email="ai@example.com", password="password")
        self.profile = StudentProfile.objects.create(user=self.user, student_class=self.class_obj)
        
        # Subject and concept
        self.subject = Subject.objects.create(title="Math", subtitle="Math", olympiad_code="IMO", icon_type="math", color_theme={})
        self.class_subject = ClassSubject.objects.create(student_class=self.class_obj, subject=self.subject)
        self.chapter = Chapter.objects.create(class_subject=self.class_subject, name="Ch 1", order=1)
        self.concept = Concept.objects.create(chapter=self.chapter, name="Concept 1", description="desc", order=1)
        
        # Game elements
        self.template = GameTemplate.objects.create(name="MCQ", slug="mcq")
        self.game = Game.objects.create(concept=self.concept, template=self.template, title="Math Game")
        self.game_level = GameLevel.objects.create(game=self.game, difficulty="easy")
        
        # Question option
        self.question = Question.objects.create(game_level=self.game_level, text="What is 2+2?")
        self.opt_wrong = QuestionOption.objects.create(question=self.question, text="3", is_correct=False, order=1)
        self.opt_correct = QuestionOption.objects.create(question=self.question, text="4", is_correct=True, order=2)

        self.client.force_authenticate(user=self.user)

    def test_explain_concept(self):
        url = reverse("ai:explain")
        response = self.client.post(url, {"concept_id": self.concept.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("explanation", response.data["data"])

    def test_feedback_wrong_answer(self):
        url = reverse("ai:feedback")
        payload = {
            "question_id": self.question.id,
            "selected_option_id": self.opt_wrong.id
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("feedback", response.data["data"])
        self.assertEqual(response.data["data"]["selected_option"], "3")

    def test_smart_hint(self):
        url = reverse("ai:hint")
        response = self.client.post(url, {"question_id": self.question.id, "attempts_count": 1}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("hint", response.data["data"])
