import json
from datetime import timedelta

from django.test import TestCase, override_settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from .models import Screen, PairingSession

User = get_user_model()


def _make_user(username='owner', **kwargs):
    defaults = dict(email=f'{username}@test.local', password='pass1234')
    defaults.update(kwargs)
    return User.objects.create_user(username=username, **defaults)


class DeviceTokenModelTests(TestCase):
    """Tests for Screen device-token helpers."""

    def setUp(self):
        self.user = _make_user()
        self.screen = Screen.objects.create(
            name='Test TV',
            device_id='dev_test_001',
            owner=self.user,
        )

    def test_issue_and_verify_device_token(self):
        raw = self.screen.issue_device_token()
        self.assertIsNotNone(raw)
        self.assertTrue(len(raw) > 30)
        self.assertTrue(self.screen.verify_device_token(raw))

    def test_verify_wrong_token_fails(self):
        self.screen.issue_device_token()
        self.assertFalse(self.screen.verify_device_token('totally-wrong'))

    def test_verify_empty_token_fails(self):
        self.screen.issue_device_token()
        self.assertFalse(self.screen.verify_device_token(''))
        self.assertFalse(self.screen.verify_device_token(None))

    def test_revoke_then_verify_fails(self):
        raw = self.screen.issue_device_token()
        self.screen.revoke_device_token()
        self.assertFalse(self.screen.verify_device_token(raw))

    def test_authenticate_device_classmethod(self):
        raw = self.screen.issue_device_token()
        found = Screen.authenticate_device(str(self.screen.id), raw)
        self.assertEqual(found, self.screen)

    def test_authenticate_device_bad_id(self):
        raw = self.screen.issue_device_token()
        self.assertIsNone(Screen.authenticate_device('00000000-0000-0000-0000-000000000000', raw))

    def test_authenticate_device_revoked(self):
        raw = self.screen.issue_device_token()
        self.screen.revoke_device_token()
        self.assertIsNone(Screen.authenticate_device(str(self.screen.id), raw))


class PairingFlowTests(TestCase):
    """End-to-end pairing: generate -> bind -> status (one-time activation)."""

    def setUp(self):
        self.user = _make_user()
        self.client = APIClient()

    # ── generate ────────────────────────────────────────────────────

    def test_generate_creates_session(self):
        resp = self.client.post('/api/pairing/generate/')
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data['status'], 'success')
        session = data['pairing_session']
        self.assertEqual(len(session['pairing_code']), 6)
        self.assertIn('pairing_token', session)

    # ── bind ────────────────────────────────────────────────────────

    def test_bind_with_code(self):
        gen = self.client.post('/api/pairing/generate/').json()
        code = gen['pairing_session']['pairing_code']

        self.client.force_authenticate(user=self.user)
        resp = self.client.post('/api/pairing/bind/', {
            'pairing_code': code,
            'screen_name': 'Lobby TV',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['status'], 'success')
        self.assertTrue(Screen.objects.filter(name='Lobby TV').exists())

    def test_bind_requires_auth(self):
        gen = self.client.post('/api/pairing/generate/').json()
        code = gen['pairing_session']['pairing_code']
        resp = self.client.post('/api/pairing/bind/', {'pairing_code': code})
        self.assertIn(resp.status_code, [401, 403])

    def test_bind_expired_session(self):
        gen = self.client.post('/api/pairing/generate/').json()
        code = gen['pairing_session']['pairing_code']
        # Force expiry
        PairingSession.objects.filter(pairing_code=code).update(
            expires_at=timezone.now() - timedelta(minutes=1),
        )
        self.client.force_authenticate(user=self.user)
        resp = self.client.post('/api/pairing/bind/', {'pairing_code': code})
        self.assertIn(resp.status_code, [400])

    def test_bind_duplicate_rejected(self):
        gen = self.client.post('/api/pairing/generate/').json()
        code = gen['pairing_session']['pairing_code']
        self.client.force_authenticate(user=self.user)
        self.client.post('/api/pairing/bind/', {'pairing_code': code})
        resp = self.client.post('/api/pairing/bind/', {'pairing_code': code})
        self.assertEqual(resp.status_code, 400)

    # ── status (one-time activation) ────────────────────────────────

    def test_status_delivers_device_token_once(self):
        gen = self.client.post('/api/pairing/generate/').json()
        token = gen['pairing_session']['pairing_token']
        code = gen['pairing_session']['pairing_code']

        self.client.force_authenticate(user=self.user)
        self.client.post('/api/pairing/bind/', {'pairing_code': code})
        self.client.force_authenticate(user=None)

        # First poll — should get device_token
        resp1 = self.client.get('/api/pairing/status/', {'pairing_token': token})
        self.assertEqual(resp1.status_code, 200)
        data1 = resp1.json()
        self.assertEqual(data1['status'], 'paired')
        self.assertIn('device_token', data1)
        self.assertIsNotNone(data1['device_token'])

        # Second poll — should NOT get device_token again
        resp2 = self.client.get('/api/pairing/status/', {'pairing_token': token})
        data2 = resp2.json()
        self.assertEqual(data2['status'], 'paired')
        self.assertNotIn('device_token', data2)

    def test_status_pending(self):
        gen = self.client.post('/api/pairing/generate/').json()
        token = gen['pairing_session']['pairing_token']
        resp = self.client.get('/api/pairing/status/', {'pairing_token': token})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['status'], 'pending')


class DeviceAuthEndpointTests(TestCase):
    """IoT endpoints require X-Device-Token after pairing."""

    def setUp(self):
        self.user = _make_user()
        self.screen = Screen.objects.create(
            name='Auth TV',
            device_id='dev_auth_001',
            owner=self.user,
        )
        self.raw_token = self.screen.issue_device_token()
        self.client = APIClient()

    def _auth_headers(self):
        return {'HTTP_X_DEVICE_TOKEN': self.raw_token}

    def test_heartbeat_with_valid_token(self):
        resp = self.client.post(
            '/iot/screens/heartbeat/',
            data=json.dumps({'screen_id': str(self.screen.id)}),
            content_type='application/json',
            **self._auth_headers(),
        )
        self.assertEqual(resp.status_code, 200)

    def test_heartbeat_without_token_rejected(self):
        resp = self.client.post(
            '/iot/screens/heartbeat/',
            data=json.dumps({'screen_id': str(self.screen.id)}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 401)

    def test_template_with_valid_token(self):
        resp = self.client.get(
            f'/iot/player/template/?screen_id={self.screen.id}',
            **self._auth_headers(),
        )
        self.assertIn(resp.status_code, [200])

    def test_template_without_token_rejected(self):
        resp = self.client.get(f'/iot/player/template/?screen_id={self.screen.id}')
        self.assertEqual(resp.status_code, 401)

    def test_command_pull_without_token_rejected(self):
        resp = self.client.get(f'/iot/commands/pending/?screen_id={self.screen.id}')
        self.assertEqual(resp.status_code, 401)

    def test_revoked_token_rejected(self):
        self.screen.revoke_device_token()
        resp = self.client.post(
            '/iot/screens/heartbeat/',
            data=json.dumps({'screen_id': str(self.screen.id)}),
            content_type='application/json',
            **self._auth_headers(),
        )
        self.assertEqual(resp.status_code, 401)


class RevokeRegenerateTests(TestCase):
    """Dashboard revoke / regenerate actions."""

    def setUp(self):
        self.user = _make_user()
        self.screen = Screen.objects.create(
            name='Revoke TV',
            device_id='dev_revoke_001',
            owner=self.user,
        )
        self.raw_token = self.screen.issue_device_token()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_revoke_invalidates_token(self):
        resp = self.client.post(f'/api/screens/{self.screen.id}/revoke-token/')
        self.assertEqual(resp.status_code, 200)
        self.screen.refresh_from_db()
        self.assertFalse(self.screen.verify_device_token(self.raw_token))

    def test_regenerate_issues_new_token(self):
        resp = self.client.post(f'/api/screens/{self.screen.id}/regenerate-token/')
        self.assertEqual(resp.status_code, 200)
        new_token = resp.json()['device_token']
        self.screen.refresh_from_db()
        self.assertTrue(self.screen.verify_device_token(new_token))
        self.assertFalse(self.screen.verify_device_token(self.raw_token))
