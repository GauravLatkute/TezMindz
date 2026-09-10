from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from academics.models import Concept
from accounts.models import StudentProfile


class GameTemplate(models.Model):
    name = models.CharField(max_length=100)  # e.g., "Dream House Builder", "Multiple Choice Question"
    slug = models.SlugField(unique=True)     # e.g., "house_builder", "number_builder"
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Game(models.Model):
    """Core Game Definition in the Tezz-Mindz Game Engine."""
    DIFFICULTY_CHOICES = [
        ("easy", "Easy"),
        ("medium", "Medium"),
        ("hard", "Hard"),
    ]

    concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name="games")
    template = models.ForeignKey(GameTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name="games")
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255, blank=True, null=True)
    game_path = models.CharField(
        max_length=500,
        blank=True,
        default="",
        help_text="Path within games/ folder, e.g. class_5/mathematics/chapter_01_large_numbers/topic_01_reading_writing_numbers/number_builder"
    )
    game_type = models.CharField(max_length=50, default="house_builder", help_text="Engine identifier: house_builder, shopping, fractions, etc.")
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default="medium")
    thumbnail = models.CharField(max_length=255, blank=True, null=True)
    estimated_time = models.PositiveIntegerField(default=15, help_text="Estimated play time in minutes")
    xp_reward = models.PositiveIntegerField(default=50)
    coin_reward = models.PositiveIntegerField(default=15)
    config = models.JSONField(default=dict, blank=True)  # General game config
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_hierarchical_url(self):
        """Returns clean educational URL: /class/<grade>/<subject>/chapter/<ch>/topic/<top>/game/<slug>/"""
        try:
            concept = self.concept
            chapter = concept.chapter
            cs = chapter.class_subject
            grade = cs.student_class.grade_number
            subject_slug = slugify(cs.subject.title)
            return f"/class/{grade}/{subject_slug}/chapter/{chapter.order}/topic/{concept.order}/game/{self.slug}/"
        except Exception:
            return f"/game/{self.id}/play/"

    def __str__(self):
        return f"{self.title} ({self.game_type})"


class GameLevel(models.Model):
    """Distinct Level within a game (e.g. Level 1 to Level 5)."""
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="levels")
    level_number = models.PositiveIntegerField(default=1)
    title = models.CharField(max_length=255, default="Level 1")  # e.g., "Buy the Land"
    instructions = models.TextField(blank=True)
    difficulty = models.CharField(max_length=20, default="easy")
    time_limit = models.PositiveIntegerField(default=60, help_text="Time limit in seconds")
    points = models.PositiveIntegerField(default=100)
    xp_reward = models.PositiveIntegerField(default=10)
    coin_reward = models.PositiveIntegerField(default=3)
    configuration = models.JSONField(default=dict, blank=True)
    is_locked = models.BooleanField(default=False)
    unlock_requirement = models.CharField(max_length=255, blank=True, default="Complete previous level")

    class Meta:
        ordering = ["level_number"]

    def __str__(self):
        return f"{self.game.title} - Level {self.level_number}: {self.title}"


class GameContent(models.Model):
    """Dynamic Content / Questions for Game Levels (loaded from database)."""
    CONTENT_TYPE_CHOICES = [
        ("read_number", "Read Number"),
        ("build_number", "Build Number"),
        ("place_value", "Place Value"),
        ("compare_order", "Compare & Order"),
        ("budget_verification", "Budget Verification"),
        ("mcq", "Multiple Choice"),
    ]

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="contents")
    level = models.ForeignKey(GameLevel, on_delete=models.CASCADE, related_name="contents", null=True, blank=True)
    content_type = models.CharField(max_length=50, choices=CONTENT_TYPE_CHOICES, default="read_number")
    question = models.TextField()
    data = models.JSONField(default=dict, blank=True)
    correct_answer = models.JSONField(default=dict, blank=True)
    hint = models.TextField(blank=True)
    explanation = models.TextField(blank=True)
    points = models.PositiveIntegerField(default=100)
    difficulty = models.CharField(max_length=20, default="easy")
    display_order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order"]

    def __str__(self):
        lvl_num = self.level.level_number if self.level else 0
        return f"Level {lvl_num} ({self.content_type}): {self.question[:50]}"


class GameHint(models.Model):
    """Reusable tiered hints for game content."""
    content = models.ForeignKey(GameContent, on_delete=models.CASCADE, related_name="hints", null=True, blank=True)
    level = models.ForeignKey(GameLevel, on_delete=models.CASCADE, related_name="hints", null=True, blank=True)
    order = models.PositiveIntegerField(default=1)  # Hint 1, 2, 3
    text = models.TextField()
    cost_points = models.PositiveIntegerField(default=10)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Hint {self.order}: {self.text[:40]}"


class GameReward(models.Model):
    """Reward rule definitions for game achievements and milestones."""
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="rewards")
    reward_type = models.CharField(max_length=50, default="game_complete")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    xp_reward = models.PositiveIntegerField(default=20)
    coin_reward = models.PositiveIntegerField(default=5)
    badge_icon = models.CharField(max_length=50, blank=True, default="🏆")

    def __str__(self):
        return f"{self.title} (+{self.xp_reward} XP, +{self.coin_reward} Coins)"


class GameSession(models.Model):
    """Live Game Session tracked per student."""
    STATUS_CHOICES = [
        ("STARTED", "Started"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
        ("ABANDONED", "Abandoned"),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="sessions")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="sessions")
    current_level = models.PositiveIntegerField(default=1)
    difficulty = models.CharField(max_length=20, default="medium")
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="STARTED")
    score = models.PositiveIntegerField(default=0)
    accuracy = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    time_spent = models.PositiveIntegerField(default=0)  # in seconds
    hints_used = models.PositiveIntegerField(default=0)
    xp_earned = models.PositiveIntegerField(default=0)
    coins_earned = models.PositiveIntegerField(default=0)
    session_data = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Session {self.id} - Student: {self.student.user.username} - Game: {self.game.title} ({self.status})"


class GameAttempt(models.Model):
    """Student level attempt submission within a game session."""
    session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name="game_attempts")
    level = models.ForeignKey(GameLevel, on_delete=models.CASCADE, null=True, blank=True)
    content = models.ForeignKey(GameContent, on_delete=models.CASCADE, null=True, blank=True)
    student_answer = models.JSONField(default=dict, blank=True)
    is_correct = models.BooleanField(default=False)
    time_taken = models.PositiveIntegerField(default=0)  # in seconds
    hints_used = models.PositiveIntegerField(default=0)
    points_earned = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attempt {self.id} - Session {self.session_id} - Correct: {self.is_correct}"


class GameProgress(models.Model):
    """Persistent student progress per game across levels."""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="game_progresses")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="student_progresses")
    current_level = models.PositiveIntegerField(default=1)
    highest_level = models.PositiveIntegerField(default=1)
    best_score = models.PositiveIntegerField(default=0)
    completion_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    is_completed = models.BooleanField(default=False)
    last_played_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "game")

    def __str__(self):
        return f"{self.student.user.username} - {self.game.title}: Level {self.current_level} ({self.completion_percentage}%)"


# ── Legacy models preserved for backward compatibility ──────────────────────────
class Question(models.Model):
    game_level = models.ForeignKey(GameLevel, on_delete=models.CASCADE, related_name="legacy_questions", null=True, blank=True)
    text = models.TextField()
    image_url = models.CharField(max_length=255, blank=True, null=True)
    explanation = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"QID {self.id}: {self.text[:50]}..."


class QuestionOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="legacy_options")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["order"]


class Hint(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="legacy_hints")
    text = models.TextField()
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["order"]


class Attempt(models.Model):
    session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name="legacy_attempts")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True)
    selected_option = models.ForeignKey(QuestionOption, on_delete=models.CASCADE, null=True, blank=True)
    is_correct = models.BooleanField(default=False)
    time_taken = models.PositiveIntegerField(default=0)
    hints_used = models.PositiveIntegerField(default=0)
    points_earned = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
