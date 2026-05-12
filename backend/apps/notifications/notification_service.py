"""
Notification Service - Core business logic for notification system.

This service handles:
- Creating notifications of various types
- Broadcast operations (single, multiple, all users)
- WebSocket communication
- Preference checking
- Async task queueing
"""

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Prefetch
from datetime import timedelta
import json

from .models import (
    Notification,
    NotificationType,
    NotificationPriority,
    NotificationPreference,
)

User = get_user_model()


class NotificationService:
    """
    Central service for all notification operations.
    Coordinates between models, WebSocket consumers, and async tasks.
    """

    # Default priority mapping for notification types
    DEFAULT_PRIORITY_MAP = {
        NotificationType.ORDER_CONFIRMED: NotificationPriority.NORMAL,
        NotificationType.PAYMENT_RECEIVED: NotificationPriority.NORMAL,
        NotificationType.ORDER_SHIPPED: NotificationPriority.NORMAL,
        NotificationType.DELIVERY_UPDATE: NotificationPriority.NORMAL,
        NotificationType.DELIVERED: NotificationPriority.NORMAL,
        NotificationType.DELIVERY_FAILED: NotificationPriority.URGENT,
        NotificationType.RESTOCKED_ITEM: NotificationPriority.LOW,
        NotificationType.ADMIN_MESSAGE: NotificationPriority.HIGH,
        NotificationType.WARRANTY_UPDATE: NotificationPriority.HIGH,
        NotificationType.REFUND_STATUS: NotificationPriority.HIGH,
        NotificationType.INVOICE_READY: NotificationPriority.NORMAL,
        NotificationType.DELIVERY_ETA: NotificationPriority.NORMAL,
        NotificationType.LOYALTY_POINTS: NotificationPriority.LOW,
        NotificationType.REVIEW_REMINDER: NotificationPriority.LOW,
    }

    @staticmethod
    def create_notification(
        user,
        title,
        message,
        notification_type,
        priority=None,
        action_url=None,
        metadata=None,
        expires_at=None,
    ):
        """
        Create a single notification with comprehensive validation.
        
        Args:
            user: User instance
            title: Brief notification title
            message: Full message body
            notification_type: One of NotificationType choices
            priority: Optional priority (uses DEFAULT_PRIORITY_MAP if not provided)
            action_url: Optional URL to navigate to
            metadata: Optional JSON data (order_id, product_id, tracking_info, etc.)
            expires_at: Optional expiration datetime
            
        Returns:
            Notification instance or None if creation fails
        """
        
        # Check user preferences
        try:
            pref = NotificationPreference.objects.get(user=user)
            if not pref.should_notify(notification_type):
                return None
        except NotificationPreference.DoesNotExist:
            # User has never set preferences, use defaults (allow all)
            pass
        
        # Set default priority if not provided
        if priority is None:
            priority = NotificationService.DEFAULT_PRIORITY_MAP.get(
                notification_type,
                NotificationPriority.NORMAL
            )
        
        # Create notification
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            action_url=action_url,
            metadata=metadata or {},
            expires_at=expires_at,
        )
        
        return notification

    @staticmethod
    def create_and_broadcast(
        user,
        title,
        message,
        notification_type,
        priority=None,
        action_url=None,
        metadata=None,
        expires_at=None,
        broadcast_websocket=True,
    ):
        """
        Create notification and immediately broadcast via WebSocket.
        
        Args:
            broadcast_websocket: If True, sends instant WebSocket update
            
        Returns:
            Notification instance or None
        """
        
        notification = NotificationService.create_notification(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            action_url=action_url,
            metadata=metadata,
            expires_at=expires_at,
        )
        
        if notification and broadcast_websocket:
            # Send real-time update to WebSocket
            NotificationService.broadcast_notification(notification)
            
            # Update unread badge count
            NotificationService.broadcast_unread_count_update(user)
        
        return notification

    @staticmethod
    def broadcast_to_users(
        title,
        message,
        recipient_type,
        notification_type,
        user_ids=None,
        priority=None,
        action_url=None,
        metadata=None,
        expires_in_hours=None,
        created_by_user=None,
    ):
        """
        Broadcast notification to single user, multiple users, or all users.
        Efficient bulk creation with minimal database queries.
        
        Args:
            recipient_type: 'single', 'multiple', or 'all'
            user_ids: List of user IDs (required for 'single'/'multiple')
            expires_in_hours: Optional hours until expiration
            created_by_user: Admin user who created the broadcast (for audit)
            
        Returns:
            Count of notifications created
        """
        
        # Calculate expiration
        expires_at = None
        if expires_in_hours:
            expires_at = timezone.now() + timedelta(hours=expires_in_hours)
        
        # Determine recipients
        if recipient_type == 'single':
            user_ids = user_ids or []
            recipients = User.objects.filter(id=user_ids[0])
        elif recipient_type == 'multiple':
            recipients = User.objects.filter(id__in=user_ids or [])
        elif recipient_type == 'all':
            # Exclude inactive users
            recipients = User.objects.filter(is_active=True)
        else:
            return 0
        
        # Bulk create notifications
        notifications = [
            Notification(
                user=user,
                title=title,
                message=message,
                notification_type=notification_type,
                priority=priority or NotificationService.DEFAULT_PRIORITY_MAP.get(
                    notification_type,
                    NotificationPriority.NORMAL
                ),
                action_url=action_url,
                metadata=metadata or {},
                expires_at=expires_at,
            )
            for user in recipients
        ]
        
        created_notifications = Notification.objects.bulk_create(
            notifications,
            batch_size=100,  # Create in batches for memory efficiency
        )
        
        # Broadcast via WebSocket to connected users (via Celery task)
        from apps.notifications.tasks import broadcast_notification_async
        broadcast_notification_async.delay(
            [n.id for n in created_notifications]
        )
        
        return len(created_notifications)

    @staticmethod
    def broadcast_notification(notification):
        """
        Send notification via WebSocket to connected user.
        Delegates to Celery for async execution.
        
        Args:
            notification: Notification instance
        """
        from apps.notifications.tasks import send_notification_via_websocket
        
        send_notification_via_websocket.delay(notification.id)

    @staticmethod
    def broadcast_unread_count_update(user):
        """
        Update unread count badge via WebSocket.
        Sends only the numeric count to update UI badge in real-time.
        
        Args:
            user: User instance
        """
        from apps.notifications.tasks import update_unread_count_async
        
        update_unread_count_async.delay(user.id)

    @staticmethod
    def mark_notification_delivered_websocket(notification_id):
        """
        Mark notification as delivered via WebSocket.
        Called after successful WebSocket transmission.
        """
        try:
            notification = Notification.objects.get(id=notification_id)
            # Update log if exists
            if hasattr(notification, 'log'):
                notification.log.websocket_delivered = True
                notification.log.save(update_fields=['websocket_delivered'])
        except Notification.DoesNotExist:
            pass

    @staticmethod
    def get_formatted_notification(notification):
        """
        Format notification for WebSocket transmission.
        Returns dictionary ready for JSON serialization.
        """
        from django.utils.timesince import timesince
        
        return {
            'id': notification.id,
            'uuid': str(notification.uuid),
            'title': notification.title,
            'message': notification.message,
            'notification_type': notification.notification_type,
            'type_display': notification.get_notification_type_display(),
            'priority': notification.priority,
            'priority_display': notification.get_priority_display(),
            'is_read': notification.is_read,
            'action_url': notification.action_url,
            'metadata': notification.metadata,
            'created_at': notification.created_at.isoformat(),
            'created_at_relative': timesince(notification.created_at) + ' ago',
        }


class NotificationFactory:
    """
    Factory class for creating specific notification types.
    Encapsulates business logic for each notification type.
    
    Usage:
        NotificationFactory.order_confirmed(user, order)
        NotificationFactory.payment_received(user, payment)
        NotificationFactory.order_shipped(user, order)
    """

    @staticmethod
    def order_confirmed(user, order):
        """Create notification for confirmed order."""
        return NotificationService.create_and_broadcast(
            user=user,
            title=f"Order #{order.id} Confirmed",
            message=f"Your order for {order.total_items} item(s) has been confirmed. We're preparing it for shipment.",
            notification_type=NotificationType.ORDER_CONFIRMED,
            priority=NotificationPriority.NORMAL,
            action_url=f"/orders/{order.id}",
            metadata={
                'order_id': order.id,
                'total_items': order.total_items,
                'total_amount': str(order.total_amount),
            },
        )

    @staticmethod
    def payment_received(user, order, transaction_id=None):
        """Create notification for received payment."""
        return NotificationService.create_and_broadcast(
            user=user,
            title=f"Payment Received",
            message=f"We've received your payment of ${order.total_amount}. Your order #{order.id} is now confirmed.",
            notification_type=NotificationType.PAYMENT_RECEIVED,
            priority=NotificationPriority.NORMAL,
            action_url=f"/orders/{order.id}",
            metadata={
                'order_id': order.id,
                'transaction_id': transaction_id,
                'amount': str(order.total_amount),
            },
        )

    @staticmethod
    def order_shipped(user, order, tracking_number=None, carrier=None):
        """Create notification for shipped order."""
        message = f"Your order #{order.id} has shipped!"
        if tracking_number and carrier:
            message += f" Track it with {carrier} using {tracking_number}."
        
        return NotificationService.create_and_broadcast(
            user=user,
            title="Order Shipped",
            message=message,
            notification_type=NotificationType.ORDER_SHIPPED,
            priority=NotificationPriority.NORMAL,
            action_url=f"/orders/{order.id}",
            metadata={
                'order_id': order.id,
                'tracking_number': tracking_number,
                'carrier': carrier,
            },
        )

    @staticmethod
    def order_received(user, order):
        """Create notification for order received (acknowledgement)."""
        return NotificationService.create_and_broadcast(
            user=user,
            title="Order Received",
            message="Your order has been received and is now being processed.",
            notification_type=NotificationType.ORDER_CONFIRMED,
            priority=NotificationPriority.NORMAL,
            action_url=f"/orders/{order.id}",
            metadata={'order_id': order.id},
        )

    @staticmethod
    def admin_reply_to_message(user, message_obj):
        """Notify a user that support/admin replied to their message."""
        preview = (message_obj.reply_text or '')[:120]
        return NotificationService.create_and_broadcast(
            user=user,
            title="You have received a reply from support.",
            message=f"{preview}",
            notification_type=NotificationType.ADMIN_MESSAGE,
            priority=NotificationPriority.HIGH,
            action_url=f"/support/tickets/{getattr(message_obj, 'id', '')}",
            metadata={
                'message_id': getattr(message_obj, 'id', None),
                'preview': preview,
            },
        )

    @staticmethod
    def delivery_update(user, order, update_message, tracking_info=None):
        """Create notification for delivery update."""
        return NotificationService.create_and_broadcast(
            user=user,
            title="Delivery Update",
            message=update_message,
            notification_type=NotificationType.DELIVERY_UPDATE,
            priority=NotificationPriority.NORMAL,
            action_url=f"/orders/{order.id}",
            metadata={
                'order_id': order.id,
                'tracking_info': tracking_info or {},
            },
        )

    @staticmethod
    def delivery_eta(user, order, eta_time, carrier=None):
        """Create notification for delivery ETA."""
        return NotificationService.create_and_broadcast(
            user=user,
            title="Delivery ETA",
            message=f"Your order is expected to arrive {eta_time}.",
            notification_type=NotificationType.DELIVERY_ETA,
            priority=NotificationPriority.NORMAL,
            action_url=f"/orders/{order.id}",
            metadata={
                'order_id': order.id,
                'eta_time': eta_time,
                'carrier': carrier,
            },
        )

    @staticmethod
    def delivered(user, order):
        """Create notification for successful delivery."""
        return NotificationService.create_and_broadcast(
            user=user,
            title="Order Delivered",
            message=f"Your order #{order.id} has been delivered. How's your experience? Please leave a review!",
            notification_type=NotificationType.DELIVERED,
            priority=NotificationPriority.NORMAL,
            action_url=f"/orders/{order.id}",
            metadata={
                'order_id': order.id,
            },
        )

    @staticmethod
    def delivery_failed(user, order, reason=None):
        """Create notification for failed delivery."""
        message = f"Delivery of your order #{order.id} was unsuccessful."
        if reason:
            message += f" Reason: {reason}"
        
        return NotificationService.create_and_broadcast(
            user=user,
            title="Delivery Failed",
            message=message,
            notification_type=NotificationType.DELIVERY_FAILED,
            priority=NotificationPriority.URGENT,
            action_url=f"/orders/{order.id}",
            metadata={
                'order_id': order.id,
                'reason': reason,
            },
        )

    @staticmethod
    def item_restocked(user, product):
        """Create notification for item back in stock."""
        return NotificationService.create_and_broadcast(
            user=user,
            title=f"{product.name} is Back in Stock",
            message=f"Good news! The {product.name} you were interested in is now available.",
            notification_type=NotificationType.RESTOCKED_ITEM,
            priority=NotificationPriority.LOW,
            action_url=f"/products/{product.id}",
            metadata={
                'product_id': product.id,
                'product_name': product.name,
            },
        )

    @staticmethod
    def refund_status(user, order, status, amount=None):
        """Create notification for refund status update."""
        status_messages = {
            'initiated': 'Your refund has been initiated.',
            'processing': 'Your refund is being processed. It may take 5-10 business days.',
            'completed': f'Your refund of ${amount} has been completed.',
        }
        
        return NotificationService.create_and_broadcast(
            user=user,
            title="Refund Status Update",
            message=status_messages.get(status, f'Refund status: {status}'),
            notification_type=NotificationType.REFUND_STATUS,
            priority=NotificationPriority.HIGH,
            action_url=f"/orders/{order.id}",
            metadata={
                'order_id': order.id,
                'refund_status': status,
                'refund_amount': str(amount) if amount else None,
            },
        )

    @staticmethod
    def invoice_ready(user, order, invoice_url):
        """Create notification for invoice ready."""
        return NotificationService.create_and_broadcast(
            user=user,
            title="Invoice Ready",
            message=f"Your invoice for order #{order.id} is ready to download.",
            notification_type=NotificationType.INVOICE_READY,
            priority=NotificationPriority.NORMAL,
            action_url=invoice_url,
            metadata={
                'order_id': order.id,
                'invoice_url': invoice_url,
            },
        )

    @staticmethod
    def loyalty_points(user, points, action_type='earned'):
        """Create notification for loyalty/reward points."""
        action_messages = {
            'earned': f'You earned {points} loyalty points on your recent purchase!',
            'redeemed': f'You used {points} loyalty points. Your discount has been applied.',
            'expired': f'{points} loyalty points have expired.',
        }
        
        return NotificationService.create_and_broadcast(
            user=user,
            title="Loyalty Points",
            message=action_messages.get(action_type, f'Loyalty points: {points}'),
            notification_type=NotificationType.LOYALTY_POINTS,
            priority=NotificationPriority.LOW,
            metadata={
                'points': points,
                'action': action_type,
            },
        )

    @staticmethod
    def warranty_update(user, warranty_info):
        """Create notification for warranty/support updates."""
        return NotificationService.create_and_broadcast(
            user=user,
            title="Warranty/Support Update",
            message=warranty_info.get('message', 'You have a warranty or support update.'),
            notification_type=NotificationType.WARRANTY_UPDATE,
            priority=NotificationPriority.HIGH,
            action_url=warranty_info.get('action_url'),
            metadata=warranty_info.get('metadata', {}),
        )

    @staticmethod
    def review_reminder(user, order):
        """Create notification to remind user to leave review."""
        return NotificationService.create_and_broadcast(
            user=user,
            title="Share Your Experience",
            message=f"How did you like your order? We'd love to hear your feedback on the items you purchased.",
            notification_type=NotificationType.REVIEW_REMINDER,
            priority=NotificationPriority.LOW,
            action_url=f"/orders/{order.id}/reviews",
            metadata={
                'order_id': order.id,
            },
        )
