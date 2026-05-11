from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from .models import Notification, NotificationPreference, NotificationLog, NotificationType
from .serializers import (
    NotificationDetailSerializer,
    NotificationListSerializer,
    NotificationPreferenceSerializer,
    NotificationLogSerializer,
    UnreadCountSerializer,
    BulkNotificationActionSerializer,
    AdminBroadcastNotificationSerializer,
)
from .notification_service import NotificationService
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly
from core.response_helpers import success_response, error_response


class NotificationPagination(PageNumberPagination):
    """
    Custom pagination for notification list.
    Default page size of 20, max 100.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class NotificationViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing user notifications.
    
    Endpoints:
    - GET /api/notifications/ - List paginated notifications
    - GET /api/notifications/{id}/ - Get notification details
    - GET /api/notifications/unread-count/ - Get unread badge count
    - POST /api/notifications/{id}/mark-read/ - Mark single as read
    - POST /api/notifications/mark-all-read/ - Mark all as read
    - POST /api/notifications/bulk-action/ - Perform bulk actions (mark read, delete)
    - DELETE /api/notifications/{id}/ - Delete (soft delete) notification
    
    Security:
    - Users can only access their own notifications
    - Proper permission checks on all endpoints
    - Read access for prefetch optimization
    """
    
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = NotificationPagination
    search_fields = ['title', 'message', 'notification_type']
    filterset_fields = ['notification_type', 'priority', 'is_read']
    ordering_fields = ['created_at', 'priority', 'is_read']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Return only non-deleted notifications for the current user.
        Optimized with select_related for common FK lookups.
        """
        user = self.request.user
        
        # Base queryset filtered by user and not deleted
        queryset = Notification.objects.filter(
            user=user,
            is_deleted=False
        ).exclude(
            expires_at__lt=timezone.now()
        )
        
        # Filter by type if specified
        notification_type = self.request.query_params.get('notification_type')
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        # Filter by status
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            is_read_bool = is_read.lower() in ('true', '1', 'yes')
            queryset = queryset.filter(is_read=is_read_bool)
        
        return queryset.select_related('user')

    def get_serializer_class(self):
        """
        Return lightweight list serializer for list views,
        detailed serializer for detail views.
        """
        if self.action == 'list':
            return NotificationListSerializer
        return NotificationDetailSerializer

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """
        GET /api/notifications/unread-count/
        
        Return current unread notification count for badge.
        Lightweight query - only COUNT(*) on database.
        
        Response:
        {
            "unread_count": 5
        }
        """
        user = request.user
        unread_count = Notification.get_unread_count(user)
        
        serializer = UnreadCountSerializer({'unread_count': unread_count})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """
        POST /api/notifications/{id}/mark-read/
        
        Mark single notification as read.
        User can only mark their own notifications.
        
        Response includes updated notification data.
        """
        notification = self.get_object()
        
        # Check ownership
        if notification.user != request.user:
            return error_response(
                'Forbidden',
                'Cannot mark another user\'s notification as read',
                status.HTTP_403_FORBIDDEN
            )
        
        # Mark as read
        notification.mark_as_read()
        
        # Broadcast to WebSocket if needed
        NotificationService.broadcast_unread_count_update(notification.user)
        
        serializer = self.get_serializer(notification)
        return success_response(
            serializer.data,
            'Notification marked as read'
        )

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """
        POST /api/notifications/mark-all-read/
        
        Mark all unread notifications as read for current user.
        Bulk operation for convenience.
        
        Response:
        {
            "marked_count": 5,
            "message": "5 notifications marked as read"
        }
        """
        user = request.user
        now = timezone.now()
        
        # Get all unread, non-deleted notifications
        unread_notifications = Notification.objects.filter(
            user=user,
            is_read=False,
            is_deleted=False
        ).exclude(
            expires_at__lt=now
        )
        
        count = unread_notifications.count()
        
        # Bulk update for efficiency
        unread_notifications.update(
            is_read=True,
            read_at=now,
            updated_at=now
        )
        
        # Broadcast to WebSocket
        NotificationService.broadcast_unread_count_update(user)
        
        return success_response(
            {'marked_count': count},
            f'{count} notifications marked as read'
        )

    @action(detail=False, methods=['post'])
    def bulk_action(self, request):
        """
        POST /api/notifications/bulk-action/
        
        Perform bulk actions on multiple notifications.
        Supported actions: mark_read, mark_unread, delete
        
        Request body:
        {
            "notification_ids": [1, 2, 3],
            "action": "mark_read"
        }
        
        Response:
        {
            "affected_count": 3,
            "message": "3 notifications marked as read"
        }
        """
        serializer = BulkNotificationActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        notification_ids = serializer.validated_data['notification_ids']
        action = serializer.validated_data['action']
        user = request.user
        
        # Get notifications belonging to user
        notifications = Notification.objects.filter(
            id__in=notification_ids,
            user=user,
            is_deleted=False
        )
        
        now = timezone.now()
        affected_count = 0
        
        if action == 'mark_read':
            affected_count = notifications.update(
                is_read=True,
                read_at=now,
                updated_at=now
            )
            message = f'{affected_count} notifications marked as read'
        
        elif action == 'mark_unread':
            affected_count = notifications.update(
                is_read=False,
                read_at=None,
                updated_at=now
            )
            message = f'{affected_count} notifications marked as unread'
        
        elif action == 'delete':
            affected_count = notifications.update(
                is_deleted=True,
                updated_at=now
            )
            message = f'{affected_count} notifications deleted'
        
        # Broadcast update
        NotificationService.broadcast_unread_count_update(user)
        
        return success_response(
            {'affected_count': affected_count},
            message
        )

    def destroy(self, request, pk=None):
        """
        DELETE /api/notifications/{id}/
        
        Soft delete a notification.
        Data is retained in database for audit purposes.
        """
        notification = self.get_object()
        
        if notification.user != request.user:
            return error_response(
                'Forbidden',
                'Cannot delete another user\'s notification',
                status.HTTP_403_FORBIDDEN
            )
        
        notification.is_deleted = True
        notification.save(update_fields=['is_deleted', 'updated_at'])
        
        NotificationService.broadcast_unread_count_update(request.user)
        
        return success_response(
            {},
            'Notification deleted',
            status.HTTP_200_OK
        )


class NotificationPreferenceViewSet(viewsets.ViewSet):
    """
    ViewSet for managing user notification preferences.
    
    Endpoints:
    - GET /api/notification-preferences/ - Get current preferences
    - PUT /api/notification-preferences/ - Update preferences
    """
    
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """
        GET /api/notification-preferences/
        
        Get current user's notification preferences.
        """
        user = request.user
        pref, created = NotificationPreference.objects.get_or_create(user=user)
        
        serializer = NotificationPreferenceSerializer(pref)
        return Response(serializer.data)

    def update(self, request):
        """
        PUT /api/notification-preferences/
        
        Update notification preferences.
        """
        user = request.user
        pref, created = NotificationPreference.objects.get_or_create(user=user)
        
        serializer = NotificationPreferenceSerializer(pref, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return success_response(
            serializer.data,
            'Notification preferences updated'
        )


class AdminNotificationViewSet(viewsets.ViewSet):
    """
    Admin-only endpoints for broadcasting notifications.
    
    Endpoints:
    - POST /api/admin/send-notification/ - Broadcast to single/multiple/all users
    - GET /api/admin/notification-logs/ - View delivery logs
    
    Security:
    - Staff/superuser access required
    - Proper audit logging
    """
    
    permission_classes = [permissions.IsAdminUser]

    def create(self, request):
        """
        POST /api/admin/send-notification/
        
        Admin broadcasting endpoint.
        Create and deliver notifications to specified recipients.
        Can target: single user, multiple users, or all users.
        
        Request body:
        {
            "title": "Important Update",
            "message": "We've updated our return policy...",
            "recipient_type": "all",
            "priority": "HIGH",
            "action_url": "/pages/policy",
            "expires_in_hours": 48
        }
        
        Response:
        {
            "created_count": 1000,
            "message": "Notification sent to 1000 users"
        }
        """
        serializer = AdminBroadcastNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        created_count = NotificationService.broadcast_to_users(
            title=data['title'],
            message=data['message'],
            recipient_type=data['recipient_type'],
            user_ids=data.get('user_ids', []),
            notification_type=NotificationType.ADMIN_MESSAGE,
            priority=data.get('priority', 'NORMAL'),
            action_url=data.get('action_url'),
            metadata=data.get('metadata', {}),
            expires_in_hours=data.get('expires_in_hours'),
            created_by_user=request.user
        )
        
        return success_response(
            {'created_count': created_count},
            f'Notification sent to {created_count} users',
            status.HTTP_201_CREATED
        )

    def logs(self, request):
        """
        GET /api/admin/notification-logs/
        
        View notification delivery logs for debugging.
        Includes delivery status, attempts, and errors.
        """
        logs = NotificationLog.objects.all().order_by('-created_at')[:100]
        serializer = NotificationLogSerializer(logs, many=True)
        return Response(serializer.data)
