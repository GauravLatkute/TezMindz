from django.db import models
from accounts.models import StudentProfile


class XPTransaction(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="xp_transactions")
    points = models.IntegerField()   # Can be positive or negative
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.user.username} — {self.points:+d} XP ({self.reason})"


class CoinTransaction(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="coin_transactions")
    coins = models.IntegerField()   # Can be positive or negative
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.user.username} — {self.coins:+d} Coins ({self.reason})"


class Badge(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, default="🏆")
    criteria = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class StudentBadge(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="unlocked_badges")
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name="earned_by")
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "badge")

    def __str__(self):
        return f"{self.student.user.username} — {self.badge.name}"


class DailyMission(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    target_type = models.CharField(
        max_length=50,
        choices=[
            ("games_count", "Games Count"),
            ("concepts_count", "Concepts Count"),
            ("questions_solved", "Questions Solved"),
            ("xp_earned", "XP Earned"),
            ("streak_days", "Streak Days"),
            ("lessons_completed", "Lessons Completed"),
            ("quizzes_passed", "Quizzes Passed"),
        ]
    )
    target_value = models.PositiveIntegerField()
    xp_reward = models.PositiveIntegerField(default=30)
    coin_reward = models.PositiveIntegerField(default=15)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class StudentMission(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="missions")
    mission = models.ForeignKey(DailyMission, on_delete=models.CASCADE, related_name="student_missions")
    progress = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    assigned_date = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "mission", "assigned_date")

    def __str__(self):
        return f"{self.student.user.username} — {self.mission.title} ({self.progress}/{self.mission.target_value})"


# ── ACHIEVEMENT SYSTEM ───────────────────────────────────────────────────────

class Achievement(models.Model):
    CONDITION_TYPES = [
        ("xp_total", "Total XP Earned"),
        ("streak_days", "Streak Days"),
        ("quizzes_passed", "Quizzes Passed"),
        ("games_completed", "Games Completed"),
        ("lessons_completed", "Lessons Completed"),
        ("perfect_quiz", "Perfect Quiz Score"),
        ("first_game", "First Game Played"),
        ("first_lesson", "First Lesson Completed"),
        ("first_quiz", "First Quiz Passed"),
    ]

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, default="🏆")
    xp_reward = models.PositiveIntegerField(default=50)
    coin_reward = models.PositiveIntegerField(default=25)
    condition_type = models.CharField(max_length=50, choices=CONDITION_TYPES)
    condition_value = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["condition_type", "condition_value"]

    def __str__(self):
        return f"{self.icon} {self.name}"


class StudentAchievement(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="achievements")
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name="earned_by")
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "achievement")
        verbose_name_plural = "Student Achievements"

    def __str__(self):
        return f"{self.student.user.username} — {self.achievement.name}"
