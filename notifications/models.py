from django.db import models
from accounts.models import StudentProfile

class Notification(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    notification_type = models.CharField(
        max_length=50,
        choices=[
            ("BADGE_UNLOCKED", "Badge Unlocked"),
            ("ACHIEVEMENT_UNLOCKED", "Achievement Unlocked"),
            ("MISSION_COMPLETED", "Mission Completed"),
            ("PROGRESS_MILESTONE", "Progress Milestone"),
            ("STREAK_ALERT", "Streak Alert"),
            ("NEW_CHALLENGE", "New Challenge"),
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student.user.username} - {self.title} ({'Read' if self.is_read else 'Unread'})"
