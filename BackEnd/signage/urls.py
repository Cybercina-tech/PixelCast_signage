from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ScreenViewSet,
    heartbeat_endpoint,
    command_pull_endpoint,
    command_response_endpoint,
    content_sync_endpoint,
    health_check_endpoint
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'screens', ScreenViewSet, basename='screen')

urlpatterns = [
    # Router URLs (includes /api/screens/ for ViewSet)
    path('', include(router.urls)),
    
    # Standalone API endpoints
    path('screens/heartbeat/', heartbeat_endpoint, name='screen-heartbeat'),
    path('screens/command-pull/', command_pull_endpoint, name='screen-command-pull'),
    path('screens/command-response/', command_response_endpoint, name='screen-command-response'),
    path('screens/content-sync/', content_sync_endpoint, name='screen-content-sync'),
    path('screens/health-check/', health_check_endpoint, name='screen-health-check'),
    # Note: command-receive endpoint is in commands.urls for better organization
]
