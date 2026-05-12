"""
ASGI config for Pie Global Furniture project.
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pie_global.settings')

# Import notifications routing and middleware
try:
	from apps.notifications.routing import websocket_urlpatterns
	from apps.notifications.consumers import NotificationConsumerAuthMiddleware
except Exception:
	websocket_urlpatterns = []
	NotificationConsumerAuthMiddleware = None

django_asgi_app = get_asgi_application()

if NotificationConsumerAuthMiddleware:
	application = ProtocolTypeRouter({
		"http": django_asgi_app,
		"websocket": NotificationConsumerAuthMiddleware(
			URLRouter(websocket_urlpatterns)
		),
	})
else:
	application = django_asgi_app
