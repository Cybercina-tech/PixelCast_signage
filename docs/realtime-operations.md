# Realtime Operations Baseline

## Core counters

Run:

`python manage.py realtime_metrics_report`

Track these counters over time:

- `dashboard_ws_connect_success_total`
- `dashboard_ws_connect_rejected_total`
- `dashboard_ws_auth_rejected_total`
- `dashboard_ws_rate_limited_total`
- `dashboard_ws_active_connections`

## Suggested alert thresholds

- `dashboard_ws_auth_rejected_total` growth spike (> 20/min): likely stale/expired token loop.
- `dashboard_ws_rate_limited_total` growth (> 10/min): likely reconnect storm or abusive client.
- `dashboard_ws_connect_rejected_total / dashboard_ws_connect_success_total > 0.2`: degraded auth/network behavior.
- `dashboard_ws_active_connections` sudden drop to zero during active hours: channel layer/network outage.

## Load probe

Use the synthetic probe script before/after changes:

`python scripts/loadtest_dashboard_ws.py --url ws://localhost:8000/ws/dashboard/ --token <ACCESS_JWT> --clients 20 --seconds 30`

Compare:

- connection success ratio
- failed connections
- message throughput
