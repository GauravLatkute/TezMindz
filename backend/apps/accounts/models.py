from django.contrib.auth.models import AbstractUser
from django.db import models

from common.models import TimeStampedModel


class User(AbstractUser):
    """
    Custom user from day one (required before the first migration —
    swapping AUTH_USER_MODEL later is painful/near-impossible once
    migrations exist, so we pay this cost up front even though the
    MVP only adds one extra field today).

    `role` is informational / for content-scoping convenience (e.g.
    "show mentors a content dashboard"). It is NOT the source of truth
    for admin access — Django's own is_staff/is_superuser control the
    Django Admin and are checked separately, per the requirement that
    students must never reach admin functionality through this field.
    """

    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        PARENT = "parent", "Parent"
        MENTOR = "mentor", "Mentor"
        ADMIN = "admin", "Admin"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    email = models.EmailField(unique=True)

    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return f"{self.username} ({self.role})"


class AccountStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    SUSPENDED = "suspended", "Suspended"


class StudentProfile(TimeStampedModel):
    """
    One per student User. Deliberately thin: no date_of_birth, no
    address, no phone number — grade already implies the age band,
    and we're minimizing personal data collected from children per
    the product's own privacy requirement. Add fields here only when
    a real feature needs them, not speculatively.
    """

    class Avatar(models.TextChoices):
        COMET = "comet", "Comet"
        FOX = "fox", "Fox"
        OWL = "owl", "Owl"
        ROBOT = "robot", "Robot"
        TURTLE = "turtle", "Turtle"

    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE, related_name="student_profile")
    display_name = models.CharField(max_length=50)
    # PROTECT, not CASCADE: deleting a Grade should never silently delete
    # every student in it. A real deletion has to be an explicit, separate
    # decision (reassign students first).
    grade = models.ForeignKey("curriculum.Grade", on_delete=models.PROTECT, related_name="students")
    avatar_key = models.CharField(max_length=20, choices=Avatar.choices, default=Avatar.COMET)
    parent = models.ForeignKey(
        "accounts.ParentProfile", on_delete=models.SET_NULL, null=True, blank=True, related_name="children"
    )
    account_status = models.CharField(max_length=20, choices=AccountStatus.choices, default=AccountStatus.ACTIVE)

    def __str__(self):
        return self.display_name


class ParentProfile(TimeStampedModel):
    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE, related_name="parent_profile")

    def __str__(self):
        return f"Parent: {self.user.username}"


class MentorProfile(TimeStampedModel):
    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE, related_name="mentor_profile")
    # Scopes which subjects a mentor is allowed to create/edit content for.
    # Enforced in permissions in a later phase — the field just needs to
    # exist now so that check has something to read.
    assigned_subjects = models.ManyToManyField("curriculum.Subject", blank=True, related_name="mentors")

    def __str__(self):
        return f"Mentor: {self.user.username}"
