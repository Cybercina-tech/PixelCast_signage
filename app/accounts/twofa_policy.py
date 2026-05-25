"""Platform-wide two-factor authentication toggle."""
from django.conf import settings


def is_twofa_enabled() -> bool:
    """When False, login never requires 2FA and setup endpoints are disabled."""
    # Platform 2FA is off unless explicitly enabled in environment.
    return bool(getattr(settings, 'ENABLE_TWO_FACTOR_AUTH', False))
