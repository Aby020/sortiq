"""Custom user model for the Sortiq authentication app."""

from __future__ import annotations

import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """User with a UUID primary key and enforced unique email."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    email = models.EmailField(unique=True)

    class Meta:
        app_label = "authentication"
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return f"{self.email}"
