"""
Create a default Developer user if no account with that email exists.

For local/dev bootstrap. Password is set with set_password (does not run Django's
password validators) so short/dev passwords work.

Usage:
  python manage.py ensure_default_developer
  python manage.py ensure_default_developer --email you@example.com --password 'yourpass'
  python manage.py ensure_default_developer --update   # reset password + role if user exists

Docker:
  docker compose exec backend python manage.py ensure_default_developer --update
"""

from django.core.management.base import BaseCommand

from accounts.models import User


class Command(BaseCommand):
    help = 'Create default Developer user if missing (idempotent by email).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            default='admin@pixelcast.com',
            help='Email (and username) for the account',
        )
        parser.add_argument(
            '--password',
            default='adminadmina',
            help='Plain password (stored hashed; not validated for strength)',
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='If user exists: set password and Developer role (is_staff/is_superuser)',
        )

    def handle(self, *args, **options):
        email = options['email'].strip().lower()
        password = options['password']
        update = options['update']

        existing = User.objects.filter(email__iexact=email).first()

        if existing:
            if not update:
                self.stdout.write(
                    self.style.WARNING(
                        f'User with email {email} already exists — nothing to do. '
                        f'Pass --update to reset password and Developer role.'
                    )
                )
                return
            existing.username = email
            existing.role = 'Developer'
            existing.is_staff = True
            existing.is_superuser = True
            existing.is_active = True
            existing.set_password(password)
            existing.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Updated Developer: email={email!r} username={email!r} '
                    f'(is_superuser=True, is_staff=True)'
                )
            )
            return

        user = User(
            username=email,
            email=email,
            role='Developer',
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )
        user.set_password(password)
        user.save()

        self.stdout.write(
            self.style.SUCCESS(
                f'Created Developer: email={email!r} username={email!r} '
                f'(is_superuser=True, is_staff=True)'
            )
        )
