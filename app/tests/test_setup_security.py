"""Security-related tests for setup/installation API."""

import pytest
from django.test import Client, override_settings
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_setup_status_never_returns_db_password():
    client = APIClient()
    url = reverse('setup:setup-status')
    r = client.get(url)
    assert r.status_code == 200
    assert 'db_password' not in r.data
    assert 'db_password_configured' in r.data
    assert isinstance(r.data['db_password_configured'], bool)


@pytest.mark.django_db
@override_settings(
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
)
def test_setup_status_password_configured_reflects_settings():
    client = APIClient()
    url = reverse('setup:setup-status')
    r = client.get(url)
    assert r.status_code == 200
    assert r.data['db_password_configured'] is False


def test_api_health_live_ok_before_installation(monkeypatch, tmp_path):
    """Docker healthcheck uses /api/health/live/ — must not get 503 before install."""
    monkeypatch.delenv('PIXELCAST_SIGNAGE_INSTALLED', raising=False)
    monkeypatch.delenv('SCREENGRAM_INSTALLED', raising=False)
    lock = tmp_path / 'installed.lock'
    with override_settings(INSTALLATION_STATE_DIR=tmp_path):
        assert not lock.exists()
        r = Client().get('/api/health/live/')
    assert r.status_code == 200
    assert r.json()['live'] is True


def test_api_health_ok_before_installation(monkeypatch, tmp_path):
    """Docker/Dokploy healthcheck must not get 503 from InstallationCheckMiddleware."""
    monkeypatch.delenv('PIXELCAST_SIGNAGE_INSTALLED', raising=False)
    monkeypatch.delenv('SCREENGRAM_INSTALLED', raising=False)
    lock = tmp_path / 'installed.lock'
    with override_settings(INSTALLATION_STATE_DIR=tmp_path):
        assert not lock.exists()
        r = Client().get('/api/health/')
    assert r.status_code == 200
    assert r.json()['status'] == 'ok'
