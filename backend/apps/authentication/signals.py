"""Signal handlers for the authentication app."""

from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.authentication.models import User


@receiver(post_save, sender=User)
def _log_user_created(sender, instance: User, created: bool, **kwargs):
    if created:
        import structlog

        structlog.get_logger(__name__).info("user.created", user_id=str(instance.id))
