from django.urls import path
from rest_framework.routers import DefaultRouter

from .stripe_webhook import stripe_webhook_view
from .billing_customer_views import create_billing_portal_session, create_checkout_session
from .pricing_views import (
    BillingPromotionViewSet,
    SubscriptionPlanViewSet,
    platform_billing_settings,
)
from .integration_views import tenant_api_key_revoke, tenant_api_keys, tenant_webhooks
from .export_views import export_users_xlsx
from .overview_views import (
    platform_capacity,
    platform_cohorts,
    platform_communications_feed,
    platform_overview,
    platform_system_health,
)
from .reporting_views import platform_reports_summary
from .license_views import tenant_license_enforcement_logs, tenant_license_view
from licensing.registry_admin_views import (
    self_hosted_license_detail,
    self_hosted_license_heartbeats,
    self_hosted_license_list,
    self_hosted_license_reactivate,
    self_hosted_license_suspicious,
    self_hosted_license_suspend,
)
from .views import PlatformExpenseViewSet, TenantViewSet, impersonate_start, impersonate_stop

router = DefaultRouter()
router.register(r'tenants', TenantViewSet, basename='platform-tenant')
router.register(r'billing/expenses', PlatformExpenseViewSet, basename='platform-expense')
router.register(r'pricing/plans', SubscriptionPlanViewSet, basename='platform-subscription-plan')
router.register(r'pricing/promotions', BillingPromotionViewSet, basename='platform-billing-promotion')

urlpatterns = [
    path('overview/', platform_overview, name='platform-overview'),
    path('reports/summary/', platform_reports_summary, name='platform-reports-summary'),
    path('cohorts/', platform_cohorts, name='platform-cohorts'),
    path('exports/users.xlsx', export_users_xlsx, name='platform-export-users-xlsx'),
    path('capacity/', platform_capacity, name='platform-capacity'),
    path('communications/', platform_communications_feed, name='platform-communications'),
    path('system-health/', platform_system_health, name='platform-system-health'),
    path('stripe/webhook/', stripe_webhook_view, name='platform-stripe-webhook'),
    path('billing/checkout-session/', create_checkout_session, name='platform-billing-checkout'),
    path('billing/portal-session/', create_billing_portal_session, name='platform-billing-portal'),
    path('pricing/settings/', platform_billing_settings, name='platform-billing-settings'),
    path('integrations/api-keys/', tenant_api_keys, name='platform-api-keys'),
    path('integrations/api-keys/<uuid:pk>/revoke/', tenant_api_key_revoke, name='platform-api-key-revoke'),
    path('integrations/webhooks/', tenant_webhooks, name='platform-tenant-webhooks'),
    path('impersonate/', impersonate_start, name='platform-impersonate-start'),
    path('impersonate/stop/', impersonate_stop, name='platform-impersonate-stop'),
    path('tenants/<uuid:tenant_id>/license/', tenant_license_view, name='platform-tenant-license'),
    path('tenants/<uuid:tenant_id>/license/enforcement-logs/', tenant_license_enforcement_logs, name='platform-tenant-license-logs'),
    path('self-hosted-licenses/', self_hosted_license_list, name='platform-self-hosted-licenses'),
    path('self-hosted-licenses/<uuid:pk>/', self_hosted_license_detail, name='platform-self-hosted-license-detail'),
    path('self-hosted-licenses/<uuid:pk>/suspend/', self_hosted_license_suspend, name='platform-self-hosted-license-suspend'),
    path('self-hosted-licenses/<uuid:pk>/reactivate/', self_hosted_license_reactivate, name='platform-self-hosted-license-reactivate'),
    path('self-hosted-licenses/<uuid:pk>/suspicious/', self_hosted_license_suspicious, name='platform-self-hosted-license-suspicious'),
    path('self-hosted-licenses/<uuid:pk>/heartbeats/', self_hosted_license_heartbeats, name='platform-self-hosted-license-heartbeats'),
] + router.urls
