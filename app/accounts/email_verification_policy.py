"""When email verification is off, login/signup issue tokens immediately (user + password only)."""

from django.conf import settings


def is_email_verification_required() -> bool:
    return bool(getattr(settings, 'REQUIRE_EMAIL_VERIFICATION', False))
