"""
URL configuration for core infrastructure endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import (
    AuditLogViewSet,
    SystemBackupViewSet,
    NotificationViewSet,
    NotificationPreferenceViewSet,
    TVBrandViewSet,
)
from core.deploy_views import github_webhook, deployment_status

router = DefaultRouter()
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')
router.register(r'backups', SystemBackupViewSet, basename='backup')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'notification-preferences', NotificationPreferenceViewSet, basename='notification-preferences')
router.register(r'tv-brands', TVBrandViewSet, basename='tv-brand')

urlpatterns = [
    path('', include(router.urls)),
    # Deployment webhook endpoints
    path('deploy/webhook/', github_webhook, name='github-webhook'),
    path('deploy/status/', deployment_status, name='deployment-status'),
]
