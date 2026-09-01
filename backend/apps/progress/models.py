from django.db import models


class TopicProgress(models.Model):
    """
    The one row per (student, topic) that everything else aggregates
    from. Subject- and grade-level "performance" rollups (weak/strong
    subjects, §17) are computed on read by aggregating over these rows
    rather than stored as separate denormalized tables — at MVP content
    volume that aggregation is cheap, and it removes an entire class of
    "rollup went out of sync with the source rows" bugs. If this ever
    becomes a real query cost, the fix is a periodic snapshot table
    built by a management command, not a cache layer.
    """

    student = models.ForeignKey("accounts.StudentProfile", on_delete=models.CASCADE, related_name="topic_progress")
    topic = models.ForeignKey("curriculum.Topic", on_delete=models.CASCADE, related_name="student_progress")

    attempts = models.PositiveIntegerField(default=0)
    correct_count = models.PositiveIntegerField(default=0)
    incorrect_count = models.PositiveIntegerField(default=0)
    best_score = models.PositiveIntegerField(default=0)
    last_activity_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["student", "topic"], name="unique_progress_per_student_topic"),
        ]
        indexes = [models.Index(fields=["student", "last_activity_at"])]

    @property
    def accuracy(self):
        total = self.correct_count + self.incorrect_count
        return round(self.correct_count / total, 3) if total else None

    def __str__(self):
        return f"{self.student} · {self.topic}"
