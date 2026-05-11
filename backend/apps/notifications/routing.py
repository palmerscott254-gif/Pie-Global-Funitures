"""
Django Channels WebSocket URL routing.

Maps WebSocket connections to consumers.
Includes authentication middleware.

Installation in asgi.py:
    from apps.notifications.routing import websocket_urlpatterns, NotificationConsumerAuthMiddleware
    from channels.routing import ProtocolTypeRouter, URLRouter
    
    application = ProtocolTypeRouter({
        "http": get_asgi_application(),
        "websocket": NotificationConsumerAuthMiddleware(
            URLRouter(websocket_urlpatterns)
        ),
    })
"""

from django.urls import path
from . import consumers

# WebSocket URL patterns
websocket_urlpatterns = [
    # Main notification WebSocket endpoint
    # Client connects via: ws://localhost:8000/ws/notifications/?token=<jwt_token>
    # or with session: ws://localhost:8000/ws/notifications/
    path(
        'ws/notifications/',
        consumers.NotificationConsumer.as_asgi(),
        name='websocket-notifications'
    ),
]
