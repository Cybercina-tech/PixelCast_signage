"""Tests for public and platform blog APIs."""

import uuid
from unittest.mock import patch

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import User
from blog.models import BlogPost
from blog.serializers import _author_display_name


@pytest.fixture
def published_post(db, superadmin_user):
    past = timezone.now() - timezone.timedelta(days=1)
    return BlogPost.objects.create(
        title='Published Article',
        slug='published-article',
        excerpt='Excerpt',
        body='# Hello\n\nBody text.',
        status=BlogPost.STATUS_PUBLISHED,
        published_at=past,
        author=superadmin_user,
    )


@pytest.fixture
def draft_post(db):
    return BlogPost.objects.create(
        title='Draft Only',
        slug='draft-only',
        excerpt='',
        body='Secret',
        status=BlogPost.STATUS_DRAFT,
        published_at=None,
    )


@pytest.fixture
def future_post(db):
    future = timezone.now() + timezone.timedelta(days=7)
    return BlogPost.objects.create(
        title='Future Post',
        slug='future-post',
        excerpt='',
        body='Soon',
        status=BlogPost.STATUS_PUBLISHED,
        published_at=future,
    )


def test_author_display_name_survives_missing_user():
    """Orphan author_id (no matching User) must not raise — avoids 500 on public blog API."""

    class StubPost:
        author_id = uuid.uuid4()

        @property
        def author(self):
            raise User.DoesNotExist()

    assert _author_display_name(StubPost()) is None


@pytest.mark.django_db
def test_public_list_accepts_spurious_bearer_header(published_post):
    """SPA sends Authorization on all requests; public blog must not 401/5xx on bad tokens."""
    client = APIClient()
    r = client.get(
        '/api/public/blog/posts/',
        HTTP_AUTHORIZATION='Bearer totally.invalid.token',
    )
    assert r.status_code == 200


@pytest.mark.django_db
def test_public_list_only_shows_visible_posts(published_post, draft_post, future_post):
    client = APIClient()
    r = client.get('/api/public/blog/posts/')
    assert r.status_code == 200
    data = r.data
    slugs = {row['slug'] for row in data.get('results', data)}
    assert 'published-article' in slugs
    assert 'draft-only' not in slugs
    assert 'future-post' not in slugs


@pytest.mark.django_db
def test_public_retrieve_by_slug(published_post):
    client = APIClient()
    r = client.get('/api/public/blog/posts/published-article/')
    assert r.status_code == 200
    assert r.data['title'] == 'Published Article'
    assert 'Hello' in r.data['body']


@pytest.mark.django_db
def test_public_retrieve_draft_404(draft_post):
    client = APIClient()
    r = client.get('/api/public/blog/posts/draft-only/')
    assert r.status_code == 404


@pytest.mark.django_db
@patch('blog.views.blog_post_table_has_ai_columns', return_value=False)
def test_platform_list_compat_without_ai_columns_detected(_, superadmin_user, published_post):
    """Large page_size list must not 500 when schema is treated as pre-AI (only core columns selected)."""
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.get('/api/platform/blog/posts/', {'page_size': 100})
    assert r.status_code == 200
    assert 'results' in r.data


@pytest.mark.django_db
def test_platform_crud_developer(superadmin_user, published_post):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)

    r = client.post(
        '/api/platform/blog/posts/',
        {
            'title': 'New From API',
            'body': 'Content',
            'status': BlogPost.STATUS_DRAFT,
        },
        format='json',
    )
    assert r.status_code == 201
    new_id = r.data['id']
    assert r.data['slug']  # auto-generated

    r = client.get('/api/platform/blog/posts/')
    assert r.status_code == 200
    ids = {row['id'] for row in r.data['results']}
    assert new_id in ids

    r = client.patch(
        f'/api/platform/blog/posts/{new_id}/',
        {'title': 'Updated Title'},
        format='json',
    )
    assert r.status_code == 200
    assert r.data['title'] == 'Updated Title'

    r = client.delete(f'/api/platform/blog/posts/{new_id}/')
    assert r.status_code == 204


@pytest.mark.django_db
def test_platform_denied_for_manager(manager_user, published_post):
    client = APIClient()
    client.force_authenticate(user=manager_user)
    r = client.get('/api/platform/blog/posts/')
    assert r.status_code == 403


@pytest.mark.django_db
def test_platform_publish_action(superadmin_user, draft_post):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    r = client.post(f'/api/platform/blog/posts/{draft_post.id}/publish/', {}, format='json')
    assert r.status_code == 200
    assert r.data['status'] == BlogPost.STATUS_PUBLISHED
    assert r.data['published_at']

    anon = APIClient()
    r2 = anon.get('/api/public/blog/posts/draft-only/')
    assert r2.status_code == 200


@pytest.mark.django_db
def test_platform_slug_unique(superadmin_user):
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    BlogPost.objects.create(
        title='First',
        slug='taken-slug',
        body='a',
        status=BlogPost.STATUS_DRAFT,
    )
    r = client.post(
        '/api/platform/blog/posts/',
        {
            'title': 'Second',
            'slug': 'taken-slug',
            'body': 'b',
            'status': BlogPost.STATUS_DRAFT,
        },
        format='json',
    )
    assert r.status_code == 400
