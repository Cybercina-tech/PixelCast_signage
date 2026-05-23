from django.core.management.base import BaseCommand

from commands.realtime_metrics import snapshot_metrics, set_metric


class Command(BaseCommand):
    help = "Show (and optionally reset) dashboard realtime WebSocket metrics."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Reset all realtime metric counters to zero after printing.",
        )

    def handle(self, *args, **options):
        metrics = snapshot_metrics()
        self.stdout.write(self.style.NOTICE("Realtime metrics snapshot:"))
        for key, value in metrics.items():
            self.stdout.write(f"  - {key}: {value}")

        if options.get("reset"):
            for key in metrics.keys():
                set_metric(key, 0)
            self.stdout.write(self.style.SUCCESS("Realtime metrics counters reset to zero."))
