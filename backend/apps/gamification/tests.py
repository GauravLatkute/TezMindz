from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.accounts.models import StudentProfile, User
from apps.curriculum.models import Grade
from apps.gamification.models import CreditAccount, CreditTransaction


class CreditLedgerIdempotencyTests(TestCase):
    """
    Model-level proof of the design decision in Phase 2/3: a
    CreditTransaction with a reference that's already been used for
    this account must be rejected by the database, not just by
    application logic that a future developer might forget to add.

    This is what a real "duplicate game-completion request" collapses
    to at the model layer — the view-level idempotency behavior
    (Phase 6) is built ON TOP of this constraint, not instead of it.
    """

    def setUp(self):
        grade = Grade.objects.create(name="Grade 4", order=4)
        user = User.objects.create_user(username="aarav", email="aarav@example.com", password="testpass123")
        self.student = StudentProfile.objects.create(user=user, display_name="Aarav", grade=grade)
        self.account = CreditAccount.objects.create(student=self.student, balance=0)

    def test_same_reference_cannot_be_rewarded_twice(self):
        CreditTransaction.objects.create(
            account=self.account, amount=20, transaction_type="earn", reference="session-abc123"
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                CreditTransaction.objects.create(
                    account=self.account, amount=20, transaction_type="earn", reference="session-abc123"
                )

    def test_blank_reference_does_not_trigger_uniqueness(self):
        # Manual admin adjustments etc. legitimately have no reference —
        # the constraint must not accidentally block more than one of those.
        CreditTransaction.objects.create(account=self.account, amount=5, transaction_type="admin_adjustment")
        CreditTransaction.objects.create(account=self.account, amount=-5, transaction_type="admin_adjustment")
        self.assertEqual(self.account.transactions.count(), 2)
