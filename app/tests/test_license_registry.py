"""Central license registry (SaaS) and self-hosted gateway client paths."""

import os
from unittest.mock import patch

import pytest
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from licensing.models import LicenseRegistryInstallation, LicenseRegistryPurchase, LicenseState
from licensing.registry_service import (
    activate_installation,
    hash_activation_token,
    purchase_code_fingerprint,
    validate_by_token,
)
from licensing.service import activate_license, validate_license


class RegistryActivateApiTests(TestCase):
    def setUp(self):
        os.environ["PIXELCAST_SIGNAGE_INSTALLED"] = "true"
        self.client = APIClient()

    @override_settings(
        PLATFORM_SAAS_ENABLED=True,
        LICENSE_REGISTRY_API_ENABLED=True,
        CODECANYON_TOKEN="envato-test-token",
        CODECANYON_PRODUCT_ID="12345",
    )
    @patch("licensing.registry_service.fetch_sale_by_purchase_code")
    def test_activate_returns_token(self, mock_sale):
        mock_sale.return_value = {
            "buyer": "codecanyon_user",
            "item": {"id": 12345, "name": "Test Item"},
            "sold_at": "2024-01-01T00:00:00+00:00",
            "license": "Regular License",
        }
        r = self.client.post(
            "/api/license-registry/v1/activate/",
            {
                "purchase_code": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
                "domain": "customer.example.com",
                "product_id": "12345",
                "app_version": "1.0.0",
            },
            format="json",
        )
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertTrue(body.get("valid"))
        self.assertIn("activation_token", body)
        fp = purchase_code_fingerprint("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
        self.assertTrue(LicenseRegistryPurchase.objects.filter(code_fingerprint=fp).exists())
        inst = LicenseRegistryInstallation.objects.get(domain="customer.example.com")
        self.assertEqual(
            inst.token_hash,
            hash_activation_token(body["activation_token"]),
        )

    @override_settings(PLATFORM_SAAS_ENABLED=False, LICENSE_REGISTRY_API_ENABLED=True)
    def test_registry_disabled_returns_404(self):
        r = self.client.post(
            "/api/license-registry/v1/activate/",
            {"purchase_code": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", "domain": "x.com"},
            format="json",
        )
        self.assertEqual(r.status_code, 404)


@override_settings(
    LICENSE_ENFORCEMENT_ENABLED=True,
    LICENSE_OFFLINE_GRACE_HOURS=72,
    LICENSE_CACHE_TTL_SECONDS=1,
    LICENSE_SERVER_URL="https://license.example.test/validate",
    LICENSE_GATEWAY_BASE_URL="",
)
class LicensingGatewayClientTests(TestCase):
    def setUp(self):
        os.environ["PIXELCAST_SIGNAGE_INSTALLED"] = "true"
        LicenseState.objects.all().delete()
        self.state = LicenseState.get_solo()

    @patch("licensing.service.post_license_validation")
    def test_validate_with_activation_token(self, mock_post):
        self.state.activation_token = "secret-test-token"
        self.state.purchase_code = ""
        self.state.activated_domain = "self.example.com"
        self.state.save()

        mock_post.return_value = (True, {"valid": True, "status": "active"})

        decision = validate_license(force=True)
        self.assertTrue(decision.allow)
        mock_post.assert_called_once()
        kwargs = mock_post.call_args.kwargs
        self.assertEqual(kwargs["auth_bearer"], "secret-test-token")
        self.assertIn("validate", kwargs["license_server_url"])


@override_settings(
    LICENSE_ENFORCEMENT_ENABLED=True,
    LICENSE_OFFLINE_GRACE_HOURS=72,
    LICENSE_CACHE_TTL_SECONDS=1,
    LICENSE_GATEWAY_BASE_URL="https://gw.example.com/api/license-registry/v1",
    LICENSE_SERVER_URL="",
    CODECANYON_PRODUCT_ID="999",
)
class LicensingActivateGatewayTests(TestCase):
    def setUp(self):
        os.environ["PIXELCAST_SIGNAGE_INSTALLED"] = "true"
        LicenseState.objects.all().delete()

    @patch("licensing.service.post_gateway_activate")
    @patch("licensing.service.post_license_validation")
    def test_activate_uses_gateway(self, mock_val, mock_act):
        mock_act.return_value = {
            "valid": True,
            "activation_token": "tok-from-gateway",
            "status": "active",
        }
        mock_val.return_value = (True, {"valid": True, "status": "active"})

        decision = activate_license(
            "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            domain="install.example.com",
            override_product_id="",
        )
        self.assertTrue(decision.allow)
        mock_act.assert_called_once()
        state = LicenseState.get_solo()
        self.assertEqual(state.activation_token, "tok-from-gateway")
        self.assertEqual(state.purchase_code, "")


@override_settings(
    PLATFORM_SAAS_ENABLED=True,
    LICENSE_REGISTRY_API_ENABLED=True,
    CODECANYON_TOKEN="x",
    CODECANYON_PRODUCT_ID="1",
)
class ValidateByTokenTests(TestCase):
    @patch("licensing.registry_service.fetch_sale_by_purchase_code")
    def test_suspended_denies(self, mock_sale):
        mock_sale.return_value = {"buyer": "b", "item": {"id": 1}}

        _inst, token, _extra = activate_installation(
            purchase_code="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
            domain="s1.example.com",
            product_id="1",
        )
        inst = LicenseRegistryInstallation.objects.get(domain="s1.example.com")
        inst.suspended = True
        inst.save()

        ok, payload = validate_by_token(token)
        self.assertFalse(ok)
        self.assertIn("suspended", payload.get("status", ""))


@pytest.mark.django_db
def test_platform_self_hosted_licenses_list(superadmin_user):
    os.environ["PIXELCAST_SIGNAGE_INSTALLED"] = "true"
    client = APIClient()
    client.force_authenticate(user=superadmin_user)
    with override_settings(PLATFORM_SAAS_ENABLED=True):
        r = client.get("/api/platform/self-hosted-licenses/")
    assert r.status_code == 200
    assert r.json().get("results") == []
