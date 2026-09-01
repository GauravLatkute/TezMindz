from django.db import models


class Event(models.Model):
    """
    Append-only. Deliberately NOT foreign-keyed into every other app's
    business logic path — writing an event should never be able to
    fail a game-completion or quiz-submission transaction. In views,
    this gets written in a best-effort try/except (or on a post-commit
    signal) so a logging hiccup never blocks the operation it's
    describing. `student` is nullable so anonymous/pre-auth events
    (e.g. signup funnel) are representable too.
    """

    class EventType(models.TextChoices):
        GAME_STARTED = "game_started", "Game started"
        GAME_COMPLETED = "game_completed", "Game completed"
        QUIZ_STARTED = "quiz_started", "Quiz started"
        QUIZ_COMPLETED = "quiz_completed", "Quiz completed"
        QUESTION_ANSWERED = "question_answered", "Question answered"
        HINT_USED = "hint_used", "Hint used"
        XP_EARNED = "xp_earned", "XP earned"
        COIN_EARNED = "coin_earned", "Coin earned"
        COIN_SPENT = "coin_spent", "Coin spent"
        BADGE_EARNED = "badge_earned", "Badge earned"
        TOPIC_COMPLETED = "topic_completed", "Topic completed"

    student = models.ForeignKey(
        "accounts.StudentProfile", on_delete=models.SET_NULL, null=True, blank=True, related_name="events"
    )
    event_type = models.CharField(max_length=30, choices=EventType.choices)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["event_type", "created_at"]),
            models.Index(fields=["student", "created_at"]),
        ]

    def __str__(self):
        return f"{self.event_type} · {self.created_at:%Y-%m-%d %H:%M}"
