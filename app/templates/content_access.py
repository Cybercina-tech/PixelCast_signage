"""
Content / media-library access helpers for tenant and template scoping.
"""
from __future__ import annotations

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db.models import Q, QuerySet, Sum
from django.db.models.functions import Coalesce

from accounts.models import User


def media_library_quota_bytes(user: User | None = None) -> int:
    """Per-tenant media library quota from settings (bytes)."""
    cfg = getattr(settings, 'CONTENT_STORAGE', {}) or {}
    return int(cfg.get('MEDIA_LIBRARY_QUOTA_BYTES', 500 * 1024 * 1024))


def _standalone_media_q(user: User) -> Q:
    """Standalone uploads (widget is null) visible to this user."""
    base = Q(widget__isnull=True)
    if user.is_developer():
        return base
    tenant_id = getattr(user, 'tenant_id', None)
    if tenant_id:
        return base & Q(uploaded_by__tenant_id=tenant_id)
    if user.organization_name:
        return base & (
            Q(uploaded_by=user)
            | Q(uploaded_by__organization_name=user.organization_name)
        )
    return base & Q(uploaded_by=user)


def _widget_bound_media_q(user: User) -> Q:
    """Widget-bound content visible when the parent template is accessible."""
    templates = user.get_accessible_templates_queryset()
    return Q(widget__isnull=False, widget__layer__template__in=templates)


def filter_content_queryset_for_user(queryset: QuerySet, user: User) -> QuerySet:
    """
    Restrict Content rows to media-library uploads and widget content the user may access.
    """
    if not user or not getattr(user, 'is_authenticated', False):
        return queryset.none()
    if user.is_developer():
        return queryset
    scoped = queryset.filter(_standalone_media_q(user) | _widget_bound_media_q(user))
    # Subquery avoids PostgreSQL DISTINCT + Meta.ordering conflicts on joined lists.
    visible_ids = scoped.values_list('pk', flat=True).distinct()
    return queryset.filter(pk__in=visible_ids)


def assert_content_access(user: User, content) -> None:
    """Raise PermissionDenied if the user cannot access this content row."""
    if user.is_developer():
        return
    from .models import Content

    if not filter_content_queryset_for_user(Content.objects.filter(pk=content.pk), user).exists():
        raise PermissionDenied('You do not have permission to access this content.')


def get_tenant_storage_used_bytes(user: User) -> int:
    """Sum file_size for standalone media-library content in the user's scope."""
    from .models import Content

    qs = filter_content_queryset_for_user(
        Content.objects.filter(widget__isnull=True).exclude(file_size__isnull=True),
        user,
    )
    total = qs.aggregate(total=Coalesce(Sum('file_size'), 0))['total']
    return int(total or 0)
