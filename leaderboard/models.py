from django.db import models


class LeaderboardEntry(models.Model):
    """Cached leaderboard position per student per class (updated on XP change)."""
    student = models.ForeignKey(
        "accounts.StudentProfile",
        on_delete=models.CASCADE,
        related_name="leaderboard_entries"
    )
    student_class = models.ForeignKey(
        "academics.Class",
        on_delete=models.CASCADE,
        related_name="leaderboard_entries"
    )
    rank = models.PositiveIntegerField(default=0)
    xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    games_played = models.PositiveIntegerField(default=0)
    quizzes_passed = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "student_class")
        ordering = ["rank"]
        verbose_name_plural = "Leaderboard Entries"

    def __str__(self):
        return f"Rank {self.rank}: {self.student.user.username} ({self.student_class.class_label})"
