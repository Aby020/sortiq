"""Custom middleware for the Sortiq control plane."""

from __future__ import annotations

import uuid

from django.utils.deprecation import MiddlewareMixin


class RequestIdMiddleware(MiddlewareMixin):
    """Attach a per-request UUID to every incoming request/response."""

    @staticmethod
    def process_request(request):
        request.request_id = uuid.uuid4().hex[:8]

    @staticmethod
    def process_response(request, response):
        response["X-Request-ID"] = request.request_id
        return response
