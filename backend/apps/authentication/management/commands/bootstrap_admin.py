"""Idempotent admin bootstrap command for the Sortiq control plane."""

from __future__ import annotations

import os
from secrets import token_urlsafe

from django.core.management.base import BaseCommand
from django.db import IntegrityError, transaction

from apps.authentication.models import User


class Command(BaseCommand):
    """Bootstrap an admin user and print a one-time bootstrap token."""

    help = "Create an admin user if none exists and print a bootstrap token."

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            default=os.environ.get("ADMIN_EMAIL", "admin@sortiq.local"),
        )
        parser.add_argument(
            "--username",
            default=os.environ.get("ADMIN_USERNAME", "admin"),
        )
        parser.add_argument(
            "--password",
            default=os.environ.get("ADMIN_PASSWORD", token_urlsafe(16)),
        )

    def handle(self, *args, **options):
        email = options["email"]
        username = options["username"]
        password = options["password"]

        user, created = self._get_or_create(email=email, username=username, password=password)

        if created:
            self.stdout.write(self.style.SUCCESS(f"Admin created: {email}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Admin already exists: {email}"))

        bootstrap_token = token_urlsafe(32)
        self.stdout.write(self.style.NOTICE(f"Bootstrap token: {bootstrap_token}"))

    @staticmethod
    def _get_or_create(email: str, username: str, password: str) -> tuple[User, bool]:
        try:
            user = User.objects.get(email=email)
            return user, False
        except User.DoesNotExist:
            pass

        try:
            with transaction.atomic():
                user = User.objects.create_superuser(
                    email=email, username=username, password=password
                )
                return user, True
        except IntegrityError:
            user = User.objects.get(email=email)
            return user, False
