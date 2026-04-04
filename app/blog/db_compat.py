"""Detect optional columns added by blog migration 0003 (AI fields)."""

from __future__ import annotations

from django.db import connection

from .models import BlogPost

_ai_columns_cache: bool | None = None


def clear_blog_ai_column_cache() -> None:
    """For tests or after migrations in long-lived workers (optional)."""
    global _ai_columns_cache
    _ai_columns_cache = None


def blog_post_table_has_ai_columns() -> bool:
    """
    True when DB table includes ai_generated and ai_log_id (migration 0003 applied).
    Cached per process so list endpoints do not introspect on every request.
    """
    global _ai_columns_cache
    if _ai_columns_cache is not None:
        return _ai_columns_cache
    table = BlogPost._meta.db_table
    try:
        with connection.cursor() as cursor:
            desc = connection.introspection.get_table_description(cursor, table)
        names = {col.name for col in desc}
        _ai_columns_cache = 'ai_generated' in names and 'ai_log_id' in names
    except Exception:
        _ai_columns_cache = False
    return _ai_columns_cache
