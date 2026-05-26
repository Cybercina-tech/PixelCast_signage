"""
WebSocket routing configuration for Django Channels.

Defines URL patterns for WebSocket connections.
"""
from django.urls import re_path
from commands.consumers import ScreenConsumer
from commands.dashboard_consumer import AdminDashboardConsumer
from signage.pairing_consumer import PairingConsumer

# Pairing must NOT use AuthMiddlewareStack (temporary pairing_token only).
pairing_websocket_urlpatterns = [
    re_path(r'ws/pairing/$', PairingConsumer.as_asgi()),
]

# Screen + dashboard WebSockets (JWT / screen credentials).
authenticated_websocket_urlpatterns = [
    re_path(r'ws/screen/$', ScreenConsumer.as_asgi()),
    re_path(r'ws/dashboard/$', AdminDashboardConsumer.as_asgi()),
]

websocket_urlpatterns = [
    *pairing_websocket_urlpatterns,
    *authenticated_websocket_urlpatterns,
]

