"""Clear 2FA flags and secrets for all users (use when disabling platform 2FA)."""
from django.core.management.base import BaseCommand

from accounts.models import User


class Command(BaseCommand):
    help = 'Disable two-factor authentication on every user account.'

    def handle(self, *args, **options):
        updated = User.objects.filter(is_2fa_enabled=True).update(
            is_2fa_enabled=False,
            totp_secret='',
            backup_codes_hash='',
        )
        self.stdout.write(self.style.SUCCESS(f'Cleared 2FA on {updated} user(s).'))
