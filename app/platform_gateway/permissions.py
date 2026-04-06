from __future__ import annotations

from rest_framework.permissions import BasePermission

from .models import InstanceRegistry
from .utils import hash_api_key


class IsValidInstance(BasePermission):
    """
    Requires header X-Instance-Key matching a registered instance (hashed in DB).
    Sets request.gateway_instance on success.
    """

    def has_permission(self, request, view):
        raw = request.headers.get("X-Instance-Key") or request.headers.get("x-instance-key")
        if not raw or not str(raw).strip():
            return False
        digest = hash_api_key(str(raw).strip())
        inst = (
            InstanceRegistry.objects.filter(
                api_key_hash=digest,
                license_status=InstanceRegistry.STATUS_ACTIVE,
            )
            .only("id", "domain", "license_status", "api_key_hash")
            .first()
        )
        if not inst:
            return False
        request.gateway_instance = inst
        return True
