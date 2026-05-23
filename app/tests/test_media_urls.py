"""Tests for public media URL resolution."""
from django.test import RequestFactory, TestCase, override_settings

from core.media_urls import resolve_public_media_url


@override_settings(
    BASE_URL='https://pixelcast.uk',
    PUBLIC_WEB_APP_URL='https://pixelcast.uk',
    MEDIA_URL='/media/',
)
class ResolvePublicMediaUrlTests(TestCase):
    def test_relative_path_uses_public_origin(self):
        url = resolve_public_media_url('/media/users/1/test.jpg')
        self.assertEqual(url, 'https://pixelcast.uk/media/users/1/test.jpg')

    def test_internal_backend_host_rewritten(self):
        url = resolve_public_media_url('http://backend:8000/media/users/1/test.jpg')
        self.assertEqual(url, 'https://pixelcast.uk/media/users/1/test.jpg')

    def test_request_host_used_when_set(self):
        factory = RequestFactory()
        request = factory.get('/', HTTP_HOST='pixelcast.uk', HTTP_X_FORWARDED_PROTO='https')
        url = resolve_public_media_url('/media/x.jpg', request=request)
        self.assertEqual(url, 'https://pixelcast.uk/media/x.jpg')
