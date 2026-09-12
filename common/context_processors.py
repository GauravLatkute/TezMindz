"""
Context processors for TezMindz platform.
Injects student profile and authentication data across all templates.
"""
from accounts.models import StudentProfile


def user_context(request):
    """
    Ensures 'profile' and 'student_class' are always accessible in templates
    whenever a user is authenticated.
    """
    if request.user.is_authenticated:
        # Guarantee demo account 'student' is never granted staff/admin status
        if request.user.username == "student" and (request.user.is_staff or request.user.is_superuser):
            request.user.is_staff = False
            request.user.is_superuser = False
            request.user.save(update_fields=["is_staff", "is_superuser"])

        try:
            profile = request.user.profile
        except Exception:
            try:
                profile = StudentProfile.objects.filter(user=request.user).first()
            except Exception:
                profile = None
        return {
            "profile": profile,
            "student_profile": profile,
        }
    return {
        "profile": None,
        "student_profile": None,
    }
