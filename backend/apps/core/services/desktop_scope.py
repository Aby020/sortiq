"""Desktop runtime scope helper.

In local desktop mode every DRF endpoint allows anonymous access
(`AllowAny`). Viewsets that historically scoped queries to
``request.user`` need a graceful fallback for anonymous requests,
otherwise filtering by ``AnonymousUser`` raises a ``ValidationError``
(``'AnonymousUser' is not a valid UUID``).

Anonymous requests are scoped to a provisioned local desktop user so
the whole app (lists *and* creates) keeps working without a login
screen.
"""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db.models import QuerySet


def desktop_user():
    """Return (or provision) the local desktop user."""

    User = get_user_model()
    user, _ = User.objects.get_or_create(
        username="desktop",
        defaults={"email": "desktop@sortiq.local", "is_active": True},
    )
    return user


def effective_user(request):
    """Return the authenticated user, or the local desktop user."""

    user = getattr(request, "user", None)
    if user is not None and not isinstance(user, AnonymousUser) and user.is_authenticated:
        return user
    return desktop_user()


def user_scope(request, queryset: QuerySet, user_field: str = "user") -> QuerySet:
    """Scope ``queryset`` to the effective (desktop) user."""

    return queryset.filter(**{user_field: effective_user(request)})
