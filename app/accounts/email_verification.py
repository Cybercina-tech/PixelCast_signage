"""Shared helpers for email verification codes (SMTP via system settings)."""
from __future__ import annotations

import logging

from core.email_service import resolve_default_from_email, send_system_email

logger = logging.getLogger(__name__)


def mask_email(email: str) -> str:
    """Return a partially masked email for display (e.g. j***@example.com)."""
    email = (email or '').strip()
    if '@' not in email:
        return email or 'your email'
    local, domain = email.rsplit('@', 1)
    if len(local) <= 1:
        masked_local = '*'
    elif len(local) == 2:
        masked_local = local[0] + '*'
    else:
        masked_local = local[0] + ('*' * min(len(local) - 2, 4)) + local[-1]
    return f'{masked_local}@{domain}'


def send_user_verification_email(user, *, request=None) -> str:
    """
    Generate a verification code, send it via system SMTP, and return the code.

    Raises on SMTP failure so callers can surface errors to the client.
    """
    code = user.generate_verification_code()
    name = user.full_name or user.username or 'there'
    subject = 'PixelCast Signage — Email verification code'
    message = f'''Hello {name},

Your email verification code is: {code}

This code expires in 10 minutes.

If you did not request this, you can ignore this email.

— PixelCast Signage
'''
    send_system_email(
        subject=subject,
        message=message,
        recipient_list=[user.email],
        from_email=resolve_default_from_email(),
        fail_silently=False,
    )
    return code
