from django.db import models

from common.models import PublishableModel, PublishedManager, TimeStampedModel, UUIDPublicIDMixin


class Question(PublishableModel, TimeStampedModel):
    """
    A reusable bank entry, not owned by a single quiz — the same
    question can appear in multiple quizzes via QuizQuestion. `concept`
    is nullable because some questions (general reasoning/GK) don't map
    to one specific concept.
    """

    class Difficulty(models.TextChoices):
        EASY = "easy", "Easy"
        MEDIUM = "medium", "Medium"
        HARD = "hard", "Hard"

    topic = models.ForeignKey("curriculum.Topic", on_delete=models.CASCADE, related_name="questions")
    concept = models.ForeignKey(
        "curriculum.Concept", on_delete=models.SET_NULL, null=True, blank=True, related_name="questions"
    )
    prompt = models.TextField()
    explanation = models.TextField(help_text="Shown to the student after an incorrect answer.")
    difficulty = models.CharField(max_length=10, choices=Difficulty.choices, default=Difficulty.EASY)
    allow_multiple_answers = models.BooleanField(default=False)
    marks = models.PositiveSmallIntegerField(default=1)
    negative_marks = models.PositiveSmallIntegerField(default=0)

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        indexes = [models.Index(fields=["topic", "status"])]

    def __str__(self):
        return self.prompt[:60]


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.text


class Hint(models.Model):
    """
    Scoped to Question only (not a generic relation to Question+Game) —
    a GenericForeignKey is easy to misuse for a small team; if games
    need hints later, add a nullable `game` FK here rather than going
    generic. A question can have more than one hint at increasing cost
    (progressive hints), ordered by `order`.
    """

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="hints")
    text = models.TextField()
    cost_credits = models.PositiveSmallIntegerField(default=5)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["question", "order"]

    def __str__(self):
        return f"Hint for: {self.question}"


class Quiz(PublishableModel, TimeStampedModel, UUIDPublicIDMixin):
    topic = models.ForeignKey("curriculum.Topic", on_delete=models.CASCADE, related_name="quizzes")
    title = models.CharField(max_length=150)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True, help_text="Null = untimed.")
    questions = models.ManyToManyField(Question, through="QuizQuestion", related_name="quizzes")

    objects = models.Manager()
    published = PublishedManager()

    def __str__(self):
        return self.title


class QuizQuestion(models.Model):
    """Through-table: controls per-quiz ordering of an otherwise reusable question."""

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(fields=["quiz", "question"], name="unique_question_per_quiz"),
        ]


class QuizAttempt(TimeStampedModel, UUIDPublicIDMixin):
    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "In progress"
        SUBMITTED = "submitted", "Submitted"

    student = models.ForeignKey("accounts.StudentProfile", on_delete=models.CASCADE, related_name="quiz_attempts")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_PROGRESS)
    score = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["student", "quiz"])]

    def __str__(self):
        return f"{self.student} · {self.quiz} · {self.status}"


class QuestionResponse(TimeStampedModel):
    """
    `is_correct` and `marks_awarded` are computed ONCE at submit time and
    stored here — never re-derived live from the current Option.is_correct.
    This is what protects historical attempts from being silently rewritten
    if a mentor edits a question's correct answer next month (requirement
    #45: content edits must not corrupt past results).
    """

    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name="responses")
    question = models.ForeignKey(Question, on_delete=models.PROTECT, related_name="responses")
    selected_options = models.ManyToManyField(Option, blank=True, related_name="selected_in_responses")
    is_correct = models.BooleanField(null=True, help_text="Null until answered.")
    marks_awarded = models.SmallIntegerField(default=0)
    answered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["attempt", "question"], name="unique_response_per_attempt_question"),
        ]

    def __str__(self):
        return f"{self.attempt} · {self.question}"
