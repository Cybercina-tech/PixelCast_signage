"""
URL configuration for core infrastructure endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import AuditLogViewSet, SystemBackupViewSet, NotificationViewSet

router = DefaultRouter()
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')
router.register(r'backups', SystemBackupViewSet, basename='backup')
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
]
