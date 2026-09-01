from django.db import models


class Plan(models.Model):
    """
    CONFIRMED: three plans exist. Names/prices below are placeholder —
    TODO / NEEDS MENTOR+BUSINESS CONFIRMATION before this is real data,
    per rule 50 (not inventing finalized pricing). `features` is JSON
    because plan-to-feature mapping is genuinely business-configurable
    and not something that should require a migration to change.
    """

    class BillingPeriod(models.TextChoices):
        MONTHLY = "monthly", "Monthly"
        YEARLY = "yearly", "Yearly"

    code = models.SlugField(max_length=40, unique=True)
    name = models.CharField(max_length=80)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    billing_period = models.CharField(max_length=10, choices=BillingPeriod.choices, default=BillingPeriod.MONTHLY)
    features = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"

    student = models.ForeignKey("accounts.StudentProfile", on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="subscriptions")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    start_date = models.DateField()
    end_date = models.DateField()
    auto_renew = models.BooleanField(default=True)

    class Meta:
        indexes = [models.Index(fields=["student", "status"])]

    def __str__(self):
        return f"{self.student} · {self.plan} · {self.status}"


class TrialGameLog(models.Model):
    """
    CONFIRMED: free trial = 3 DISTINCT games. Replaying a game the
    student already logged here must NOT consume another trial slot.
    The unique_together constraint is what enforces "distinct" at the
    database level — the entitlement check (Phase 10 service layer) is
    just: has this (student, game) row already? If yes, always allow
    (it's a replay). If no, allow only while COUNT(student's rows) < 3,
    then insert this row.
    """

    student = models.ForeignKey("accounts.StudentProfile", on_delete=models.CASCADE, related_name="trial_games")
    game = models.ForeignKey("games.Game", on_delete=models.CASCADE, related_name="trial_logs")
    first_played_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["student", "game"], name="unique_trial_game_per_student"),
        ]

    def __str__(self):
        return f"{self.student} tried {self.game}"


class Payment(models.Model):
    """
    Provider-agnostic record. All provider-specific logic (Razorpay,
    Stripe, whichever is chosen — TODO, not decided) lives behind
    `subscriptions/services/payments.py` in a later phase; this model
    only stores the outcome, never talks to a provider API itself.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    student = models.ForeignKey("accounts.StudentProfile", on_delete=models.CASCADE, related_name="payments")
    subscription = models.ForeignKey(
        Subscription, on_delete=models.SET_NULL, null=True, blank=True, related_name="payments"
    )
    provider = models.CharField(max_length=40, help_text="e.g. 'razorpay', 'stripe' — TODO: not yet decided.")
    provider_reference = models.CharField(max_length=150, unique=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=10, default="INR")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    raw_payload = models.JSONField(null=True, blank=True, help_text="Raw provider webhook payload, for audit.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} · {self.amount} {self.currency} · {self.status}"
