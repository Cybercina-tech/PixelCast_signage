"""
ASGI config for PixelCast Signage (package: Screengram).

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from django.urls import re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Screengram.settings')

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# Import routing after Django is initialized
from Screengram.routing import (
    authenticated_websocket_urlpatterns,
    pairing_websocket_urlpatterns,
)

application = ProtocolTypeRouter({
    # Django's ASGI application to handle traditional HTTP requests
    "http": django_asgi_app,
    
    # WebSocket handler — pairing uses temporary token auth inside the consumer,
    # not Django session/JWT middleware (avoids AuthFailed on TV wait screen).
    "websocket": AllowedHostsOriginValidator(
        URLRouter([
            *pairing_websocket_urlpatterns,
            # AuthMiddlewareStack must be wrapped in re_path — not a raw URLRouter child.
            re_path(
                r'',
                AuthMiddlewareStack(
                    URLRouter(authenticated_websocket_urlpatterns)
                ),
            ),
        ])
    ),
})
