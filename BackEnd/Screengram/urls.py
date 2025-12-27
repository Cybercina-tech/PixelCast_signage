"""
URL configuration for Screengram project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from log.views import ErrorLogViewSet

# Create router for admin endpoints
admin_router = DefaultRouter()
admin_router.register(r'errors', ErrorLogViewSet, basename='error-log')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/', include('signage.urls')),
    path('api/', include('templates.urls')),
    path('api/', include('commands.urls')),
    path('api/', include('bulk_operations.urls')),  # Bulk operations endpoints
    path('api/', include('content_validation.urls')),  # Content validation endpoints
    path('api/', include('analytics.urls')),  # Analytics dashboard endpoints
    path('api/core/', include('core.urls')),  # Core infrastructure (audit, backup)
    path('api/logs/', include('log.urls')),
    path('api/admin/', include(admin_router.urls)),  # Admin-only endpoints (errors)
    path('', include('api_docs.urls')),  # API documentation (Swagger/OpenAPI)
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
