import uuid

from django.db import models


class TimeStampedModel(models.Model):
    """
    Adds created_at / updated_at to any model that inherits it.
    Applied to almost everything — cheap, and every model ends up
    needing "when was this created/changed" sooner or later.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDPublicIDMixin(models.Model):
    """
    Gives a model a public-facing UUID identifier, separate from its
    internal integer primary key.

    Use this ONLY on models that are addressed directly in a URL
    (Game, GameSession, Quiz, QuizAttempt, ...). Internal FK targets
    (Grade, Subject, Topic, Option, ...) keep plain integer PKs —
    they're faster to join on and are never exposed as "guess the ID"
    surface area, so a UUID buys nothing there.
    """

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)

    class Meta:
        abstract = True


class ContentStatus(models.TextChoices):
    """
    Shared content lifecycle: DRAFT -> UNDER_REVIEW -> APPROVED -> PUBLISHED.
    Only PUBLISHED content should ever reach a student-facing endpoint —
    that filtering is the responsibility of each app's queryset manager,
    not something we trust the caller to remember to add.
    """

    DRAFT = "draft", "Draft"
    UNDER_REVIEW = "under_review", "Under review"
    APPROVED = "approved", "Approved"
    PUBLISHED = "published", "Published"


class PublishableModel(models.Model):
    """
    Mixed into any content model that goes through a review/publish
    workflow: Topic, Concept, Game, Quiz, Question.
    """

    status = models.CharField(max_length=20, choices=ContentStatus.choices, default=ContentStatus.DRAFT)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def is_published(self):
        return self.status == ContentStatus.PUBLISHED


class PublishedManager(models.Manager):
    """
    Drop-in manager for PublishableModel subclasses: Model.published.all()
    returns only PUBLISHED rows. Student-facing views should query through
    this manager; mentor/admin views use the default `objects` manager to
    see everything regardless of status.
    """

    def get_queryset(self):
        return super().get_queryset().filter(status=ContentStatus.PUBLISHED)
