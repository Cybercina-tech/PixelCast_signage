from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TemplateViewSet,
    LayerViewSet,
    WidgetViewSet,
    ContentViewSet,
    ScheduleViewSet
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'templates', TemplateViewSet, basename='template')
router.register(r'layers', LayerViewSet, basename='layer')
router.register(r'widgets', WidgetViewSet, basename='widget')
router.register(r'contents', ContentViewSet, basename='content')
router.register(r'schedules', ScheduleViewSet, basename='schedule')

urlpatterns = [
    # Router URLs (includes /api/templates/, /api/layers/, etc.)
    path('', include(router.urls)),
]
