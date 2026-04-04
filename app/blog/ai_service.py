"""OpenAI-powered blog generation with daily caps and audit logs."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone as dt_timezone

import requests
from django.utils import timezone
from django.utils.text import slugify

from core.email_crypto import decrypt_secret, encrypt_secret

from .models import BlogAISettings, BlogAIGenerationLog, BlogPost

logger = logging.getLogger(__name__)

SINGLETON_PK = 1

DEFAULT_SYSTEM_PROMPT = """You are a senior B2B marketing writer for PixelCast, a digital signage software platform
(retail, hospitality, corporate displays, scheduling, web players, fleet operations).
Write accurate, practical English. Do not invent product features that a typical SaaS signage product would not have."""

USER_JSON_INSTRUCTIONS = """
Return ONLY a single JSON object (no markdown fences) with exactly these keys:
- title (string)
- slug (string, lowercase, hyphens, ASCII)
- excerpt (string, 1-2 sentences)
- body (string, Markdown: use ## for sections, bullets where useful, roughly 800-2000 words)
- meta_title (string, SEO)
- meta_description (string, under ~160 characters when possible)
- primary_keywords (JSON array of 3-8 short keyword strings)
"""


def get_blog_ai_settings() -> BlogAISettings:
    obj, _ = BlogAISettings.objects.get_or_create(pk=SINGLETON_PK)
    return obj


def mask_api_key(encrypted_value: str) -> str:
    plain = decrypt_secret(encrypted_value or '')
    if not plain:
        return ''
    if len(plain) <= 8:
        return '********'
    return f'****{plain[-4:]}'


def utc_midnight_today():
    now = timezone.now()
    d = now.astimezone(dt_timezone.utc).date()
    return datetime(d.year, d.month, d.day, 0, 0, 0, tzinfo=dt_timezone.utc)


def count_ai_posts_today() -> int:
    start = utc_midnight_today()
    return BlogPost.objects.filter(ai_generated=True, created_at__gte=start).count()


def remaining_quota_today(settings_obj: BlogAISettings) -> int:
    return max(0, settings_obj.max_posts_per_day - count_ai_posts_today())


def recent_titles(limit: int = 15):
    return list(BlogPost.objects.order_by('-created_at').values_list('title', flat=True)[:limit])


def build_user_prompt(settings_obj: BlogAISettings, recent: list[str]) -> str:
    pool = (settings_obj.keyword_pool or '').strip()
    recent_block = '\n'.join(f'- {t}' for t in recent) if recent else '(none yet)'
    return f"""Write ONE blog article for the PixelCast digital signage product blog.

Keyword / topic pool (choose a focused SEO angle; use a sensible primary keyword phrase):
{pool or '(general: digital signage software, screen networks, templates, scheduling, operations)'}

Avoid duplicating or paraphrasing these recent article titles too closely:
{recent_block}
"""


def call_openai_chat(settings_obj: BlogAISettings, user_content: str) -> dict:
    api_key = decrypt_secret(settings_obj.openai_api_key_encrypted or '')
    if not api_key:
        raise ValueError('OpenAI API key is not configured')

    base = (settings_obj.api_base_url or 'https://api.openai.com/v1').rstrip('/')
    url = f'{base}/chat/completions'

    system_text = (settings_obj.system_prompt or '').strip()
    if not system_text:
        system_text = DEFAULT_SYSTEM_PROMPT
    system_text = f'{system_text.strip()}\n{USER_JSON_INSTRUCTIONS}'

    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    payload = {
        'model': settings_obj.model,
        'messages': [
            {'role': 'system', 'content': system_text},
            {'role': 'user', 'content': user_content},
        ],
        'response_format': {'type': 'json_object'},
        'temperature': 0.7,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    if not resp.ok:
        err = resp.text[:500] if resp.text else resp.reason
        raise RuntimeError(f'OpenAI HTTP {resp.status_code}: {err}')
    data = resp.json()
    content = data['choices'][0]['message']['content']
    return json.loads(content)


def create_post_from_payload(
    article: dict,
    log: BlogAIGenerationLog,
    user,
    settings_obj: BlogAISettings,
) -> BlogPost:
    title = (article.get('title') or '').strip()[:255]
    if not title:
        raise ValueError('Missing title')
    slug_raw = (article.get('slug') or '').strip()
    body = (article.get('body') or '').strip()
    if not body:
        raise ValueError('Missing body')
    excerpt = (article.get('excerpt') or '').strip()[:2000]
    meta_title = (article.get('meta_title') or '').strip()[:255]
    meta_description = (article.get('meta_description') or '').strip()[:500]

    status = BlogPost.STATUS_PUBLISHED if settings_obj.auto_publish else BlogPost.STATUS_DRAFT
    published_at = timezone.now() if status == BlogPost.STATUS_PUBLISHED else None

    slug_stem = slugify(slug_raw)[:280] if slug_raw else slugify(title)[:280] or 'post'

    post = BlogPost(
        title=title,
        slug=slug_stem,
        excerpt=excerpt,
        body=body,
        meta_title=meta_title or title,
        meta_description=meta_description or excerpt[:500],
        status=status,
        published_at=published_at,
        author=user if user and getattr(user, 'is_authenticated', False) else None,
        ai_generated=True,
        ai_log=log,
    )
    post.save()
    return post


def run_generation(*, requested_count: int, trigger: str, user=None):
    """
    Generate up to min(requested_count, remaining_quota, posts_per_run) posts.
    Returns (BlogAIGenerationLog, list[BlogPost]).
    """
    settings_obj = get_blog_ai_settings()

    if not settings_obj.enabled:
        log = BlogAIGenerationLog.objects.create(
            trigger=trigger,
            status=BlogAIGenerationLog.STATUS_FAILED,
            message='Blog AI is disabled',
            requested_count=requested_count,
            created_count=0,
        )
        return log, []

    if not decrypt_secret(settings_obj.openai_api_key_encrypted or ''):
        log = BlogAIGenerationLog.objects.create(
            trigger=trigger,
            status=BlogAIGenerationLog.STATUS_FAILED,
            message='OpenAI API key is not configured',
            requested_count=requested_count,
            created_count=0,
        )
        return log, []

    remaining = remaining_quota_today(settings_obj)
    effective = min(max(0, requested_count), remaining, settings_obj.posts_per_run)
    if effective <= 0:
        log = BlogAIGenerationLog.objects.create(
            trigger=trigger,
            status=BlogAIGenerationLog.STATUS_SKIPPED_QUOTA,
            message='Daily quota reached or posts_per_run is 0',
            requested_count=requested_count,
            created_count=0,
        )
        return log, []

    log = BlogAIGenerationLog.objects.create(
        trigger=trigger,
        status=BlogAIGenerationLog.STATUS_SUCCESS,
        message='',
        requested_count=requested_count,
        created_count=0,
    )

    posts: list[BlogPost] = []
    errors: list[str] = []

    for _ in range(effective):
        try:
            recent = recent_titles()
            prompt = build_user_prompt(settings_obj, recent)
            article = call_openai_chat(settings_obj, prompt)
            post = create_post_from_payload(article, log, user, settings_obj)
            posts.append(post)
        except Exception as e:
            logger.exception('AI blog generation step failed')
            errors.append(str(e)[:400])

    created = len(posts)
    log.created_count = created
    if created == 0:
        log.status = BlogAIGenerationLog.STATUS_FAILED
        log.message = (errors[0] if errors else 'No posts created')[:500]
        log.error_detail = '\n'.join(errors)[:2000]
    elif created < effective:
        log.status = BlogAIGenerationLog.STATUS_PARTIAL
        log.message = f'Created {created} of {effective} requested in this batch'
        if errors:
            log.error_detail = '\n'.join(errors)[:2000]
    else:
        log.message = f'Created {created} post(s)'
    log.save(update_fields=['created_count', 'status', 'message', 'error_detail'])
    return log, posts


def apply_api_key_if_provided(settings_obj: BlogAISettings, raw_key: str | None) -> None:
    """Set encrypted key on instance when a non-empty string is provided; caller must save()."""
    if raw_key is None:
        return
    key = (raw_key or '').strip()
    if not key:
        return
    settings_obj.openai_api_key_encrypted = encrypt_secret(key)
