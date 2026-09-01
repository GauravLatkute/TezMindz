from django.db import models


class CreditAccount(models.Model):
    """
    One per student. `balance` is a cached/denormalized total —
    CreditTransaction rows are the source of truth; balance exists so
    "can this student afford this hint" is a single indexed read, not
    a SUM() aggregate on every request. Every write to balance MUST
    happen inside the same transaction.atomic() block that creates the
    matching CreditTransaction row (enforced in service-layer code in
    a later phase, not here in the model).
    """

    student = models.OneToOneField("accounts.StudentProfile", on_delete=models.CASCADE, related_name="credit_account")
    balance = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.student} · {self.balance} credits"


class CreditTransaction(models.Model):
    """
    Full ledger, never just an in-place balance mutation. `reference`
    is what makes reward-granting idempotent: e.g. a game session's
    public_id is passed as the reference when awarding coins for
    completing it, and the unique constraint below means a retried
    "complete session" request cannot create a second EARN row for the
    same reference — the DB rejects it, not application logic.
    """

    class TransactionType(models.TextChoices):
        EARN = "earn", "Earn"
        SPEND = "spend", "Spend"
        BONUS = "bonus", "Bonus"
        REFUND = "refund", "Refund"
        ADMIN_ADJUSTMENT = "admin_adjustment", "Admin adjustment"

    account = models.ForeignKey(CreditAccount, on_delete=models.CASCADE, related_name="transactions")
    amount = models.IntegerField(help_text="Positive for earn/bonus/refund, negative for spend.")
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)
    reference = models.CharField(
        max_length=150, blank=True, default="", help_text="e.g. a GameSession or Hint-request public_id."
    )
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["account", "created_at"])]
        constraints = [
            models.UniqueConstraint(
                fields=["account", "reference"],
                condition=~models.Q(reference=""),
                name="unique_credit_reference_per_account",
            )
        ]

    def __str__(self):
        return f"{self.account} · {self.transaction_type} · {self.amount}"


class XPAccount(models.Model):
    student = models.OneToOneField("accounts.StudentProfile", on_delete=models.CASCADE, related_name="xp_account")
    total_xp = models.PositiveIntegerField(default=0)
    current_level = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f"{self.student} · Level {self.current_level} · {self.total_xp} XP"


class XPLevelThreshold(models.Model):
    """
    Admin-editable leveling curve — level N requires xp_required total XP.
    Kept as data, not a hardcoded formula, so the curve can be tuned
    without a deploy (per Phase-2 recommendation).
    """

    level = models.PositiveSmallIntegerField(unique=True)
    xp_required = models.PositiveIntegerField()

    class Meta:
        ordering = ["level"]

    def __str__(self):
        return f"Level {self.level} at {self.xp_required} XP"


class XPTransaction(models.Model):
    class Source(models.TextChoices):
        GAME = "game", "Game"
        QUIZ = "quiz", "Quiz"
        DAILY_CHALLENGE = "daily_challenge", "Daily challenge"
        MILESTONE = "milestone", "Milestone"
        ADMIN_ADJUSTMENT = "admin_adjustment", "Admin adjustment"

    account = models.ForeignKey(XPAccount, on_delete=models.CASCADE, related_name="transactions")
    amount = models.PositiveIntegerField()
    source = models.CharField(max_length=20, choices=Source.choices)
    reference = models.CharField(max_length=150, blank=True, default="")
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["account", "created_at"])]
        constraints = [
            models.UniqueConstraint(
                fields=["account", "reference"],
                condition=~models.Q(reference=""),
                name="unique_xp_reference_per_account",
            )
        ]

    def __str__(self):
        return f"{self.account} · +{self.amount} XP ({self.source})"


class Badge(models.Model):
    """
    `criteria` is a small structured JSON dispatched to a registry of
    Python evaluator functions keyed by `criteria["type"]` (built in the
    gamification service layer, Phase 8) — e.g.
    {"type": "quiz_perfect_score", "count": 1}
    {"type": "topic_games_completed", "topic_slug": "fractions", "count": 5}
    New badges that reuse an existing criteria type need zero code
    changes, just a new admin row. A genuinely new criteria type needs
    one new evaluator function.
    """

    code = models.SlugField(max_length=60, unique=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True)
    icon_key = models.CharField(max_length=50, blank=True, help_text="Frontend icon/asset identifier.")
    criteria = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class StudentBadge(models.Model):
    student = models.ForeignKey("accounts.StudentProfile", on_delete=models.CASCADE, related_name="badges")
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name="awarded_to")
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["student", "badge"], name="unique_badge_per_student"),
        ]

    def __str__(self):
        return f"{self.student} earned {self.badge}"
