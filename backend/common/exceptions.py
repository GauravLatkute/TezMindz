"""
Custom exception handler wired in via REST_FRAMEWORK["EXCEPTION_HANDLER"].

Per the Phase 2 decision: success responses stay as plain DRF serializer
output (no forced wrapper — it plays better with pagination and adds no
real value), but every ERROR response is normalized to:

    {"success": false, "error": {"code": "...", "message": "..."}}

`code` is a short machine-readable string (e.g. "INSUFFICIENT_CREDITS")
that the frontend can switch on without parsing prose. Application-level
exceptions (Phase 6+) should subclass ApplicationError below so they get
a stable code automatically instead of falling through to the generic
DRF default_code.
"""

from rest_framework.views import exception_handler as drf_exception_handler


class ApplicationError(Exception):
    """
    Base class for domain-specific errors raised by service-layer code,
    e.g. InsufficientCreditsError, GameAlreadyCompletedError,
    SubscriptionRequiredError. Each subclass sets `code`, `message`,
    and `status_code`; views don't need their own try/except per error
    type because the handler below catches ApplicationError generically.
    """

    code = "APPLICATION_ERROR"
    message = "Something went wrong."
    status_code = 400


def tezmindz_exception_handler(exc, context):
    from rest_framework import status
    from rest_framework.response import Response

    if isinstance(exc, ApplicationError):
        return Response(
            {"success": False, "error": {"code": exc.code, "message": exc.message}},
            status=exc.status_code,
        )

    response = drf_exception_handler(exc, context)
    if response is None:
        # Unexpected/unhandled exception — never leak internals to the client.
        return Response(
            {"success": False, "error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred."}},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Normalize DRF's own errors (validation, auth, permission, throttling, 404)
    # into the same shape instead of leaving DRF's default {"detail": "..."}.
    code = getattr(exc, "default_code", "error")
    if isinstance(response.data, dict) and "detail" in response.data:
        message = str(response.data["detail"])
    else:
        message = str(response.data)

    response.data = {"success": False, "error": {"code": str(code).upper(), "message": message}}
    return response
