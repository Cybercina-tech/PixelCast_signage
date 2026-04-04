import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class BlogAISettings(models.Model):
    """Singleton (pk=1) — OpenAI + rate limits for automated blog generation."""

    id = models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False)
    enabled = models.BooleanField(default=False)
    openai_api_key_encrypted = models.TextField(blank=True, default='')
    model = models.CharField(max_length=128, default='gpt-4o-mini')
    api_base_url = models.URLField(
        max_length=512,
        default='https://api.openai.com/v1',
        help_text='OpenAI API base, trailing /v1',
    )
    system_prompt = models.TextField(
        blank=True,
        default='',
        help_text='System instructions prepended to each generation request.',
    )
    keyword_pool = models.TextField(
        blank=True,
        default='',
        help_text='One topic or keyword per line (or comma-separated) for SEO-focused posts.',
    )
    posts_per_run = models.PositiveSmallIntegerField(default=2)
    max_posts_per_day = models.PositiveSmallIntegerField(default=2)
    auto_publish = models.BooleanField(
        default=False,
        help_text='If true, AI posts are published immediately; otherwise draft.',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Blog AI settings'

    def __str__(self):
        return 'Blog AI settings'


class BlogAIGenerationLog(models.Model):
    """Audit trail for AI blog generation runs."""

    TRIGGER_SCHEDULED = 'scheduled'
    TRIGGER_MANUAL = 'manual'
    TRIGGER_CHOICES = [
        (TRIGGER_SCHEDULED, 'Scheduled'),
        (TRIGGER_MANUAL, 'Manual'),
    ]

    STATUS_SUCCESS = 'success'
    STATUS_PARTIAL = 'partial'
    STATUS_SKIPPED_QUOTA = 'skipped_quota'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_SUCCESS, 'Success'),
        (STATUS_PARTIAL, 'Partial'),
        (STATUS_SKIPPED_QUOTA, 'Skipped quota'),
        (STATUS_FAILED, 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    trigger = models.CharField(max_length=20, choices=TRIGGER_CHOICES)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES)
    message = models.CharField(max_length=512, blank=True)
    requested_count = models.PositiveSmallIntegerField(default=0)
    created_count = models.PositiveSmallIntegerField(default=0)
    error_detail = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.created_at:%Y-%m-%d %H:%M} {self.status}'


class BlogPost(models.Model):
    """Marketing blog post — edited via platform API (Developer) or Django admin."""

    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PUBLISHED, 'Published'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, db_index=True)
    excerpt = models.TextField(blank=True)
    body = models.TextField(help_text='Markdown content')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT, db_index=True)
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)
    featured_image_url = models.URLField(max_length=2048, blank=True)
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='blog_posts',
    )
    ai_generated = models.BooleanField(default=False, db_index=True)
    ai_log = models.ForeignKey(
        'BlogAIGenerationLog',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='blog_posts',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
        ]

    def __str__(self):
        return self.title

    def _ensure_unique_slug(self, stem: str) -> str:
        stem = (stem or '')[:280] or 'post'
        candidate = stem
        n = 2
        qs = BlogPost.objects.exclude(pk=self.pk)
        while qs.filter(slug=candidate).exists():
            suffix = f'-{n}'
            max_stem = max(0, 280 - len(suffix))
            candidate = f'{stem[:max_stem]}{suffix}'
            n += 1
        return candidate

    def save(self, *args, **kwargs):
        title = (self.title or '').strip()
        raw_slug = (self.slug or '').strip()
        if not raw_slug and title:
            stem = slugify(self.title)[:280] or 'post'
            self.slug = self._ensure_unique_slug(stem)
        elif raw_slug:
            stem = slugify(self.slug)[:280] or 'post'
            self.slug = self._ensure_unique_slug(stem)
        if self.status == self.STATUS_PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
