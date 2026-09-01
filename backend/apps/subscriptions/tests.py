from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.accounts.models import StudentProfile, User
from apps.curriculum.models import Grade, Subject, Topic
from apps.games.models import Game
from apps.subscriptions.models import TrialGameLog


class TrialGameLogTests(TestCase):
    """
    CONFIRMED requirement: the free trial covers 3 DISTINCT games.
    Replaying a game already logged must not consume another slot.
    This constraint is what a Phase-10 entitlement check will rely on:
    "insert; if it already exists, this was a replay, not a new game."
    """

    def setUp(self):
        grade = Grade.objects.create(name="Grade 4", order=4)
        subject = Subject.objects.create(name="Mathematics", slug="mathematics")
        topic = Topic.objects.create(subject=subject, grade=grade, title="Fractions")
        self.game = Game.objects.create(topic=topic, title="Pizza Fraction Challenge", access_tier="trial")
        user = User.objects.create_user(username="aarav", email="aarav@example.com", password="testpass123")
        self.student = StudentProfile.objects.create(user=user, display_name="Aarav", grade=grade)

    def test_replaying_the_same_game_does_not_create_a_second_trial_slot(self):
        TrialGameLog.objects.create(student=self.student, game=self.game)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                TrialGameLog.objects.create(student=self.student, game=self.game)

        self.assertEqual(TrialGameLog.objects.filter(student=self.student).count(), 1)
