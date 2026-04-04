import logging
from django.conf import settings
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

from .service import validate_license

logger = logging.getLogger(__name__)


class LicenseEnforcementMiddleware(MiddlewareMixin):
    EXEMPT_PREFIXES = (
        "/api/setup/",
        "/api/auth/login/",
        "/api/auth/signup/",
        "/api/auth/token/",
        "/api/auth/token/refresh/",
        "/api/license/",
        "/api/license-registry/",
        "/api/schema/",
        "/api/docs/",
        "/api/redoc/",
    )

    def process_request(self, request):
        if not bool(getattr(settings, "LICENSE_ENFORCEMENT_ENABLED", False)):
            return None

        path = request.path
        if not path.startswith("/api/"):
            return None

        if any(path.startswith(prefix) for prefix in self.EXEMPT_PREFIXES):
            return None

        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            # Enforcement begins after authentication for protected API use.
            return None

        decision = validate_license(force=False)
        if decision.allow:
            if decision.status == "grace":
                request.META["HTTP_X_LICENSE_STATUS"] = "grace"
            return None

        logger.warning(
            "License denied request path=%s user=%s status=%s",
            path,
            getattr(user, "id", None),
            decision.status,
        )

        return JsonResponse(
            {
                "error": decision.error_code or "license_invalid",
                "message": decision.message,
                "license_status": decision.status,
                "grace_until": decision.grace_until.isoformat()
                if decision.grace_until
                else None,
            },
            status=403,
        )
