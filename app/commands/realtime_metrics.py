"""
Lightweight realtime metrics backed by Django cache.

These counters are intentionally simple and dependency-free so they can run
in local and self-hosted deployments without introducing Prometheus/StatsD.
"""

from django.core.cache import cache


METRIC_KEYS = {
    "dashboard_ws_active_connections": 0,
    "dashboard_ws_connect_success_total": 0,
    "dashboard_ws_connect_rejected_total": 0,
    "dashboard_ws_auth_rejected_total": 0,
    "dashboard_ws_rate_limited_total": 0,
}


def _cache_key(name):
    return f"realtime_metric:{name}"


def increment_metric(name, delta=1):
    key = _cache_key(name)
    try:
        cache.add(key, 0, None)
        if delta >= 0:
            cache.incr(key, delta)
        else:
            current = cache.get(key, 0)
            next_value = max(0, int(current) + int(delta))
            cache.set(key, next_value, None)
    except Exception:
        current = cache.get(key, 0)
        cache.set(key, max(0, int(current) + int(delta)), None)


def set_metric(name, value):
    cache.set(_cache_key(name), int(value), None)


def get_metric(name):
    if name not in METRIC_KEYS:
        return 0
    return int(cache.get(_cache_key(name), METRIC_KEYS[name]) or 0)


def snapshot_metrics():
    return {name: get_metric(name) for name in METRIC_KEYS}
