import hashlib
import hmac
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
