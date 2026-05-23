from django.core.management.base import BaseCommand
from django.db import transaction

from templates.models import Content


class Command(BaseCommand):
    help = "Audit Content rows for missing file_url/storage_path and optionally repair file_url from storage_path."

    def add_arguments(self, parser):
        parser.add_argument(
            "--content-id",
            type=str,
            default=None,
            help="Audit only a specific Content UUID.",
        )
        parser.add_argument(
            "--fix",
            action="store_true",
            help="Fill missing file_url from storage_path when possible.",
        )

    def handle(self, *args, **options):
        content_id = options.get("content_id")
        apply_fix = bool(options.get("fix"))

        queryset = Content.objects.all().order_by("created_at")
        if content_id:
            queryset = queryset.filter(id=content_id)

        total = 0
        problematic = 0
        fixed = 0

        for item in queryset.iterator():
            total += 1
            file_url = (item.file_url or "").strip()
            storage_path = (item.storage_path or "").strip()

            if file_url and storage_path:
                continue
            if item.type not in {"image", "video", "webview"}:
                continue

            problematic += 1
            self.stdout.write(
                f"[problem] id={item.id} type={item.type} file_url={bool(file_url)} storage_path={bool(storage_path)}"
            )

            if not apply_fix or file_url or not storage_path:
                continue

            normalized_storage_path = storage_path.replace("\\", "/").strip("/")
            repaired_url = f"/media/{normalized_storage_path}"
            with transaction.atomic():
                item.file_url = repaired_url
                item.save(update_fields=["file_url", "updated_at"])
            fixed += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"[fixed] id={item.id} file_url set from storage_path -> {repaired_url}"
                )
            )

        self.stdout.write(
            self.style.NOTICE(
                f"Audit completed: total={total}, problematic={problematic}, fixed={fixed}, fix_mode={apply_fix}"
            )
        )
