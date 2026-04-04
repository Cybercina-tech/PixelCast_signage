"""
Scheduled AI blog generation. Run via cron, e.g. daily at 08:00 server time:

    0 8 * * * cd /app && python manage.py blog_ai_daily
"""

from django.core.management.base import BaseCommand

from blog.ai_service import get_blog_ai_settings, run_generation
from blog.models import BlogAIGenerationLog


class Command(BaseCommand):
    help = 'Generate up to posts_per_run AI blog posts if enabled and daily quota allows.'

    def handle(self, *args, **options):
        settings_obj = get_blog_ai_settings()
        if not settings_obj.enabled:
            self.stdout.write(self.style.WARNING('Blog AI is disabled; skipping.'))
            return

        log, posts = run_generation(
            requested_count=settings_obj.posts_per_run,
            trigger=BlogAIGenerationLog.TRIGGER_SCHEDULED,
            user=None,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Blog AI run: status={log.status} created={log.created_count} '
                f'requested_cap={settings_obj.posts_per_run} message={log.message!r}'
            )
        )
