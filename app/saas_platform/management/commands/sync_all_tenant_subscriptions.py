"""Sync all tenant subscriptions from Stripe into Tenant + UserSubscription snapshots."""

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from saas_platform.models import Tenant
from saas_platform.services import fetch_stripe_subscription, sync_tenant_from_stripe_subscription


class Command(BaseCommand):
    help = "One-time sync of tenant subscriptions from Stripe"

    def add_arguments(self, parser):
        parser.add_argument(
            "--tenant-id",
            type=str,
            help="Optional tenant UUID to sync only one tenant",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Only report what would be synced",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Max tenants to process (0 means all)",
        )
        parser.add_argument(
            "--continue-on-error",
            dest="continue_on_error",
            action="store_true",
            default=True,
            help="Continue processing when one tenant fails (default: true)",
        )
        parser.add_argument(
            "--no-continue-on-error",
            dest="continue_on_error",
            action="store_false",
            help="Stop immediately on first error",
        )

    def handle(self, *args, **options):
        tenant_id = (options.get("tenant_id") or "").strip()
        dry_run = bool(options.get("dry_run"))
        limit = int(options.get("limit") or 0)
        continue_on_error = bool(options.get("continue_on_error"))

        qs = Tenant.objects.exclude(stripe_subscription_id="").order_by("name")
        if tenant_id:
            qs = qs.filter(pk=tenant_id)
        if limit > 0:
            qs = qs[:limit]

        processed = 0
        synced = 0
        skipped = 0
        failed = 0

        self.stdout.write("Starting tenant subscription sync...")
        for tenant in qs:
            processed += 1
            subscription_id = (tenant.stripe_subscription_id or "").strip()
            if not subscription_id:
                skipped += 1
                self.stdout.write(self.style.WARNING(f"SKIP {tenant.slug}: no stripe_subscription_id"))
                continue

            sub = fetch_stripe_subscription(subscription_id)
            if not sub:
                failed += 1
                msg = f"FAIL {tenant.slug}: could not fetch subscription {subscription_id}"
                self.stderr.write(self.style.ERROR(msg))
                if not continue_on_error:
                    raise CommandError(msg)
                continue

            if dry_run:
                plan_label = ""
                items = (sub.get("items") or {}).get("data") or []
                if items and isinstance(items[0], dict):
                    plan_label = ((items[0].get("price") or {}).get("nickname") or "")
                self.stdout.write(
                    self.style.WARNING(
                        f"DRY-RUN {tenant.slug}: status={sub.get('status') or 'none'} plan={plan_label or '-'}"
                    )
                )
                synced += 1
                continue

            try:
                sync_tenant_from_stripe_subscription(tenant, sub)
                synced += 1
                self.stdout.write(self.style.SUCCESS(f"OK {tenant.slug}: synced"))
            except Exception as exc:  # noqa: BLE001
                failed += 1
                msg = f"FAIL {tenant.slug}: {exc}"
                self.stderr.write(self.style.ERROR(msg))
                if not continue_on_error:
                    raise CommandError(msg) from exc

        self.stdout.write(
            self.style.SUCCESS(
                f"Summary processed={processed} synced={synced} skipped={skipped} failed={failed}"
            )
        )
        if failed and synced == 0 and not dry_run:
            raise CommandError("All sync operations failed.")
