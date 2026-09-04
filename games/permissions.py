from rest_framework import permissions


class IsStudentOwner(permissions.BasePermission):
    """
    Ensures the student can only access and modify their own sessions, attempts, and progress.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated or not hasattr(request.user, "profile"):
            return False
        
        # Object can be GameSession, GameProgress, or GameAttempt
        if hasattr(obj, "student"):
            return obj.student == request.user.profile
        if hasattr(obj, "session"):
            return obj.session.student == request.user.profile
        return False
