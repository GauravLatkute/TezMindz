from django.db import models
from django.utils.text import slugify


class Class(models.Model):
    grade_number = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=50)           # e.g., "Grade 5"
    class_label = models.CharField(max_length=50)    # e.g., "Class 5"
    slug = models.SlugField(unique=True, blank=True)  # e.g., "class-5"
    stage = models.CharField(max_length=100)          # e.g., "Olympiad Challenger"
    age_group = models.CharField(max_length=50)       # e.g., "Age 10 - 11"
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=20,
        choices=[
            ("primary", "Primary"),
            ("middle", "Middle"),
            ("senior", "Senior"),
        ]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        verbose_name_plural = "Classes"
        ordering = ["grade_number"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.class_label) or f"class-{self.grade_number}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.class_label


class Subject(models.Model):
    title = models.CharField(max_length=100, unique=True)
    subtitle = models.CharField(max_length=255)
    olympiad_code = models.CharField(max_length=100)
    icon_type = models.CharField(
        max_length=50,
        choices=[
            ("math", "math"),
            ("science", "science"),
            ("english", "english"),
        ]
    )
    # Holds Tailwind color details: bg, border, badgeBg, accentText, buttonBg
    color_theme = models.JSONField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class ClassSubject(models.Model):
    """Junction: a Subject as it exists for a specific Class."""
    student_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="class_subjects")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="class_subjects")
    total_modules = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("student_class", "subject")

    def __str__(self):
        return f"{self.student_class.class_label} — {self.subject.title}"


class Chapter(models.Model):
    class_subject = models.ForeignKey(ClassSubject, on_delete=models.CASCADE, related_name="chapters")
    name = models.CharField(max_length=255)
    slug = models.SlugField(blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        unique_together = ("class_subject", "order")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.class_subject.student_class.class_label} "
            f"| {self.class_subject.subject.title} "
            f"| Ch {self.order}: {self.name}"
        )


class Concept(models.Model):
    """A Topic / Concept within a Chapter."""
    DIFFICULTY_CHOICES = [
        ("easy", "Easy"),
        ("medium", "Medium"),
        ("hard", "Hard"),
    ]

    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name="concepts")
    name = models.CharField(max_length=255)
    slug = models.SlugField(blank=True)
    description = models.TextField()
    real_world_example = models.TextField(blank=True, null=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default="medium")
    estimated_time = models.PositiveIntegerField(default=15, help_text="Estimated time in minutes")
    order = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        unique_together = ("chapter", "order")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.chapter.name} — Concept {self.order}: {self.name}"


# ── QUIZ SYSTEM ──────────────────────────────────────────────────────────────

class Quiz(models.Model):
    """A standalone academic quiz linked to a Concept/Topic."""
    DIFFICULTY_CHOICES = [
        ("easy", "Easy"),
        ("medium", "Medium"),
        ("hard", "Hard"),
    ]

    concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name="quizzes")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default="medium")
    time_limit = models.PositiveIntegerField(default=10, help_text="Time limit in minutes")
    passing_percentage = models.PositiveIntegerField(default=60)
    xp_reward = models.PositiveIntegerField(default=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.concept.name})"


class QuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()
    explanation = models.TextField(blank=True, help_text="Shown after answering")
    marks = models.PositiveIntegerField(default=1)
    display_order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["display_order"]

    def __str__(self):
        return f"Q{self.display_order}: {self.question_text[:60]}"


class QuizOption(models.Model):
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name="options")
    option_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        mark = "✓" if self.is_correct else "✗"
        return f"{mark} {self.option_text[:50]}"


# ── DAILY CHALLENGE ──────────────────────────────────────────────────────────

class DailyChallenge(models.Model):
    """A class-specific daily challenge (one per class per day)."""
    DIFFICULTY_CHOICES = [
        ("easy", "Easy"),
        ("medium", "Medium"),
        ("hard", "Hard"),
    ]

    student_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="daily_challenges")
    title = models.CharField(max_length=255)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default="medium")
    xp_reward = models.PositiveIntegerField(default=50)
    coin_reward = models.PositiveIntegerField(default=25)
    date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student_class", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.student_class.class_label} | {self.date} — {self.title}"
