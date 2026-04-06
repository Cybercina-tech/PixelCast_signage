from __future__ import annotations

import logging

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.rate_limiting import RateLimiter
from licensing.envato import EnvatoApiError

from .models import GatewayRegistrationAttempt, InstanceHeartbeat, InstanceUsageLog
from .permissions import IsValidInstance
from .serializers import (
    GatewayTicketSerializer,
    HeartbeatSerializer,
    RegisterInstanceSerializer,
    UsageReportSerializer,
)
from .services import gateway_public_enabled, register_new_instance

logger = logging.getLogger(__name__)


def _client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "") or None


def _log_attempt(*, request, fingerprint: str, outcome: str, http_status: int, detail: str = ""):
    GatewayRegistrationAttempt.objects.create(
        ip_address=_client_ip(request),
        purchase_code_fingerprint=fingerprint,
        outcome=outcome,
        http_status=http_status,
        detail=(detail or "")[:255],
    )


class RegisterInstanceView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        if not gateway_public_enabled():
            return Response(
                {"detail": "Platform gateway is not enabled."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        lim_hour = int(getattr(settings, "GATEWAY_REGISTER_RATE_LIMIT_PER_HOUR", 5) or 5)
        allowed, remaining = RateLimiter.check_rate_limit(
            request,
            endpoint="gateway_register",
            strategy=RateLimiter.STRATEGY_IP,
            limit_per_minute=10_000,
            limit_per_hour=lim_hour,
            limit_per_day=1_000_000,
        )
        if not allowed:
            headers = RateLimiter.get_rate_limit_headers(
                remaining,
                {"minute": 10_000, "hour": lim_hour, "day": 1_000_000},
            )
            return Response(
                {"detail": "Too many registration attempts from this IP; try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
                headers=headers,
            )

        ser = RegisterInstanceSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        purchase_code = ser.validated_data["purchase_code"]
        domain = ser.validated_data["domain"]
        version = ser.validated_data.get("version") or ""

        from licensing.registry_service import purchase_code_fingerprint

        fp = purchase_code_fingerprint(purchase_code)

        try:
            outcome, inst, raw_key = register_new_instance(
                purchase_code=purchase_code,
                domain=domain,
                version=version,
                client_ip=_client_ip(request),
            )
        except EnvatoApiError as exc:
            code = getattr(exc, "status_code", None) or 502
            drf_status = status.HTTP_502_BAD_GATEWAY
            if code == 400:
                drf_status = status.HTTP_400_BAD_REQUEST
            elif code == 403:
                drf_status = status.HTTP_403_FORBIDDEN
            elif code == 404:
                drf_status = status.HTTP_404_NOT_FOUND
            elif code == 429:
                drf_status = status.HTTP_429_TOO_MANY_REQUESTS
            _log_attempt(
                request=request,
                fingerprint=fp,
                outcome="envato_error",
                http_status=drf_status,
                detail=str(exc)[:200],
            )
            return Response({"detail": str(exc)}, status=drf_status)
        except ValueError as exc:
            _log_attempt(
                request=request,
                fingerprint=fp,
                outcome="validation_error",
                http_status=400,
                detail=str(exc),
            )
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        if outcome == "conflict":
            _log_attempt(
                request=request,
                fingerprint=fp,
                outcome="conflict",
                http_status=409,
            )
            return Response(
                {
                    "detail": (
                        "This purchase is already registered. Use your existing API key on the instance. "
                        "To rotate the key, use the operator key-rotation flow when available."
                    ),
                    "instance_id": str(inst.id),
                },
                status=status.HTTP_409_CONFLICT,
            )

        _log_attempt(
            request=request,
            fingerprint=fp,
            outcome="created",
            http_status=201,
        )
        return Response(
            {
                "instance_id": str(inst.id),
                "api_key": raw_key,
                "status": "registered",
            },
            status=status.HTTP_201_CREATED,
        )


class HeartbeatView(APIView):
    authentication_classes = []
    permission_classes = [IsValidInstance]

    def post(self, request):
        if not gateway_public_enabled():
            return Response(
                {"detail": "Platform gateway is not enabled."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        ser = HeartbeatSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        inst = request.gateway_instance
        ip = _client_ip(request)
        ver = (ser.validated_data.get("version") or "")[:20]
        st = (ser.validated_data.get("status") or "ok")[:50]

        from django.utils import timezone

        now = timezone.now()
        inst.last_heartbeat_at = now
        inst.is_online = True
        inst.ip_address = ip
        if ver:
            inst.version = ver
        inst.save(update_fields=["last_heartbeat_at", "is_online", "ip_address", "version"])

        InstanceHeartbeat.objects.create(
            instance=inst,
            version=ver,
            status=st,
            ip_address=ip,
        )
        return Response({"status": "ok"}, status=status.HTTP_200_OK)


class UsageReportView(APIView):
    authentication_classes = []
    permission_classes = [IsValidInstance]

    def post(self, request):
        if not gateway_public_enabled():
            return Response(
                {"detail": "Platform gateway is not enabled."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        ser = UsageReportSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        inst = request.gateway_instance
        d = ser.validated_data
        InstanceUsageLog.objects.create(
            instance=inst,
            reported_at=d["reported_at"],
            active_screens=d["active_screens"],
            templates_count=d["templates_count"],
            storage_used_mb=d["storage_used_mb"],
            commands_sent=d["commands_sent"],
            users_count=d["users_count"],
            extra_data={},
        )
        return Response({"status": "ok"}, status=status.HTTP_201_CREATED)


def _instance_feature_allowed(inst, feature: str) -> bool:
    """
    CodeCanyon instances default to denied for saas_mode.
    Set InstanceRegistry.metadata["saas_mode_entitled"] = true for licensed SaaS deployments.
    """
    feature = (feature or "").strip()
    if feature != "saas_mode":
        return False
    meta = inst.metadata or {}
    if meta.get("saas_mode_entitled") is True:
        return True
    ent = meta.get("entitlements") or {}
    if isinstance(ent, dict) and ent.get("saas_mode") is True:
        return True
    return False


class FeatureCheckView(APIView):
    """POST /api/gateway/feature-check/ — instance asks whether a feature is entitled."""

    authentication_classes = []
    permission_classes = [IsValidInstance]

    def post(self, request):
        if not gateway_public_enabled():
            return Response(
                {"detail": "Platform gateway is not enabled."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        feature = (request.data or {}).get("feature")
        if not feature or not str(feature).strip():
            return Response({"detail": "feature is required."}, status=status.HTTP_400_BAD_REQUEST)
        inst = request.gateway_instance
        allowed = _instance_feature_allowed(inst, str(feature).strip())
        return Response({"allowed": bool(allowed)}, status=status.HTTP_200_OK)


class TicketForwardView(APIView):
    authentication_classes = []
    permission_classes = [IsValidInstance]

    def post(self, request):
        if not gateway_public_enabled():
            return Response(
                {"detail": "Platform gateway is not enabled."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        ser = GatewayTicketSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        import uuid

        from tickets.services import ingest_gateway_ticket

        inst = request.gateway_instance
        d = ser.validated_data
        remote_id = d.get("remote_ticket_id") or uuid.uuid4()
        try:
            ticket, event = ingest_gateway_ticket(
                inst,
                remote_id,
                d["body"],
                subject=d["subject"],
                priority=d["priority"],
                requester_email=(d.get("customer_email") or "").strip(),
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "ticket_id": str(ticket.id),
                "event": event,
            },
            status=status.HTTP_201_CREATED if event == "created" else status.HTTP_200_OK,
        )
