"""platform_gateway public + admin API."""

import os
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import User
from platform_gateway.models import InstanceRegistry
from platform_gateway.utils import hash_api_key


@override_settings(
    PLATFORM_SAAS_ENABLED=True,
    PLATFORM_GATEWAY_ENABLED=True,
    CODECANYON_TOKEN="envato-test-token",
    CODECANYON_PRODUCT_ID="12345",
    GATEWAY_REGISTER_RATE_LIMIT_PER_HOUR=5,
)
class GatewayRegisterTests(TestCase):
    def setUp(self):
        os.environ["PIXELCAST_SIGNAGE_INSTALLED"] = "true"
        self.client = APIClient()

    @patch("platform_gateway.services.fetch_sale_by_purchase_code")
    def test_register_creates_instance_and_returns_key_once(self, mock_sale):
        mock_sale.return_value = {
            "buyer": "u1",
            "item": {"id": 12345},
            "sold_at": "2024-01-01T00:00:00+00:00",
        }
        r = self.client.post(
            "/api/gateway/register-instance/",
            {
                "purchase_code": "aaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
                "domain": "https://one.example.com",
                "version": "1.0.0",
            },
            format="json",
        )
        self.assertEqual(r.status_code, 201, r.content)
        body = r.json()
        self.assertEqual(body.get("status"), "registered")
        self.assertIn("api_key", body)
        self.assertTrue(InstanceRegistry.objects.filter(id=body["instance_id"]).exists())
        inst = InstanceRegistry.objects.get(id=body["instance_id"])
        self.assertEqual(inst.api_key_hash, hash_api_key(body["api_key"]))

    @patch("platform_gateway.services.fetch_sale_by_purchase_code")
    def test_register_duplicate_returns_409(self, mock_sale):
        mock_sale.return_value = {"item": {"id": 12345}, "sold_at": "2024-01-01T00:00:00+00:00"}
        payload = {
            "purchase_code": "dup-dup-dup-dup-dupdupdupdup",
            "domain": "https://dup.example.com",
            "version": "1.0.0",
        }
        r1 = self.client.post("/api/gateway/register-instance/", payload, format="json")
        self.assertEqual(r1.status_code, 201)
        r2 = self.client.post("/api/gateway/register-instance/", payload, format="json")
        self.assertEqual(r2.status_code, 409)
        self.assertNotIn("api_key", r2.json())

    @patch("platform_gateway.services.fetch_sale_by_purchase_code")
    def test_register_rate_limit_429_after_limit(self, mock_sale):
        mock_sale.return_value = {"item": {"id": 12345}, "sold_at": "2024-01-01T00:00:00+00:00"}
        cache.clear()
        for i in range(5):
            r = self.client.post(
                "/api/gateway/register-instance/",
                {
                    "purchase_code": f"code-{i}-bbbb-cccc-dddd-eeeeeeeeeeee",
                    "domain": f"https://t{i}.example.com",
                    "version": "1.0.0",
                },
                format="json",
            )
            self.assertEqual(r.status_code, 201, (i, r.content))
        r6 = self.client.post(
            "/api/gateway/register-instance/",
            {
                "purchase_code": "code-5-bbbb-cccc-dddd-eeeeeeeeeeee",
                "domain": "https://t5.example.com",
                "version": "1.0.0",
            },
            format="json",
        )
        self.assertEqual(r6.status_code, 429)


@override_settings(
    PLATFORM_SAAS_ENABLED=True,
    PLATFORM_GATEWAY_ENABLED=True,
)
class GatewayInstanceApiTests(TestCase):
    def setUp(self):
        os.environ["PIXELCAST_SIGNAGE_INSTALLED"] = "true"
        self.client = APIClient()
        raw = "test-secret-instance-key-raw"
        self.inst = InstanceRegistry.objects.create(
            purchase_code_fingerprint="a" * 64,
            domain="https://gw.example.com",
            api_key_hash=hash_api_key(raw),
            license_status=InstanceRegistry.STATUS_ACTIVE,
        )
        self.api_key = raw

    def test_heartbeat_updates_online(self):
        r = self.client.post(
            "/api/gateway/heartbeat/",
            {"version": "1.2.3", "status": "ok"},
            HTTP_X_INSTANCE_KEY=self.api_key,
            format="json",
        )
        self.assertEqual(r.status_code, 200)
        self.inst.refresh_from_db()
        self.assertTrue(self.inst.is_online)
        self.assertEqual(self.inst.version, "1.2.3")

    def test_usage_reported_at_future_rejected(self):
        future = timezone.now() + timezone.timedelta(hours=1)
        r = self.client.post(
            "/api/gateway/usage-report/",
            {
                "active_screens": 1,
                "templates_count": 2,
                "storage_used_mb": 0,
                "commands_sent": 0,
                "users_count": 0,
                "reported_at": future.isoformat(),
            },
            HTTP_X_INSTANCE_KEY=self.api_key,
            format="json",
        )
        self.assertEqual(r.status_code, 400)

    def test_usage_ok(self):
        now = timezone.now()
        r = self.client.post(
            "/api/gateway/usage-report/",
            {
                "active_screens": 3,
                "templates_count": 1,
                "storage_used_mb": 10.5,
                "commands_sent": 0,
                "users_count": 2,
                "reported_at": now.isoformat(),
            },
            HTTP_X_INSTANCE_KEY=self.api_key,
            format="json",
        )
        self.assertEqual(r.status_code, 201)


@override_settings(
    PLATFORM_SAAS_ENABLED=True,
    PLATFORM_GATEWAY_ENABLED=True,
)
class GatewayAdminApiTests(TestCase):
    def setUp(self):
        os.environ["PIXELCAST_SIGNAGE_INSTALLED"] = "true"
        self.client = APIClient()
        InstanceRegistry.objects.create(
            purchase_code_fingerprint="b" * 64,
            domain="https://admin-gw.example.com",
            api_key_hash=hash_api_key("k"),
            license_status=InstanceRegistry.STATUS_ACTIVE,
        )

    def test_instances_list_requires_developer(self):
        r = self.client.get("/api/platform/gateway/instances/")
        self.assertIn(r.status_code, (401, 403))

    def test_instances_list_as_developer(self):
        u = User.objects.create_user(
            username="gwdev",
            email="gwdev@test.com",
            password="x",
            role="Developer",
        )
        self.client.force_authenticate(user=u)
        r = self.client.get("/api/platform/gateway/instances/")
        self.assertEqual(r.status_code, 200)
        self.assertGreaterEqual(r.json().get("count", 0), 1)
