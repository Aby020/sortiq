"""List all configured URLs for the Sortiq control plane."""

from __future__ import annotations

from django.core.management.base import BaseCommand
from django.urls import get_resolver


class Command(BaseCommand):
    """Print every registered URL pattern."""

    help = "Show all URL patterns."

    def handle(self, *args, **options):
        resolver = get_resolver()
        for pattern in resolver.url_patterns:
            self.stdout.write(str(pattern.pattern))
