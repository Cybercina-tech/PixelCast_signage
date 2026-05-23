"""
Build browser-reachable media URLs for Docker / reverse-proxy deployments.
"""
from __future__ import annotations

from urllib.parse import urlparse

from django.conf import settings


def _public_site_origin(request=None) -> str:
    if request is not None:
        actual = getattr(request, '_request', request)
        if hasattr(actual, 'get_host'):
            try:
                scheme = 'https'
                if getattr(actual, 'is_secure', lambda: False)():
                    scheme = 'https'
                elif actual.META.get('HTTP_X_FORWARDED_PROTO', '').lower() == 'https':
                    scheme = 'https'
                elif actual.scheme == 'http':
                    scheme = 'http'
                return f'{scheme}://{actual.get_host()}'.rstrip('/')
            except Exception:
                pass

    for candidate in (
        getattr(settings, 'PUBLIC_WEB_APP_URL', ''),
        getattr(settings, 'BASE_URL', ''),
    ):
        if isinstance(candidate, str) and candidate.strip():
            parsed = urlparse(candidate.strip())
            if parsed.scheme in ('http', 'https') and parsed.netloc:
                return f'{parsed.scheme}://{parsed.netloc}'.rstrip('/')
    return 'http://localhost:8000'


def _is_internal_hostname(hostname: str | None) -> bool:
    if not hostname:
        return True
    h = hostname.lower()
    if h in ('localhost', '127.0.0.1', '0.0.0.0', 'backend', 'frontend'):
        return True
    if h.endswith('.traefik.me'):
        return True
    return False


def resolve_public_media_url(file_url: str | None, request=None) -> str | None:
    """
    Return an absolute URL the browser can load (SPA origin or public site).
    Relative paths (/media/...) are preferred when possible.
    """
    if not file_url:
        return None

    raw = str(file_url).strip()
    if not raw:
        return None

    origin = _public_site_origin(request)
    media_prefix = getattr(settings, 'MEDIA_URL', '/media/').rstrip('/') + '/'

    if raw.startswith('http://') or raw.startswith('https://'):
        parsed = urlparse(raw)
        if _is_internal_hostname(parsed.hostname):
            path = parsed.path or ''
            if not path.startswith('/'):
                path = '/' + path
            return f'{origin}{path}'
        return raw

    if raw.startswith('/'):
        return f'{origin}{raw}'

    clean = raw.lstrip('/')
    media_key = media_prefix.lstrip('/')
    if clean.startswith(media_key):
        return f'{origin}/{clean}'

    return f'{origin}{media_prefix}{clean}'
