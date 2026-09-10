from django.db import models
from django.contrib.auth.models import User
from academics.models import Concept


class AdminAuditLog(models.Model):
    """Immutable audit trail for all admin operations in TezMindz."""
    admin_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="audit_logs")
    action = models.CharField(max_length=100, help_text="e.g. 'Create Game', 'Upload ZIP', 'Modify Topic'")
    target_model = models.CharField(max_length=100)
    target_id = models.CharField(max_length=100, blank=True)
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        user_name = self.admin_user.username if self.admin_user else "System"
        return f"[{self.created_at.strftime('%Y-%m-%d %H:%M')}] {user_name} -> {self.action} ({self.target_model})"


class TopicUnlockRule(models.Model):
    """Configurable progression & unlock policies for each academic Topic."""
    concept = models.OneToOneField(Concept, on_delete=models.CASCADE, related_name="unlock_rule")
    learn_enabled = models.BooleanField(default=True)
    game_enabled = models.BooleanField(default=True)
    quiz_enabled = models.BooleanField(default=True)
    require_learn_for_game = models.BooleanField(default=True)
    require_game_for_quiz = models.BooleanField(default=True)
    unlock_next_topic_on_quiz = models.BooleanField(default=True)
    max_game_attempts = models.PositiveIntegerField(default=5)
    hints_allowed = models.PositiveIntegerField(default=3)
    custom_xp_bonus = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Unlock Rules for {self.concept.name}"

