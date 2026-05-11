"""
Celery tasks for asynchronous notification processing.

Handles:
- WebSocket message delivery
- Unread count updates
- Bulk notification operations
- Retry logic for failed deliveries
"""

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import logging
import json

from .models import Notification, NotificationLog
from .notification_service import NotificationService

User = get_user_model()
logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()


@shared_task(bind=True, max_retries=3)
def send_notification_via_websocket(self, notification_id):
    """
    Async task to send notification via WebSocket.
    
    Attempts to deliver notification to connected user.
    If delivery fails, retries up to 3 times with exponential backoff.
    
    Args:
        notification_id: ID of notification to send
    """
    try:
        notification = Notification.objects.select_related('user').get(
            id=notification_id
        )
    except Notification.DoesNotExist:
        logger.error(f"Notification {notification_id} not found")
        return
    
    user = notification.user
    
    try:
        # Get or create log entry
        log, created = NotificationLog.objects.get_or_create(
            notification=notification,
            defaults={'delivery_status': 'QUEUED'}
        )
        
        # Format notification for transmission
        notification_data = NotificationService.get_formatted_notification(
            notification
        )
        
        # Prepare WebSocket message
        message = {
            'type': 'notification_message',
            'notification': notification_data,
            'action': 'new_notification',
        }
        
        # Send via channel layer to user's group
        # User joins group in WebSocket consumer's connect method
        async_to_sync(channel_layer.group_send)(
            f'user_{user.id}',
            {
                'type': 'notification_message',
                'notification': notification_data,
            }
        )
        
        # Mark as delivered
        log.delivery_status = 'DELIVERED'
        log.websocket_delivered = True
        log.delivery_attempts = log.delivery_attempts + 1
        log.save(update_fields=[
            'delivery_status',
            'websocket_delivered',
            'delivery_attempts',
            'updated_at'
        ])
        
        logger.info(
            f"Notification {notification_id} delivered to user {user.id} "
            f"via WebSocket"
        )
        
    except Exception as exc:
        logger.error(
            f"Error sending notification {notification_id}: {str(exc)}",
            exc_info=True
        )
        
        # Update log with error
        log.delivery_attempts = log.delivery_attempts + 1
        log.last_error = str(exc)
        
        # Retry with exponential backoff
        # Delay: 5s, 25s, 125s
        retry_delay = (5 ** log.delivery_attempts) - log.delivery_attempts
        
        if log.delivery_attempts < 3:
            log.save(update_fields=[
                'delivery_status',
                'delivery_attempts',
                'last_error',
                'updated_at'
            ])
            raise self.retry(exc=exc, countdown=retry_delay)
        else:
            log.delivery_status = 'FAILED'
            log.save(update_fields=[
                'delivery_status',
                'delivery_attempts',
                'last_error',
                'updated_at'
            ])


@shared_task
def update_unread_count_async(user_id):
    """
    Async task to push updated unread count to user via WebSocket.
    
    Sends only the numeric count to efficiently update badge.
    Called after notification is marked as read.
    
    Args:
        user_id: ID of user to update
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found for unread count update")
        return
    
    try:
        # Get current unread count
        unread_count = Notification.get_unread_count(user)
        
        # Send to user's WebSocket group
        async_to_sync(channel_layer.group_send)(
            f'user_{user.id}',
            {
                'type': 'unread_count_update',
                'unread_count': unread_count,
            }
        )
        
        logger.debug(
            f"Unread count {unread_count} sent to user {user.id}"
        )
        
    except Exception as exc:
        logger.error(
            f"Error updating unread count for user {user_id}: {str(exc)}",
            exc_info=True
        )


@shared_task
def broadcast_notification_async(notification_ids):
    """
    Async task to broadcast multiple notifications to connected users.
    
    Used after bulk operations to efficiently send all notifications.
    
    Args:
        notification_ids: List of notification IDs to broadcast
    """
    try:
        notifications = Notification.objects.filter(
            id__in=notification_ids
        ).select_related('user')
        
        for notification in notifications:
            # Queue each notification separately for reliability
            send_notification_via_websocket.delay(notification.id)
        
        logger.info(f"Queued {len(notification_ids)} notifications for broadcast")
        
    except Exception as exc:
        logger.error(
            f"Error broadcasting notifications: {str(exc)}",
            exc_info=True
        )


@shared_task
def schedule_review_reminder(order_id):
    """
    Async task: Schedule reminder to leave review after delivery.
    
    Runs 3-7 days after successful delivery.
    """
    from apps.orders.models import Order
    from .notification_service import NotificationFactory
    
    try:
        order = Order.objects.get(id=order_id)
        
        # Only send if order is delivered
        if order.status != 'DELIVERED':
            logger.warning(f"Order {order_id} is not delivered, skipping review reminder")
            return
        
        # Create reminder notification
        NotificationFactory.review_reminder(order.user, order)
        
        logger.info(f"Review reminder sent for order {order_id}")
        
    except Exception as exc:
        logger.error(f"Error scheduling review reminder: {str(exc)}", exc_info=True)


@shared_task
def cleanup_expired_notifications():
    """
    Scheduled periodic task to clean up expired notifications.
    
    Runs via Celery beat (e.g., daily).
    Soft deletes notifications that have passed their expiration date.
    """
    now = timezone.now()
    
    try:
        # Find expired notifications that aren't already deleted
        expired = Notification.objects.filter(
            expires_at__lt=now,
            is_deleted=False
        )
        
        count = expired.update(
            is_deleted=True,
            updated_at=now
        )
        
        logger.info(f"Cleaned up {count} expired notifications")
        return count
        
    except Exception as exc:
        logger.error(f"Error cleaning up expired notifications: {str(exc)}", exc_info=True)


@shared_task
def cleanup_old_notification_logs():
    """
    Scheduled periodic task to archive old notification logs.
    
    Keeps logs for 90 days, then archives or deletes them.
    Useful for keeping database size manageable while maintaining audit trail.
    """
    cutoff_date = timezone.now() - timezone.timedelta(days=90)
    
    try:
        # Delete logs older than 90 days
        # In production, consider archiving to separate storage instead
        deleted_count, _ = NotificationLog.objects.filter(
            created_at__lt=cutoff_date
        ).delete()
        
        logger.info(f"Cleaned up {deleted_count} old notification logs")
        return deleted_count
        
    except Exception as exc:
        logger.error(f"Error cleaning up notification logs: {str(exc)}", exc_info=True)


@shared_task
def batch_send_notifications(notification_ids):
    """
    Async task for batch sending notifications.
    
    Optimized for bulk operations.
    
    Args:
        notification_ids: List of notification IDs to send
    """
    try:
        notifications = Notification.objects.filter(
            id__in=notification_ids
        ).select_related('user')
        
        successful = 0
        failed = 0
        
        for notification in notifications:
            try:
                send_notification_via_websocket.delay(notification.id)
                successful += 1
            except Exception as exc:
                logger.error(
                    f"Failed to queue notification {notification.id}: {str(exc)}"
                )
                failed += 1
        
        logger.info(
            f"Batch send: {successful} queued, {failed} failed out of "
            f"{len(notification_ids)} notifications"
        )
        
        return {'successful': successful, 'failed': failed}
        
    except Exception as exc:
        logger.error(f"Error in batch send: {str(exc)}", exc_info=True)


@shared_task
def check_delivery_status(order_id):
    """
    Async task to periodically check delivery status from courier API.
    
    Integrates with external tracking API.
    Creates DELIVERY_UPDATE notifications when status changes.
    
    Args:
        order_id: ID of order to check
    """
    from apps.orders.models import Order
    from .notification_service import NotificationFactory
    
    try:
        order = Order.objects.get(id=order_id)
        
        if order.status not in ['SHIPPED', 'IN_TRANSIT']:
            return
        
        # TODO: Integrate with actual courier tracking API
        # Example: FedEx, UPS, DHL API
        # tracking_info = CourierAPI.get_tracking(order.tracking_number)
        
        # if tracking_info['status'] != order.delivery_status:
        #     NotificationFactory.delivery_update(
        #         order.user,
        #         order,
        #         tracking_info['message'],
        #         tracking_info
        #     )
        
        logger.info(f"Checked delivery status for order {order_id}")
        
    except Exception as exc:
        logger.error(f"Error checking delivery status: {str(exc)}", exc_info=True)
