from django.db.models import ProtectedError
from django.test import TestCase

from apps.accounts.models import StudentProfile, User
from apps.curriculum.models import Grade, Subject, Topic


class GradeProtectionTests(TestCase):
    """A Grade with students enrolled must never be silently cascade-deleted."""

    def test_grade_with_students_cannot_be_deleted(self):
        grade = Grade.objects.create(name="Grade 4", order=4)
        user = User.objects.create_user(username="aarav", email="aarav@example.com", password="testpass123")
        StudentProfile.objects.create(user=user, display_name="Aarav", grade=grade)

        with self.assertRaises(ProtectedError):
            grade.delete()


class TopicUniquenessTests(TestCase):
    def test_duplicate_topic_title_rejected_within_same_subject_and_grade(self):
        grade = Grade.objects.create(name="Grade 4", order=4)
        subject = Subject.objects.create(name="Mathematics", slug="mathematics")
        Topic.objects.create(subject=subject, grade=grade, title="Fractions")

        with self.assertRaises(Exception):
            Topic.objects.create(subject=subject, grade=grade, title="Fractions")
