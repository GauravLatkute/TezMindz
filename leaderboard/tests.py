from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from academics.models import Class
from accounts.models import StudentProfile
from rewards.models import XPTransaction

class LeaderboardAPITests(APITestCase):
    def setUp(self):
        self.class_obj = Class.objects.create(
            grade_number=5,
            name="Grade 5",
            class_label="Class 5",
            stage="Olympiad Challenger",
            age_group="Age 10-11",
            category="middle"
        )
        
        # User 1 (Me)
        self.user_me = User.objects.create_user(username="me", email="me@example.com", password="password")
        self.profile_me = StudentProfile.objects.create(user=self.user_me, student_class=self.class_obj, xp=100)
        
        # User 2 (Competitor)
        self.user_other = User.objects.create_user(username="competitor", email="comp@example.com", password="password")
        self.profile_other = StudentProfile.objects.create(user=self.user_other, student_class=self.class_obj, xp=200)
        
        # Seed XP transactions
        XPTransaction.objects.create(student=self.profile_me, points=100, reason="Quest")
        XPTransaction.objects.create(student=self.profile_other, points=200, reason="Quest")

        self.client.force_authenticate(user=self.user_me)

    def test_weekly_leaderboard(self):
        url = reverse("leaderboard:weekly")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        # Check sorting order: competitor (200 XP) should be rank 1, me (100 XP) rank 2
        self.assertEqual(response.data["data"][0]["username" if "username" in response.data["data"][0] else "display_name"], "competitor")
        self.assertEqual(response.data["data"][0]["rank"], 1)

    def test_my_leaderboard_rank(self):
        url = reverse("leaderboard:me")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["overall_rank"], 2)
        self.assertEqual(response.data["data"]["weekly_rank"], 2)
