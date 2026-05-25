"""Tests for email verification during login/signup (SMTP-backed)."""

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    REQUIRE_EMAIL_VERIFICATION=True,
    ENABLE_TWO_FACTOR_AUTH=False,
)
class EmailVerificationAuthFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='verify@test.com',
            email='verify@test.com',
            password='SecurePass123!',
            role='Employee',
            organization_name='TestOrg',
        )
        self.user.is_email_verified = False
        self.user.save(update_fields=['is_email_verified'])

    def test_login_requires_email_verification(self):
        r = self.client.post(
            '/api/auth/login/',
            {'username': 'verify@test.com', 'password': 'SecurePass123!'},
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['status'], 'email_verification_required')
        self.assertIn('verification_token', r.data)
        self.assertNotIn('tokens', r.data)

    def test_send_and_confirm_verification(self):
        login = self.client.post(
            '/api/auth/login/',
            {'username': 'verify@test.com', 'password': 'SecurePass123!'},
            format='json',
        )
        token = login.data['verification_token']

        send = self.client.post(
            '/api/auth/email-verification/send/',
            {'verification_token': token},
            format='json',
        )
        self.assertEqual(send.status_code, 200)
        self.assertEqual(send.data['status'], 'success')

        self.user.refresh_from_db()
        code = self.user.verification_code
        self.assertTrue(code)

        confirm = self.client.post(
            '/api/auth/email-verification/confirm/',
            {'verification_token': token, 'code': code},
            format='json',
        )
        self.assertEqual(confirm.status_code, 200)
        self.assertEqual(confirm.data['status'], 'success')
        self.assertIn('tokens', confirm.data)

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_email_verified)

    def test_signup_returns_verification_required(self):
        r = self.client.post(
            '/api/auth/signup/',
            {
                'username': 'newuser@test.com',
                'email': 'newuser@test.com',
                'password': 'SecurePass123!',
                'password_confirm': 'SecurePass123!',
                'full_name': 'New User',
            },
            format='json',
        )
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data['status'], 'email_verification_required')
        self.assertIn('verification_token', r.data)
        self.assertNotIn('tokens', r.data)

    @override_settings(REQUIRE_EMAIL_VERIFICATION=False)
    def test_login_skips_verification_when_disabled(self):
        r = self.client.post(
            '/api/auth/login/',
            {'username': 'verify@test.com', 'password': 'SecurePass123!'},
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['status'], 'success')
        self.assertIn('tokens', r.data)

    def test_invalid_verification_token(self):
        r = self.client.post(
            '/api/auth/email-verification/confirm/',
            {'verification_token': 'bad', 'code': '123456'},
            format='json',
        )
        self.assertEqual(r.status_code, 400)
