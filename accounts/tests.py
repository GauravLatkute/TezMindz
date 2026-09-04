from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from academics.models import Class
from accounts.models import StudentProfile

class AuthenticationTests(APITestCase):
    def setUp(self):
        # Create a test class
        self.class_obj = Class.objects.create(
            grade_number=5,
            name="Grade 5",
            class_label="Class 5",
            stage="Olympiad Challenger",
            age_group="Age 10-11",
            category="middle"
        )
        
        # Registration payload
        self.register_url = reverse("accounts:register")
        self.login_url = reverse("accounts:login")
        self.me_url = reverse("accounts:me")
        self.refresh_url = reverse("accounts:token_refresh")
        
        self.user_data = {
            "username": "teststudent",
            "email": "student@example.com",
            "password": "securepassword123",
            "class_id": self.class_obj.id,
            "avatar": "🚀"
        }

    def test_registration_success(self):
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertIn("tokens", response.data["data"])
        self.assertIn("access", response.data["data"]["tokens"])
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(StudentProfile.objects.count(), 1)
        self.assertEqual(StudentProfile.objects.first().avatar, "🚀")

    def test_registration_missing_fields(self):
        invalid_data = self.user_data.copy()
        del invalid_data["username"]
        response = self.client.post(self.register_url, invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_registration_duplicate_email(self):
        # Register once
        self.client.post(self.register_url, self.user_data, format="json")
        # Try registering again with same email but diff username
        duplicate_data = self.user_data.copy()
        duplicate_data["username"] = "diffusername"
        response = self.client.post(self.register_url, duplicate_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data["errors"])

    def test_login_success(self):
        # Register user first
        self.client.post(self.register_url, self.user_data, format="json")
        
        login_data = {
            "username": "teststudent",
            "password": "securepassword123"
        }
        response = self.client.post(self.login_url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("access", response.data["data"])
        self.assertEqual(response.data["data"]["user"]["username"], "teststudent")

    def test_login_invalid_credentials(self):
        login_data = {
            "username": "teststudent",
            "password": "wrongpassword"
        }
        response = self.client.post(self.login_url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data["success"])

    def test_access_profile_authenticated(self):
        # Register to set up user
        reg_response = self.client.post(self.register_url, self.user_data, format="json")
        access_token = reg_response.data["data"]["tokens"]["access"]
        
        # Access profile with token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["username"], "teststudent")

    def test_access_profile_unauthenticated(self):
        response = self.client.get(self.me_url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_token_refresh(self):
        reg_response = self.client.post(self.register_url, self.user_data, format="json")
        refresh_token = reg_response.data["data"]["tokens"]["refresh"]
        
        response = self.client.post(self.refresh_url, {"refresh": refresh_token}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("access", response.data["data"])
