"""
Management command to cleanup old audit logs.

Usage:
    python manage.py cleanup_audit_logs --days=365
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import AuditLog
from django.conf import settings


class Command(BaseCommand):
    help = 'Cleanup old audit logs based on retention policy'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            help='Delete logs older than N days (default: from AUDIT_LOGGING config)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )

    def handle(self, *args, **options):
        days = options.get('days')
        if not days:
            audit_config = getattr(settings, 'AUDIT_LOGGING', {})
            days = audit_config.get('RETENTION_DAYS', 365)

        dry_run = options['dry_run']

        cutoff_date = timezone.now() - timedelta(days=days)

        old_logs = AuditLog.objects.filter(timestamp__lt=cutoff_date)
        count = old_logs.count()

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would delete {count} audit log(s) older than {days} days'
                )
            )
            return

        if count == 0:
            self.stdout.write('No old audit logs to cleanup.')
            return

        deleted_count, _ = old_logs.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Deleted {deleted_count} audit log(s) older than {days} days'
            )
        )

