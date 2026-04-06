from __future__ import annotations

import logging
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from .models import InstanceRegistry

logger = logging.getLogger(__name__)


@shared_task(name="platform_gateway.tasks.check_offline_instances")
def check_offline_instances():
    """
    Mark instances offline when heartbeat is older than threshold.
    """
    minutes = int(getattr(settings, "GATEWAY_OFFLINE_HEARTBEAT_MINUTES", 3) or 3)
    threshold = timezone.now() - timedelta(minutes=max(1, minutes))
    qs = InstanceRegistry.objects.filter(is_online=True).filter(
        Q(last_heartbeat_at__lt=threshold) | Q(last_heartbeat_at__isnull=True)
    )

    updated = 0
    for inst in qs.iterator():
        inst.is_online = False
        inst.save(update_fields=["is_online"])
        updated += 1
    if updated:
        logger.info("platform_gateway: marked %s instances offline (heartbeat stale)", updated)
    return updated
