"""Platform operator overview aggregates (Super Admin dashboard)."""

from __future__ import annotations

import calendar
from collections import Counter
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from notifications.models import NotificationLog
from accounts.jwt_sessions import active_session_stats_by_tenant

from .models import PlatformExpense, Tenant, TenantInvoice
from .permissions import IsDeveloper
from .usage import billing_alerts_for_tenant, tenant_health_score


def _add_months(dt, months_delta: int):
    """Add calendar months to an aware/datetime (month-aligned safe)."""
    month = dt.month - 1 + months_delta
    year = dt.year + month // 12
    month = month % 12 + 1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)


def _saas_enabled() -> bool:
    return bool(getattr(settings, 'PLATFORM_SAAS_ENABLED', False))


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDeveloper])
def platform_overview(request):
    """KPIs, health distribution, and chart-friendly aggregates for the Super Admin overview."""
    if not _saas_enabled():
        return Response(
            {'detail': 'Platform SaaS features are disabled (set PLATFORM_SAAS_ENABLED=true).'},
            status=status.HTTP_403_FORBIDDEN,
        )

    now = timezone.now()
    start_12m = now - timedelta(days=366)

    tenants = list(Tenant.objects.all())
    total = len(tenants)

    status_counts = Counter(t.subscription_status for t in tenants)

    paying = sum(
        1
        for t in tenants
        if t.subscription_status in ('active', 'trialing')
        and (t.stripe_subscription_id or '').strip()
    )

    trials = sum(1 for t in tenants if t.subscription_status == 'trialing')
    churn_risk_high = 0
    payment_failed_any = sum(1 for t in tenants if t.last_payment_failed_at)

    health_scores = []
    health_buckets = {'0-20': 0, '21-40': 0, '41-60': 0, '61-80': 0, '81-100': 0}
    for t in tenants:
        th = tenant_health_score(t)
        hs = th['score']
        if th.get('churn_risk_level') == 'high':
            churn_risk_high += 1
        health_scores.append(hs)
        if hs <= 20:
            health_buckets['0-20'] += 1
        elif hs <= 40:
            health_buckets['21-40'] += 1
        elif hs <= 60:
            health_buckets['41-60'] += 1
        elif hs <= 80:
            health_buckets['61-80'] += 1
        else:
            health_buckets['81-100'] += 1

    avg_health = round(sum(health_scores) / len(health_scores), 1) if health_scores else 0.0

    # Rolling 30d paid invoice total as revenue proxy (cents)
    since_30d = now - timedelta(days=30)
    rev_agg = TenantInvoice.objects.filter(created_at__gte=since_30d, amount_paid__gt=0).aggregate(
        s=Sum('amount_paid')
    )
    revenue_30d_cents = int(rev_agg['s'] or 0)
    mrr_estimate_cents = revenue_30d_cents
    arr_estimate_cents = mrr_estimate_cents * 12

    # Revenue by month (paid invoices, last 12 months)
    revenue_rows = (
        TenantInvoice.objects.filter(created_at__gte=start_12m, amount_paid__gt=0)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(amount_cents=Sum('amount_paid'))
        .order_by('month')
    )
    revenue_by_month = [
        {'month': row['month'].strftime('%Y-%m') if row['month'] else '', 'amount_cents': int(row['amount_cents'] or 0)}
        for row in revenue_rows
    ]

    expense_rows = (
        PlatformExpense.objects.filter(spent_on__gte=start_12m.date())
        .annotate(month=TruncMonth('spent_on'))
        .values('month')
        .annotate(amount_cents=Sum('amount_cents'))
        .order_by('month')
    )
    expenses_by_month = [
        {'month': row['month'].strftime('%Y-%m') if row['month'] else '', 'amount_cents': int(row['amount_cents'] or 0)}
        for row in expense_rows
    ]

    expense_30d_agg = PlatformExpense.objects.filter(spent_on__gte=since_30d.date()).aggregate(s=Sum('amount_cents'))
    expense_last_30d_cents = int(expense_30d_agg['s'] or 0)

    expense_categories = (
        PlatformExpense.objects.values('category')
        .annotate(amount_cents=Sum('amount_cents'), count=Count('id'))
        .order_by('-amount_cents')
    )
    expense_by_category = [
        {
            'category': row['category'],
            'amount_cents': int(row['amount_cents'] or 0),
            'count': int(row['count'] or 0),
        }
        for row in expense_categories
    ]

    # Signups by month (last 12 months)
    signup_rows = (
        Tenant.objects.filter(created_at__gte=start_12m)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    signups_by_month = [
        {'month': row['month'].strftime('%Y-%m') if row['month'] else '', 'count': row['count']}
        for row in signup_rows
    ]

    # Plan distribution (non-empty plan names)
    plan_counts = Counter(((t.plan_name or '').strip() or 'unknown') for t in tenants)
    plan_distribution = [{'plan': k, 'count': v} for k, v in plan_counts.most_common(20)]

    # Immediate alerts rollup (derived)
    alert_rollup = Counter()
    for t in tenants:
        for a in billing_alerts_for_tenant(t):
            alert_rollup[a] += 1

    return Response(
        {
            'generated_at': now.isoformat(),
            'counts': {
                'tenants': total,
                'by_subscription_status': dict(status_counts),
                'paying_with_subscription': paying,
                'trialing': trials,
                'with_payment_failure_flag': payment_failed_any,
                'churn_risk_high': churn_risk_high,
            },
            'revenue': {
                'mrr_estimate_cents': mrr_estimate_cents,
                'arr_estimate_cents': arr_estimate_cents,
                'revenue_last_30d_cents': revenue_30d_cents,
                'expenses_last_30d_cents': expense_last_30d_cents,
                'net_last_30d_cents': revenue_30d_cents - expense_last_30d_cents,
                'note': 'mrr_estimate_cents uses rolling 30d paid invoice total as a proxy when Stripe MRR is not stored.',
            },
            'health': {
                'average_score': avg_health,
                'distribution': health_buckets,
            },
            'charts': {
                'signups_by_month': signups_by_month,
                'revenue_by_month': revenue_by_month,
                'expenses_by_month': expenses_by_month,
                'expense_by_category': expense_by_category,
                'plan_distribution': plan_distribution,
                'health_histogram_labels': list(health_buckets.keys()),
                'health_histogram_values': list(health_buckets.values()),
            },
            'billing_alerts_rollup': dict(alert_rollup),
        }
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDeveloper])
def platform_cohorts(request):
    """Retention-style cohort table: signup month vs still-active snapshot (approximation)."""
    if not _saas_enabled():
        return Response(
            {'detail': 'Platform SaaS features are disabled (set PLATFORM_SAAS_ENABLED=true).'},
            status=status.HTTP_403_FORBIDDEN,
        )

    now = timezone.now()
    cohorts = []
    anchor = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    for i in range(11, -1, -1):
        month_start = _add_months(anchor, -i)
        month_end = _add_months(month_start, 1)

        signed = Tenant.objects.filter(
            created_at__gte=month_start,
            created_at__lt=month_end,
        ).count()
        still_active = Tenant.objects.filter(
            created_at__gte=month_start,
            created_at__lt=month_end,
            subscription_status__in=('active', 'trialing', 'past_due'),
        ).count()
        cohorts.append(
            {
                'month': month_start.strftime('%Y-%m'),
                'signed_up': signed,
                'still_entitled': still_active,
            }
        )

    return Response({'cohorts': cohorts})


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDeveloper])
def platform_capacity(request):
    """Per-tenant screen and user counts for capacity planning (lightweight)."""
    if not _saas_enabled():
        return Response(
            {'detail': 'Platform SaaS features are disabled (set PLATFORM_SAAS_ENABLED=true).'},
            status=status.HTTP_403_FORBIDDEN,
        )

    session_stats_by_tenant = active_session_stats_by_tenant()

    tenants = (
        Tenant.objects.annotate(
            screen_count=Count('users__owned_screens', distinct=True),
            user_count=Count('users', distinct=True),
        )
        .order_by('-screen_count', 'name')[:500]
    )
    rows = [
        {
            'id': str(t.id),
            'name': t.name,
            'slug': t.slug,
            'screen_count': t.screen_count,
            'user_count': t.user_count,
            'active_user_count': int(
                session_stats_by_tenant.get(str(t.id), {}).get('active_user_count', 0)
            ),
            'active_session_count': int(
                session_stats_by_tenant.get(str(t.id), {}).get('active_session_count', 0)
            ),
            'device_limit': t.device_limit,
            'subscription_status': t.subscription_status,
        }
        for t in tenants
    ]
    return Response({'tenants': rows})


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDeveloper])
def platform_communications_feed(request):
    """Recent notification delivery attempts (email/SMS/webhook pipeline)."""
    if not _saas_enabled():
        return Response(
            {'detail': 'Platform SaaS features are disabled (set PLATFORM_SAAS_ENABLED=true).'},
            status=status.HTTP_403_FORBIDDEN,
        )

    qs = NotificationLog.objects.select_related('channel').order_by('-created_at')[:400]
    results = []
    for log in qs:
        results.append(
            {
                'id': str(log.id),
                'event_key': log.event_key,
                'status': log.status,
                'channel_type': log.channel.type if log.channel else None,
                'created_at': log.created_at.isoformat() if log.created_at else None,
                'sent_at': log.sent_at.isoformat() if log.sent_at else None,
                'error_message': (log.error_message or '')[:800],
                'retry_count': log.retry_count,
            }
        )
    return Response({'results': results})


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDeveloper])
def platform_system_health(request):
    """Dependency checks for operators (DB, cache); extend with Celery/redis as needed."""
    if not _saas_enabled():
        return Response(
            {'detail': 'Platform SaaS features are disabled (set PLATFORM_SAAS_ENABLED=true).'},
            status=status.HTTP_403_FORBIDDEN,
        )

    checks = {}
    all_ok = True

    try:
        connection.ensure_connection()
        checks['database'] = {'ok': True}
    except Exception as e:
        all_ok = False
        checks['database'] = {'ok': False, 'error': str(e)}

    try:
        cache.set('__platform_health_ping', 1, 10)
        ping = cache.get('__platform_health_ping')
        cache_ok = ping == 1
        checks['cache'] = {'ok': cache_ok}
        if not cache_ok:
            all_ok = False
    except Exception as e:
        all_ok = False
        checks['cache'] = {'ok': False, 'error': str(e)}

    return Response(
        {
            'ok': all_ok,
            'checks': checks,
            'timestamp': timezone.now().isoformat(),
        }
    )
