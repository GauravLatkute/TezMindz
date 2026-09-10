from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from academics.models import Class, Subject, ClassSubject, Chapter, Concept
from accounts.models import StudentProfile
from games.models import Game, GameLevel, GameContent, GameSession, GameAttempt, GameProgress, GameHint
from games.utils.indian_number_system import (
    format_indian_number,
    number_to_indian_words,
    expanded_form_indian,
    get_place_value
)
from games.services.scoring_service import calculate_attempt_score, calculate_session_summary
from games.services.game_service import (
    start_or_resume_session,
    validate_content_answer,
    process_level_submission,
    complete_game_session
)

User = get_user_model()


class IndianNumberSystemTests(TestCase):
    """Unit tests for Indian Numbering System formatting and words conversion."""

    def test_indian_formatting(self):
        self.assertEqual(format_indian_number(375420), "3,75,420")
        self.assertEqual(format_indian_number(100000), "1,00,000")
        self.assertEqual(format_indian_number(100001), "1,00,001")
        self.assertEqual(format_indian_number(1000000), "10,00,000")
        self.assertEqual(format_indian_number(325000), "3,25,000")
        self.assertEqual(format_indian_number(835000), "8,35,000")
        self.assertEqual(format_indian_number(9999999), "99,99,999")
        self.assertEqual(format_indian_number(500), "500")

    def test_number_to_indian_words(self):
        self.assertEqual(number_to_indian_words(250000), "Two Lakh Fifty Thousand")
        self.assertEqual(number_to_indian_words(325000), "Three Lakh Twenty-Five Thousand")
        self.assertEqual(number_to_indian_words(835000), "Eight Lakh Thirty-Five Thousand")
        self.assertEqual(number_to_indian_words(1000000), "Ten Lakh")
        self.assertEqual(number_to_indian_words(1005010), "Ten Lakh Five Thousand Ten")
        self.assertEqual(number_to_indian_words(101001), "One Lakh One Thousand One")
        self.assertEqual(number_to_indian_words(110010), "One Lakh Ten Thousand Ten")

    def test_expanded_form(self):
        self.assertEqual(expanded_form_indian(325000), ["3,00,000", "20,000", "5,000"])
        self.assertEqual(expanded_form_indian(408200), ["4,00,000", "8,000", "200"])

    def test_get_place_value(self):
        pv = get_place_value(250000, 4)  # 5th digit from right -> Ten Thousands (5)
        self.assertEqual(pv["digit"], 5)
        self.assertEqual(pv["place_name"], "Ten Thousands")
        self.assertEqual(pv["place_value"], 50000)
        self.assertEqual(pv["formatted_place_value"], "50,000")


class DreamHouseBuilderEngineTests(TestCase):
    """End-to-end unit and integration tests for Dream House Builder game."""

    def setUp(self):
        self.client = Client()

        # Create Class 5 and Academic structure
        self.cls = Class.objects.create(name="Class 5", class_label="Class 5", grade_number=5, stage="Olympiad", age_group="10-11", category="primary")
        self.subject = Subject.objects.create(title="Mathematics", subtitle="Class 5 Math", olympiad_code="IMO", icon_type="math", color_theme={})
        self.cs = ClassSubject.objects.create(student_class=self.cls, subject=self.subject)
        self.chapter = Chapter.objects.create(class_subject=self.cs, name="Large Numbers", order=1)
        self.concept = Concept.objects.create(chapter=self.chapter, name="Reading and Writing Large Numbers", order=1)

        # Create Students
        self.user1 = User.objects.create_user(username="student1", password="password123")
        self.profile1 = StudentProfile.objects.create(user=self.user1, student_class=self.cls, xp=100, coins=20)

        self.user2 = User.objects.create_user(username="student2", password="password123")
        self.profile2 = StudentProfile.objects.create(user=self.user2, student_class=self.cls)

        # Create Game
        self.game = Game.objects.create(
            concept=self.concept,
            title="Dream House Builder",
            slug="dream-house-builder",
            game_type="house_builder",
            xp_reward=50,
            coin_reward=15,
            is_active=True
        )

        # Create 5 Levels & Content
        self.level1 = GameLevel.objects.create(game=self.game, level_number=1, title="Buy the Land", time_limit=60, points=100)
        self.c1 = GameContent.objects.create(
            game=self.game,
            level=self.level1,
            content_type="read_number",
            question="Read ₹2,50,000",
            data={"price": 250000},
            correct_answer={"value": "Two Lakh Fifty Thousand"},
            points=100
        )

        self.level2 = GameLevel.objects.create(game=self.game, level_number=2, title="Build the Foundation", time_limit=90, points=150)
        self.c2 = GameContent.objects.create(
            game=self.game,
            level=self.level2,
            content_type="build_number",
            question="Build ₹3,25,000",
            data={"target_number": 325000},
            correct_answer={"number": 325000, "value": "325000"},
            points=150
        )

        self.level3 = GameLevel.objects.create(game=self.game, level_number=3, title="Buy Building Material", time_limit=75, points=150)
        self.c3 = GameContent.objects.create(
            game=self.game,
            level=self.level3,
            content_type="place_value",
            question="Place value of 5 in ₹2,50,000",
            data={"target_digit": 5},
            correct_answer={"value": "50,000 (Ten-Thousands)"},
            points=150
        )

        self.level4 = GameLevel.objects.create(game=self.game, level_number=4, title="Choose the Best Material", time_limit=90, points=150)
        self.c4_compare = GameContent.objects.create(
            game=self.game,
            level=self.level4,
            content_type="compare_order",
            question="Compare 3,12,000 and 2,45,000",
            data={"type": "comparison"},
            correct_answer={"operator": ">"},
            points=150
        )
        self.c4_order = GameContent.objects.create(
            game=self.game,
            level=self.level4,
            content_type="compare_order",
            question="Order: 1,25,000, 2,10,000, 3,50,000, 4,00,000",
            data={"type": "ordering"},
            correct_answer={"order": [125000, 210000, 350000, 400000]},
            points=150
        )

        self.level5 = GameLevel.objects.create(game=self.game, level_number=5, title="Complete Your Dream House", time_limit=120, points=200)
        self.c5 = GameContent.objects.create(
            game=self.game,
            level=self.level5,
            content_type="budget_verification",
            question="Verify budget: ₹8,35,000",
            data={"target_total_number": 835000},
            correct_answer={"is_correct_budget": True, "value": "Yes, the budget total is EXACTLY ₹8,35,000 ✓"},
            points=200
        )

    def test_session_lifecycle(self):
        """Test starting, resuming, and completing a game session."""
        session = start_or_resume_session(self.profile1, self.game)
        self.assertIsNotNone(session.id)
        self.assertEqual(session.status, "STARTED")
        self.assertEqual(session.current_level, 1)

        # Re-calling start_or_resume_session should return same session
        resumed = start_or_resume_session(self.profile1, self.game)
        self.assertEqual(session.id, resumed.id)

    def test_answer_validation(self):
        """Test server-side validation for all 5 level question types."""
        # Level 1: Read Number
        self.assertTrue(validate_content_answer(self.c1, {"value": "Two Lakh Fifty Thousand"}))
        self.assertFalse(validate_content_answer(self.c1, {"value": "Twenty-Five Thousand"}))

        # Level 2: Build Number
        self.assertTrue(validate_content_answer(self.c2, {"number": 325000, "value": "325000"}))
        self.assertTrue(validate_content_answer(self.c2, {"value": "3,25,000"}))
        self.assertFalse(validate_content_answer(self.c2, {"number": 32500, "value": "32500"}))

        # Level 3: Place Value
        self.assertTrue(validate_content_answer(self.c3, {"value": "50,000 (Ten-Thousands)"}))
        self.assertFalse(validate_content_answer(self.c3, {"value": "5,000 (Thousands)"}))

        # Level 4: Compare & Order
        self.assertTrue(validate_content_answer(self.c4_compare, {"operator": ">"}))
        self.assertFalse(validate_content_answer(self.c4_compare, {"operator": "<"}))
        self.assertTrue(validate_content_answer(self.c4_order, {"order": [125000, 210000, 350000, 400000]}))
        self.assertFalse(validate_content_answer(self.c4_order, {"order": [210000, 125000, 350000, 400000]}))

        # Level 5: Budget Verification
        self.assertTrue(validate_content_answer(self.c5, {"is_correct_budget": True}))
        self.assertFalse(validate_content_answer(self.c5, {"is_correct_budget": False}))

    def test_scoring_server_truth(self):
        """Ensure scoring is calculated on backend and cannot be spoofed by client."""
        session = start_or_resume_session(self.profile1, self.game)
        
        # Submit correct answer fast
        res = process_level_submission(
            session=session,
            level_id=self.level1.id,
            content_id=self.c1.id,
            student_answer={"value": "Two Lakh Fifty Thousand"},
            time_taken=15,
            hints_used=0
        )
        self.assertTrue(res["is_correct"])
        self.assertEqual(res["points_earned"], 120)  # 100 base + 20 speed bonus
        self.assertEqual(session.score, 120)

    def test_rewards_and_progress_on_completion(self):
        """Ensure XP, Coins, and GameProgress are updated upon completion."""
        session = start_or_resume_session(self.profile1, self.game)
        initial_xp = self.profile1.xp
        initial_coins = self.profile1.coins

        # Complete game
        result = complete_game_session(session)
        self.assertTrue(result["is_completed"])

        self.profile1.refresh_from_db()
        self.assertEqual(self.profile1.xp, initial_xp + 50)
        self.assertEqual(self.profile1.coins, initial_coins + 15)

        prog = GameProgress.objects.get(student=self.profile1, game=self.game)
        self.assertTrue(prog.is_completed)
        self.assertEqual(prog.completion_percentage, 100.0)

    def test_api_endpoints_authorization(self):
        """Test API endpoints authorization and isolation."""
        self.client.force_login(self.user1)

        # Start game API
        res = self.client.post("/api/games/dream-house-builder/start/")
        self.assertEqual(res.status_code, 200)
        session_id = res.json()["data"]["session_id"]

        # Submit answer API
        submit_res = self.client.post(
            f"/api/game-sessions/{session_id}/submit/",
            data={
                "level_id": self.level1.id,
                "content_id": self.c1.id,
                "answer": {"value": "Two Lakh Fifty Thousand"},
                "time_taken": 20,
                "hints_used": 0
            },
            content_type="application/json"
        )
        self.assertEqual(submit_res.status_code, 200)
        # Switch to student 2 - must NOT be allowed to submit to student 1's session
        self.client.force_login(self.user2)
        unauth_res = self.client.post(
            f"/api/game-sessions/{session_id}/submit/",
            data={
                "level_id": self.level1.id,
                "content_id": self.c1.id,
                "answer": {"value": "Two Lakh Fifty Thousand"}
            },
            content_type="application/json"
        )
        self.assertEqual(unauth_res.status_code, 404)  # Isolated by student profile query


class ModularGameArchitectureTests(TestCase):
    """Tests for dedicated games directory, hierarchical URLs, and isolated game runner."""

    def setUp(self):
        self.client = Client()
        self.cls = Class.objects.create(name="Class 5", class_label="Class 5", grade_number=5, stage="Primary", age_group="10-11", category="primary")
        self.subject = Subject.objects.create(title="Mathematics", subtitle="Maths", olympiad_code="IMO", icon_type="math", color_theme={})
        self.cs = ClassSubject.objects.create(student_class=self.cls, subject=self.subject)
        self.chapter = Chapter.objects.create(class_subject=self.cs, name="Large Numbers", slug="large-numbers", order=1)
        self.concept = Concept.objects.create(chapter=self.chapter, name="Reading and Writing Large Numbers", slug="reading-and-writing-numbers", order=1)

        self.user = User.objects.create_user(username="mathstar", password="password123")
        self.profile = StudentProfile.objects.create(user=self.user, student_class=self.cls, xp=100, coins=25)

        self.game = Game.objects.create(
            concept=self.concept,
            title="Number Builder",
            slug="number-builder",
            game_path="class_5/mathematics/chapter_01_large_numbers/topic_01_reading_writing_numbers/number_builder",
            game_type="number_builder",
            difficulty="easy",
            xp_reward=50,
            coin_reward=15,
            is_active=True
        )

        from progress.models import StudentTopicProgress
        StudentTopicProgress.objects.create(
            student=self.profile,
            concept=self.concept,
            is_unlocked=True,
            learn_completed=True,
            game_unlocked=True
        )

    def test_game_path_field_and_hierarchical_url(self):
        """Verify game_path and clean hierarchical URL generation."""
        self.assertEqual(self.game.game_path, "class_5/mathematics/chapter_01_large_numbers/topic_01_reading_writing_numbers/number_builder")
        expected_url = "/class/5/mathematics/chapter/1/topic/1/game/number-builder/"
        self.assertEqual(self.game.get_hierarchical_url(), expected_url)

    def test_modular_game_runner_view_hierarchical_url(self):
        """Test hierarchical URL routing loads game correctly."""
        self.client.force_login(self.user)
        url = "/class/5/mathematics/chapter/1/topic/1/game/number-builder/"
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Number Builder")
        self.assertContains(res, "tezmindz-game-sdk.js")
        self.assertContains(res, "INDIAN PLACE VALUE TRAIN")

    def test_modular_game_runner_view_by_slug_and_id(self):
        """Test fallback slug and ID URLs load game correctly."""
        self.client.force_login(self.user)
        res_slug = self.client.get("/game/number-builder/play/")
        self.assertEqual(res_slug.status_code, 200)
        self.assertContains(res_slug, "Number Builder")

        res_id = self.client.get(f"/game/{self.game.id}/play/")
        self.assertEqual(res_id.status_code, 200)
        self.assertContains(res_id, "Number Builder")


