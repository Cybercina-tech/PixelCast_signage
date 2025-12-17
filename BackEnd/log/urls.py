from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ScreenStatusLogViewSet,
    ContentDownloadLogViewSet,
    CommandExecutionLogViewSet
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'screen-status', ScreenStatusLogViewSet, basename='screen-status-log')
router.register(r'content-download', ContentDownloadLogViewSet, basename='content-download-log')
router.register(r'command-execution', CommandExecutionLogViewSet, basename='command-execution-log')

urlpatterns = [
    # Router URLs (includes /api/logs/screen-status/, /api/logs/content-download/, etc.)
    path('', include(router.urls)),
]
