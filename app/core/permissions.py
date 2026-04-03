"""DRF permissions for core infrastructure (avoid importing saas_platform from core)."""

from rest_framework.permissions import BasePermission


class IsDeveloper(BasePermission):
    """Matches platform super-admin: Developer role or Django superuser."""

    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and u.is_developer())
