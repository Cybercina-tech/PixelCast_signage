import hashlib
import hmac
import uuid
from datetime import timedelta
from django.conf import settings
from django.db import models
from django.utils import timezone


class LicenseState(models.Model):
    STATUS_INACTIVE = "inactive"
    STATUS_ACTIVE = "active"
    STATUS_INVALID = "invalid"
    STATUS_GRACE = "grace"

    STATUS_CHOICES = [
        (STATUS_INACTIVE, "Inactive"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_INVALID, "Invalid"),
        (STATUS_GRACE, "Grace"),
    ]

    purchase_code = models.CharField(max_length=128, blank=True, default="")
    activated_domain = models.CharField(max_length=255, blank=True, default="")
    activated_at = models.DateTimeField(null=True, blank=True)

    license_status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_INACTIVE, db_index=True
    )
    last_validation_at = models.DateTimeField(null=True, blank=True)
    last_successful_validation_at = models.DateTimeField(null=True, blank=True)
    grace_until = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True, default="")

    codecanyon_product_id_override = models.CharField(max_length=64, blank=True, default="")
    validation_signature = models.CharField(max_length=128, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "licensing_state"
        verbose_name = "License State"
        verbose_name_plural = "License State"

    def __str__(self):
        return f"LicenseState(status={self.license_status}, domain={self.activated_domain or 'n/a'})"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def masked_purchase_code(self) -> str:
        code = (self.purchase_code or "").strip()
        if len(code) <= 8:
            return "*" * len(code)
        return f"{code[:4]}...{code[-4:]}"

    def recompute_signature(self) -> str:
        payload = "|".join(
            [
                self.purchase_code or "",
                self.activated_domain or "",
                self.license_status or "",
                str(int(self.last_successful_validation_at.timestamp()))
                if self.last_successful_validation_at
                else "0",
                self.codecanyon_product_id_override or "",
            ]
        )
        digest = hmac.new(
            key=settings.SECRET_KEY.encode("utf-8"),
            msg=payload.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()
        return digest

    def touch_signature(self):
        self.validation_signature = self.recompute_signature()

    def set_grace_window(self, grace_hours: int):
        self.grace_until = timezone.now() + timedelta(hours=max(0, int(grace_hours)))


class TenantLicenseState(models.Model):
    """Per-tenant license state for multi-tenant SaaS deployments."""

    STATUS_CHOICES = LicenseState.STATUS_CHOICES

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.OneToOneField(
        'saas_platform.Tenant', on_delete=models.CASCADE,
        related_name='license_state',
    )
    license_key = models.CharField(max_length=128, blank=True, default="")
    license_status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="inactive", db_index=True,
    )
    activated_at = models.DateTimeField(null=True, blank=True)
    last_validation_at = models.DateTimeField(null=True, blank=True)
    grace_until = models.DateTimeField(null=True, blank=True)
    offline_grace_hours = models.PositiveIntegerField(
        default=72, help_text="Hours allowed offline before enforcement",
    )
    last_error = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "licensing_tenant_state"
        verbose_name = "Tenant License State"

    def __str__(self):
        return f"TenantLicense(tenant={self.tenant_id}, status={self.license_status})"

    def set_grace_window(self):
        self.grace_until = timezone.now() + timedelta(hours=max(0, self.offline_grace_hours))

    def is_entitled(self):
        if self.license_status == "active":
            return True
        if self.license_status == "grace" and self.grace_until and self.grace_until > timezone.now():
            return True
        return False


class LicenseEnforcementLog(models.Model):
    """Immutable log of license enforcement decisions."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        'saas_platform.Tenant', on_delete=models.CASCADE,
        related_name='license_enforcement_logs', null=True, blank=True,
    )
    action = models.CharField(max_length=64, db_index=True)
    decision = models.CharField(max_length=32)
    details = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "licensing_enforcement_log"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'created_at']),
        ]

    def __str__(self):
        return f"EnforcementLog({self.action}, {self.decision})"
