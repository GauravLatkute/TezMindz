from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.management import call_command
from academics.models import Class, Subject, ClassSubject, Chapter, Concept, Quiz, QuizQuestion, QuizOption
from learning.models import Lesson
from games.models import Game, GameTemplate, GameLevel, GameSession
from progress.models import StudentTopicProgress, QuizAttempt
from accounts.models import StudentProfile


class Chapter1WeTheTravellersTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Seed Chapter 1 using our idempotent management command
        call_command("seed_chapter1")

        self.cls5 = Class.objects.get(grade_number=5)
        self.math = Subject.objects.get(title="Mathematics")
        self.ch1 = Chapter.objects.get(class_subject__student_class=self.cls5, class_subject__subject=self.math, order=1)
        self.topic1 = self.ch1.concepts.get(order=1)
        self.topic2 = self.ch1.concepts.get(order=2)
        self.game1 = self.topic1.games.first()
        self.quiz1 = self.topic1.quizzes.first()

        # Create a student user
        self.user = User.objects.create_user(username="traveller_student", email="traveller@test.com", password="password123", first_name="Aarav")
        self.profile = StudentProfile.objects.create(user=self.user, student_class=self.cls5)

    def test_chapter1_structure_and_10_topics(self):
        """Verify Chapter 1 exists and has exactly 10 topics in order."""
        self.assertEqual(self.ch1.name, "We the Travellers – I")
        self.assertEqual(self.ch1.concepts.count(), 10)

        topic_names = list(self.ch1.concepts.order_by("order").values_list("name", flat=True))
        expected_names = [
            "Reading and Writing Large Numbers",
            "Place Value",
            "Expanded Form and Standard Form",
            "Number Names",
            "Comparing Large Numbers",
            "Ordering Numbers",
            "Making Numbers Using Digits",
            "Large Numbers in Real Life",
            "Number Patterns and Puzzles",
            "Logical Number Challenges"
        ]
        self.assertEqual(topic_names, expected_names)

    def test_complete_user_journey_topic1_to_topic2(self):
        """
        Tests the complete student journey:
        Login -> Dashboard -> Chapter 1 -> Topic 1 (Learn -> Game -> Quiz) -> Topic 1 Mastered -> Topic 2 Unlocked.
        """
        self.client.login(username="traveller_student", password="password123")

        # 1. Open Chapter 1
        res = self.client.get(f"/chapter/{self.ch1.id}/")
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "We the Travellers – I")
        self.assertContains(res, "Reading and Writing Large Numbers")

        # 2. Topic 1 is initially unlocked, Game and Quiz are locked
        res_t1 = self.client.get(f"/concept/{self.topic1.id}/")
        self.assertEqual(res_t1.status_code, 200)

        # Direct access to Game & Quiz is blocked
        self.assertEqual(self.client.get(f"/game/{self.game1.id}/play/").status_code, 302)
        self.assertEqual(self.client.get(f"/quiz/{self.quiz1.id}/").status_code, 302)
        # Direct access to Topic 2 is blocked
        self.assertEqual(self.client.get(f"/concept/{self.topic2.id}/").status_code, 302)

        # 3. Complete Topic 1 Learn
        res_learn = self.client.post("/api/lesson/complete/", {
            "concept_id": self.topic1.id
        }, content_type="application/json")
        self.assertEqual(res_learn.status_code, 200)
        self.assertTrue(res_learn.json()["game_unlocked"])

        # Game is now unlocked
        res_game = self.client.get(f"/game/{self.game1.id}/play/")
        self.assertEqual(res_game.status_code, 200)
        self.assertContains(res_game, "Goal: Build the Number Train!")

        # 4. Submit Game
        res_game_submit = self.client.post("/api/game/submit/", {
            "game_id": self.game1.id,
            "difficulty": "easy",
            "score": 100,
            "accuracy": 100.0,
            "time_spent": 30,
            "hints_used": 1
        }, content_type="application/json")
        self.assertEqual(res_game_submit.status_code, 200)
        self.assertTrue(res_game_submit.json()["quiz_unlocked"])

        # Quiz is now unlocked
        res_quiz = self.client.get(f"/quiz/{self.quiz1.id}/")
        self.assertEqual(res_quiz.status_code, 200)

        # 5. Submit Quiz with correct answers
        answers = {}
        for q in self.quiz1.questions.all():
            corr_opt = q.options.filter(is_correct=True).first()
            if corr_opt:
                answers[str(q.id)] = corr_opt.id

        res_quiz_submit = self.client.post("/api/quiz/submit/", {
            "quiz_id": self.quiz1.id,
            "answers": answers,
            "time_taken": 45,
            "hints_used": 0
        }, content_type="application/json")
        self.assertEqual(res_quiz_submit.status_code, 200)
        self.assertTrue(res_quiz_submit.json()["is_mastered"])

        # 6. Verify Topic 1 is Mastered and Topic 2 is Unlocked!
        tp1 = StudentTopicProgress.objects.get(student=self.profile, concept=self.topic1)
        self.assertTrue(tp1.is_mastered)
        self.assertEqual(tp1.mastery_percentage, 100.0)

        tp2 = StudentTopicProgress.objects.get(student=self.profile, concept=self.topic2)
        self.assertTrue(tp2.is_unlocked)

        # Topic 2 is now accessible
        res_t2 = self.client.get(f"/concept/{self.topic2.id}/")
        self.assertEqual(res_t2.status_code, 200)
