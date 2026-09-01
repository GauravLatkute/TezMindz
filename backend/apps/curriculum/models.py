from django.db import models
from django.utils import timezone

from common.models import ContentStatus, PublishableModel, PublishedManager, TimeStampedModel


class Grade(TimeStampedModel):
    """E.g. "Grade 4". Plain integer PK — referenced constantly, never
    exposed as a standalone URL resource on its own."""

    name = models.CharField(max_length=50, unique=True)
    order = models.PositiveSmallIntegerField(unique=True, help_text="Display order, e.g. Grade 1 = 1.")

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name


class Subject(TimeStampedModel):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Topic(PublishableModel, TimeStampedModel):
    """
    Grade x Subject scoped content unit. `prerequisites` is self-referential
    so curriculum sequencing/unlocking (Phase 9) has something to walk
    without needing a separate graph structure.
    """

    class Difficulty(models.TextChoices):
        EASY = "easy", "Easy"
        MEDIUM = "medium", "Medium"
        HARD = "hard", "Hard"

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="topics")
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name="topics")
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    difficulty = models.CharField(max_length=10, choices=Difficulty.choices, default=Difficulty.EASY)
    learning_objectives = models.TextField(
        blank=True, help_text="Plain-text list of what a student should know after this topic."
    )
    prerequisites = models.ManyToManyField("self", symmetrical=False, blank=True, related_name="unlocks")
    estimated_minutes = models.PositiveSmallIntegerField(default=10)
    order = models.PositiveSmallIntegerField(default=0)

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ["grade__order", "subject__order", "order"]
        indexes = [
            models.Index(fields=["grade", "subject", "status"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["subject", "grade", "title"], name="unique_topic_per_subject_grade"),
        ]

    def __str__(self):
        return f"{self.grade} · {self.subject} · {self.title}"

    def publish(self):
        """Explicit action, not a side effect of a generic save() —
        matches the requirement that publishing is an auditable event,
        not something that happens implicitly."""
        self.status = ContentStatus.PUBLISHED
        self.published_at = timezone.now()
        self.save(update_fields=["status", "published_at", "updated_at"])


class Concept(PublishableModel, TimeStampedModel):
    """The actual 'Learn' step content shown before a game/quiz."""

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="concepts")
    title = models.CharField(max_length=150)
    content_body = models.TextField(help_text="Markdown or plain text explanation shown to the student.")
    order = models.PositiveSmallIntegerField(default=0)

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ["topic", "order"]

    def __str__(self):
        return f"{self.topic} · {self.title}"
