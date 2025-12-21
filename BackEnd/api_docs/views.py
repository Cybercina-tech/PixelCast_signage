"""
API Documentation views with security.

Provides protected access to Swagger/OpenAPI documentation.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.conf import settings
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


class ProtectedSpectacularAPIView(SpectacularAPIView):
    """
    Protected OpenAPI schema view.
    
    In production, requires authentication.
    In development (DEBUG=True), allows unauthenticated access.
    """
    permission_classes = [IsAuthenticated] if not settings.DEBUG else [AllowAny]


class ProtectedSpectacularSwaggerView(SpectacularSwaggerView):
    """
    Protected Swagger UI view.
    
    In production, requires authentication.
    In development (DEBUG=True), allows unauthenticated access.
    """
    permission_classes = [IsAuthenticated] if not settings.DEBUG else [AllowAny]


class ProtectedSpectacularRedocView(SpectacularRedocView):
    """
    Protected ReDoc view.
    
    In production, requires authentication.
    In development (DEBUG=True), allows unauthenticated access.
    """
    permission_classes = [IsAuthenticated] if not settings.DEBUG else [AllowAny]
