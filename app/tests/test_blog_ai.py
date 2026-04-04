"""Tests for blog OpenAI settings, quota, and generation (mocked HTTP)."""

import json
from unittest.mock import patch

import pytest
from rest_framework.test import APIClient

from blog.ai_service import get_blog_ai_settings, run_generation
from blog.models import BlogAIGenerationLog, BlogPost
from core.email_crypto import encrypt_secret


@pytest.fixture
def ai_enabled_settings(db):
    s = get_blog_ai_settings()
    s.enabled = True
    s.openai_api_key_encrypted = encrypt_secret('sk-test-key-for-encryption')
    s.model = 'gpt-4o-mini'
    s.api_base_url = 'https://api.openai.com/v1'
    s.max_posts_per_day = 2
    s.posts_per_run = 2
    s.auto_publish = False
    s.keyword_pool = 'digital signage\nretail displays'
    s.save()
    return s


@pytest.mark.django_db
def test_run_generation_skipped_when_disabled(superadmin_user):
    s = get_blog_ai_settings()
    s.enabled = False
    s.openai_api_key_encrypted = encrypt_secret('sk-x')
    s.save()
    log, posts = run_generation(requested_count=2, trigger=BlogAIGenerationLog.TRIGGER_MANUAL, user=superadmin_user)
    assert log.status == BlogAIGenerationLog.STATUS_FAILED
    assert 'disabled' in log.message.lower()
    assert posts == []


@pytest.mark.django_db
def test_run_generation_skipped_quota(ai_enabled_settings, superadmin_user):
    log_prev = BlogAIGenerationLog.objects.create(
        trigger=BlogAIGenerationLog.TRIGGER_MANUAL,
        status=BlogAIGenerationLog.STATUS_SUCCESS,
        message='seed',
        requested_count=2,
        created_count=2,
    )
    for i in range(2):
        BlogPost.objects.create(
            title=f'AI Seed {i}',
            slug=f'ai-seed-{i}',
            excerpt='e',
            body='body',
            status=BlogPost.STATUS_DRAFT,
            ai_generated=True,
            ai_log=log_prev,
            author=superadmin_user,
        )
    log, posts = run_generation(requested_count=2, trigger=BlogAIGenerationLog.TRIGGER_MANUAL, user=superadmin_user)
    assert log.status == BlogAIGenerationLog.STATUS_SKIPPED_QUOTA
    assert posts == []


@pytest.mark.django_db
def test_run_generation_success_mocked_openai(ai_enabled_settings, superadmin_user):
    article = {
        'title': 'Mock AI Article',
        'slug': 'mock-ai-article',
        'excerpt': 'Short excerpt for the card.',
        'body': '## Intro\n\nHello **world**.',
        'meta_title': 'Mock AI Article',
        'meta_description': 'Short excerpt for the card.',
        'primary_keywords': ['digital signage', 'displays'],
    }

    class FakeResp:
        ok = True
        status_code = 200
        text = ''

        def json(self):
            return {'choices': [{'message': {'content': json.dumps(article)}}]}

    def fake_post(url, headers=None, json=None, timeout=None):
        assert 'chat/completions' in url
        return FakeResp()

    with patch('blog.ai_service.requests.post', side_effect=fake_post):
        log, posts = run_generation(
            requested_count=1,
            trigger=BlogAIGenerationLog.TRIGGER_MANUAL,
            user=superadmin_user,
        )

    assert log.status == BlogAIGenerationLog.STATUS_SUCCESS
    assert log.created_count == 1
    assert len(posts) == 1
    p = posts[0]
    assert p.title == 'Mock AI Article'
    assert p.ai_generated is True
    assert p.status == BlogPost.STATUS_DRAFT


@pytest.mark.django_db
def test_platform_ai_settings_get_mask_key(superadmin_user, ai_enabled_settings):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.get('/api/platform/blog/ai/settings/')
    assert r.status_code == 200
    assert 'openai_api_key_masked' in r.data
    assert r.data['openai_api_key_masked'].startswith('****')


@pytest.mark.django_db
def test_platform_ai_generate_mocked(superadmin_user, ai_enabled_settings):
    article = {
        'title': 'API Gen Post',
        'slug': 'api-gen-post',
        'excerpt': 'Ex',
        'body': '## Body\n\ntext',
        'meta_title': 'API Gen Post',
        'meta_description': 'Ex',
        'primary_keywords': ['a', 'b'],
    }

    class FakeResp:
        ok = True
        status_code = 200
        text = ''

        def json(self):
            return {'choices': [{'message': {'content': json.dumps(article)}}]}

    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    with patch('blog.ai_service.requests.post', return_value=FakeResp()):
        r = client.post('/api/platform/blog/ai/generate/', {'count': 1}, format='json')
    assert r.status_code == 200
    assert r.data['log']['status'] == BlogAIGenerationLog.STATUS_SUCCESS
    assert len(r.data['post_ids']) == 1


@pytest.mark.django_db
def test_platform_ai_denied_for_manager(manager_user, ai_enabled_settings):
    client = APIClient()
    client.force_authenticate(user=manager_user)
    r = client.get('/api/platform/blog/ai/settings/')
    assert r.status_code == 403
