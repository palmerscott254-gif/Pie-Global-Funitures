"""
Django Channels WebSocket consumers for real-time notifications.

Handles:
- User authentication
- WebSocket connection/disconnection
- Real-time message delivery
- Safe JSON encoding/decoding
- Error handling and reconnect logic
"""

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
import json
import logging

from .models import Notification

User = get_user_model()
logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications.
    
    Features:
    - Secure authentication via JWT / session token
    - Automatic group membership for user
    - Real-time unread count updates
    - Reliable message delivery
    - Error handling
    
    WebSocket Events (from server):
    - notification_message: New notification arrived
    - unread_count_update: Unread badge count changed
    - connection_established: Confirmation message
    - error: Error message
    
    Client Commands (to server):
    - mark_read: Mark notification as read
    - ping: Keep-alive ping
    """

    async def connect(self):
        """
        Handle WebSocket connection.
        
        Steps:
        1. Authenticate user
        2. Accept connection
        3. Add to user's group
        4. Send unread count
        """
        # Extract user from scope (set by auth middleware)
        self.user = self.scope.get('user')
        
        # Authenticate: check if user is valid and authenticated
        if not self.user or not self.user.is_authenticated:
            # Reject unauthenticated connections
            await self.close()
            logger.warning(f"Unauthenticated WebSocket connection attempt")
            return
        
        # Store user ID for later use
        self.user_id = self.user.id
        
        # Create a unique group for this user
        # All notifications for this user go to this group
        self.user_group = f'user_{self.user_id}'
        
        # Add this channel to the user's group
        await self.channel_layer.group_add(
            self.user_group,
            self.channel_name
        )
        
        # Accept WebSocket connection
        await self.accept()
        
        logger.info(f"User {self.user_id} connected to WebSocket")
        
        # Send initial unread count
        await self.send_unread_count()
        
        # Send confirmation message to client
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to notification service',
            'user_id': self.user_id,
        }))

    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.
        Clean up group membership.
        """
        # Remove from user's group
        await self.channel_layer.group_discard(
            self.user_group,
            self.channel_name
        )
        
        logger.info(
            f"User {self.user_id} disconnected from WebSocket "
            f"(close_code={close_code})"
        )

    async def receive(self, text_data):
        """
        Handle incoming WebSocket messages from client.
        
        Supports commands:
        - mark_read: Mark notification as read
        - ping: Keep-alive ping
        """
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON format")
            return
        
        action = data.get('action')
        
        if action == 'mark_read':
            # Client marking notification as read
            notification_id = data.get('notification_id')
            if notification_id:
                await self.handle_mark_read(notification_id)
        
        elif action == 'ping':
            # Keep-alive ping
            await self.send(text_data=json.dumps({
                'type': 'pong',
                'timestamp': str(timezone.now()),
            }))
        
        else:
            await self.send_error(f"Unknown action: {action}")

    async def handle_mark_read(self, notification_id):
        """
        Handle marking notification as read via WebSocket.
        Delegates to database operation and broadcasts update.
        """
        try:
            await self.mark_notification_read(notification_id)
            
            # Broadcast updated unread count
            await self.send_unread_count()
            
        except Exception as exc:
            logger.error(
                f"Error marking notification {notification_id} as read: {str(exc)}",
                exc_info=True
            )
            await self.send_error(f"Failed to mark notification as read")

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """
        Database operation: Mark notification as read.
        Called from async context via @database_sync_to_async.
        """
        from django.utils import timezone
        
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user_id=self.user_id
            )
            
            if not notification.is_read:
                notification.mark_as_read()
                logger.debug(f"Marked notification {notification_id} as read")
            
        except Notification.DoesNotExist:
            logger.warning(
                f"Notification {notification_id} not found for user {self.user_id}"
            )

    @database_sync_to_async
    def get_unread_count(self):
        """
        Database operation: Get current unread count.
        Called from async context via @database_sync_to_async.
        """
        return Notification.get_unread_count(
            User.objects.get(id=self.user_id)
        )

    async def send_unread_count(self):
        """
        Send current unread count to client for badge update.
        """
        unread_count = await self.get_unread_count()
        
        await self.send(text_data=json.dumps({
            'type': 'unread_count_update',
            'unread_count': unread_count,
        }))

    async def send_error(self, message):
        """
        Send error message to client.
        """
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message,
        }))

    # ========== Group Message Handlers ==========
    # These methods are called when messages are sent to the user's group
    # via channel_layer.group_send()

    async def notification_message(self, event):
        """
        Handler for notification_message events from group.
        Called when a new notification is sent to the user's group.
        
        Event structure:
        {
            'type': 'notification_message',
            'notification': {notification_data},
        }
        """
        notification = event.get('notification')
        
        # Send notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'notification': notification,
        }))
        
        logger.debug(
            f"Sent notification {notification.get('id')} to user {self.user_id}"
        )

    async def unread_count_update(self, event):
        """
        Handler for unread_count_update events from group.
        Called when unread count changes.
        
        Event structure:
        {
            'type': 'unread_count_update',
            'unread_count': 5,
        }
        """
        await self.send(text_data=json.dumps({
            'type': 'unread_count_update',
            'unread_count': event['unread_count'],
        }))
        
        logger.debug(
            f"Updated unread count for user {self.user_id}: "
            f"{event['unread_count']}"
        )

    async def connection_error(self, event):
        """
        Handler for connection_error events from group.
        Notifies user of system-level issues.
        """
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': event.get('message', 'Connection error'),
            'error_code': event.get('code'),
        }))


# ============================================
# TOKEN-BASED AUTHENTICATION MIDDLEWARE
# ============================================

class NotificationConsumerAuthMiddleware:
    """
    Custom middleware for WebSocket authentication.
    
    Supports:
    - JWT token authentication
    - Session-based authentication
    - Token passed in URL query parameter
    
    Usage in asgi.py:
        from apps.notifications.consumers import NotificationConsumerAuthMiddleware
        
        application = ProtocolTypeRouter({
            "websocket": NotificationConsumerAuthMiddleware(
                URLRouter([
                    path("ws/notifications/", NotificationConsumer.as_asgi()),
                ])
            ),
        })
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        """
        Authenticate WebSocket connection based on token or session.
        """
        from django.contrib.auth.models import AnonymousUser
        from rest_framework_simplejwt.tokens import AccessToken
        
        # Extract token from URL parameters
        query_string = scope.get('query_string', b'').decode()
        
        user = None
        
        # Try JWT token authentication
        if 'token=' in query_string:
            token_start = query_string.index('token=') + 6
            token_end = query_string.find('&', token_start)
            if token_end == -1:
                token_end = len(query_string)
            
            token = query_string[token_start:token_end]
            
            try:
                decoded = AccessToken(token)
                user_id = decoded['user_id']
                user = await self.get_user(user_id)
            except Exception as exc:
                logger.warning(f"JWT authentication failed: {str(exc)}")
                user = AnonymousUser()
        
        # Fallback to session authentication
        if not user or not user.is_authenticated:
            try:
                # Extract session ID from cookies
                headers = dict(scope.get('headers', []))
                cookies = headers.get(b'cookie', b'').decode()
                
                if 'sessionid=' in cookies:
                    session_id_start = cookies.index('sessionid=') + 10
                    session_id_end = cookies.find(';', session_id_start)
                    if session_id_end == -1:
                        session_id_end = len(cookies)
                    
                    session_id = cookies[session_id_start:session_id_end]
                    user = await self.get_user_from_session(session_id)
            
            except Exception as exc:
                logger.warning(f"Session authentication failed: {str(exc)}")
                user = AnonymousUser()
        
        # Set user in scope
        scope['user'] = user or AnonymousUser()
        
        return await self.app(scope, receive, send)

    @database_sync_to_async
    def get_user(self, user_id):
        """Get user by ID from database."""
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def get_user_from_session(self, session_id):
        """Get user from session data."""
        from django.contrib.sessions.models import Session
        
        try:
            session = Session.objects.get(session_key=session_id)
            user_id = session.get_decoded().get('_auth_user_id')
            if user_id:
                return User.objects.get(id=user_id)
        except Exception:
            pass
        
        return None
