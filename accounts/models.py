from django.db import models
from django.contrib.auth.models import User
from academics.models import Class

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    student_class = models.ForeignKey(Class, on_delete=models.PROTECT, related_name="students")
    avatar = models.CharField(max_length=255, default="🌟")
    dob = models.DateField(null=True, blank=True)
    xp = models.PositiveIntegerField(default=0)
    coins = models.PositiveIntegerField(default=0)
    current_level = models.PositiveIntegerField(default=1)
    streak = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    is_premium = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} (Class {self.student_class.grade_number})"
