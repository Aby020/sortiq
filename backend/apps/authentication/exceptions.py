"""Global DRF exception handler producing the Sortiq error envelope."""

from __future__ import annotations

import uuid

from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

ERROR_CODES = {
    exceptions.AuthenticationFailed: "auth_failed",
    exceptions.NotAuthenticated: "auth_required",
    exceptions.PermissionDenied: "permission_denied",
    exceptions.NotFound: "not_found",
    exceptions.MethodNotAllowed: "method_not_allowed",
    exceptions.NotAcceptable: "not_acceptable",
    exceptions.UnsupportedMediaType: "unsupported_media_type",
    exceptions.Throttled: "throttled",
    exceptions.ValidationError: "validation_error",
}


def _error_code(exc: Exception) -> str:
    if isinstance(exc, exceptions.APIException):
        return ERROR_CODES.get(exc.__class__, "api_error")
    return "internal"


def _error_details(exc: Exception) -> dict:
    if isinstance(exc, exceptions.ValidationError):
        detail = exc.detail
        if isinstance(detail, dict):
            return {str(k): [str(e) for e in v] for k, v in detail.items()}
        if isinstance(detail, list):
            return {"non_field_errors": [str(e) for e in detail]}
        return {"non_field_errors": [str(detail)]}
    return {}


def handler(exc: Exception, context: dict) -> Response | None:
    """Return a Sortiq-standard error envelope for any DRF exception."""

    response = drf_exception_handler(exc, context)

    request = context.get("request")
    request_id = getattr(request, "request_id", uuid.uuid4().hex[:8])

    if response is not None:
        code = _error_code(exc)
        message = str(exc.detail if hasattr(exc, "detail") else exc)
        details = _error_details(exc)
        data = {
            "error": {
                "code": code,
                "message": message,
                "details": details,
                "request_id": request_id,
                "status": response.status_code,
            }
        }
        response.data = data
        return response

    if isinstance(exc, Exception):
        return Response(
            {
                "error": {
                    "code": "internal",
                    "message": "An unexpected error occurred.",
                    "details": {},
                    "request_id": request_id,
                    "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return None
