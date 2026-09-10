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
