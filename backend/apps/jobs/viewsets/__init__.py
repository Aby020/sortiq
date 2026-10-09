"""Job status & cancellation APIs."""

from __future__ import annotations

import uuid

from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, mixins

from apps.jobs.models import Job
from apps.jobs.serializers import JobSerializer


class JobViewSet(mixins.RetrieveModelMixin, GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = JobSerializer

    def get_queryset(self):
        return Job.objects.filter(user=self.request.user)

    @action(detail=True, methods=["post"])
    def cancel(self, request: Request, pk: uuid.UUID) -> Response:
        job = self.get_object()
        if job.status not in ("pending", "running"):
            return Response(
                {"detail": "Cannot cancel a completed or failed job."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        job.status = "cancelled"
        job.save(update_fields=["status"])
        return Response({"status": "cancelled", "job_id": str(job.id)})
