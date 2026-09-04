from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from academics.models import Class
from accounts.models import StudentProfile
from rewards.models import XPTransaction, CoinTransaction, Badge, StudentBadge

class RewardsAPITests(APITestCase):
    def setUp(self):
        self.class_obj = Class.objects.create(
            grade_number=5,
            name="Grade 5",
            class_label="Class 5",
            stage="Olympiad Challenger",
            age_group="Age 10-11",
            category="middle"
        )
        
        self.user = User.objects.create_user(username="rewardsstudent", email="rew@example.com", password="password")
        self.profile = StudentProfile.objects.create(user=self.user, student_class=self.class_obj, xp=150, coins=70, streak=3)
        
        # Create XP & Coin transactions
        self.xp_tx = XPTransaction.objects.create(student=self.profile, points=50, reason="Game Complete")
        self.coin_tx = CoinTransaction.objects.create(student=self.profile, coins=20, reason="Game Complete")
        
        # Create Badges
        self.badge_math = Badge.objects.create(name="Math Explorer", description="Math Badge", icon="📐")
        self.badge_sci = Badge.objects.create(name="Science Wizard", description="Science Badge", icon="🧪")
        
        # Unlock one badge
        self.student_badge = StudentBadge.objects.create(student=self.profile, badge=self.badge_math)

        self.client.force_authenticate(user=self.user)

    def test_rewards_summary(self):
        url = reverse("rewards:summary")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["xp"], 150)
        self.assertEqual(response.data["data"]["badges_unlocked"], 1)

    def test_xp_ledger(self):
        url = reverse("rewards:xp")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["points"], 50)

    def test_coin_ledger(self):
        url = reverse("rewards:coins")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["coins"], 20)

    def test_badges_list(self):
        url = reverse("rewards:badges")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]["unlocked"]), 1)
        self.assertEqual(len(response.data["data"]["locked"]), 1)
        self.assertEqual(response.data["data"]["unlocked"][0]["badge"]["name"], "Math Explorer")
        self.assertEqual(response.data["data"]["locked"][0]["name"], "Science Wizard")

    def test_streak_details(self):
        url = reverse("rewards:streak")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["current_streak"], 3)

    def test_buy_course(self):
        url = reverse("rewards:buy_course")
        # Insufficient coins at first
        self.profile.coins = 50
        self.profile.save()
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

        # Sufficient coins
        self.profile.coins = 120
        self.profile.save()
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.coins, 20)
        self.assertTrue(self.profile.is_premium)
