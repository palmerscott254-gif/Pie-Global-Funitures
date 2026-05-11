from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()


class NotificationType(models.TextChoices):
    """
    Enumeration of all notification types in the system.
    Each type triggers specific business logic.
    """
    ORDER_CONFIRMED = 'ORDER_CONFIRMED', 'Order Confirmed'
    PAYMENT_RECEIVED = 'PAYMENT_RECEIVED', 'Payment Received'
    ORDER_SHIPPED = 'ORDER_SHIPPED', 'Order Shipped'
    DELIVERY_UPDATE = 'DELIVERY_UPDATE', 'Delivery Update'
    DELIVERED = 'DELIVERED', 'Delivered Successfully'
    DELIVERY_FAILED = 'DELIVERY_FAILED', 'Failed Delivery Attempt'
    RESTOCKED_ITEM = 'RESTOCKED_ITEM', 'Item Restocked'
    ADMIN_MESSAGE = 'ADMIN_MESSAGE', 'Admin Message'
    WARRANTY_UPDATE = 'WARRANTY_UPDATE', 'Warranty/Support Update'
    REFUND_STATUS = 'REFUND_STATUS', 'Refund Status'
    INVOICE_READY = 'INVOICE_READY', 'Invoice Ready'
    DELIVERY_ETA = 'DELIVERY_ETA', 'Delivery ETA'
    LOYALTY_POINTS = 'LOYALTY_POINTS', 'Loyalty/Reward Points'
    REVIEW_REMINDER = 'REVIEW_REMINDER', 'Review Reminder'


class NotificationPriority(models.TextChoices):
    """
    Priority levels for notifications.
    Used to filter and sort notifications by importance.
    Affects UI rendering and notification timing.
    """
    LOW = 'LOW', 'Low'
    NORMAL = 'NORMAL', 'Normal'
    HIGH = 'HIGH', 'High'
    URGENT = 'URGENT', 'Urgent'


class Notification(models.Model):
    """
    Core notification model storing all notification data.
    
    Design Principles:
    - Denormalized fields (title, message) for fast retrieval
    - JSON metadata for flexible, type-specific data
    - Soft delete support via is_deleted flag
    - Efficient querying with proper indexing
    - Tracks read status for unread badge calculation
    """

    # Primary identifiers
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    
    # User and content
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text='User receiving the notification'
    )
    
    # Notification content
    title = models.CharField(
        max_length=255,
        help_text='Brief notification title (displayed in dropdown)'
    )
    message = models.TextField(
        help_text='Full notification message body'
    )
    
    # Notification classification
    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        db_index=True,
        help_text='Type determines automatic trigger and context'
    )
    priority = models.CharField(
        max_length=20,
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL,
        db_index=True,
        help_text='Priority level affects UI highlighting'
    )
    
    # Read status tracking
    is_read = models.BooleanField(
        default=False,
        db_index=True,
        help_text='Whether user has seen this notification'
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timestamp when notification was marked as read'
    )
    
    # Soft delete support
    is_deleted = models.BooleanField(
        default=False,
        db_index=True,
        help_text='Soft delete flag for data retention'
    )
    
    # Action and navigation
    action_url = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text='URL to navigate to when notification is clicked'
    )
    
    # Flexible metadata storage
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Type-specific data (order_id, product_id, tracking_info, etc.)'
    )
    
    # Lifecycle tracking
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='When notification was created'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Last update timestamp'
    )
    
    # Expiration support for temporary notifications
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Optional expiration for promotional/temporary notifications'
    )

    class Meta:
        # Efficient querying for common patterns
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read', '-created_at']),
            models.Index(fields=['user', 'is_deleted', '-created_at']),
            models.Index(fields=['notification_type', 'created_at']),
            models.Index(fields=['priority', '-created_at']),
        ]
        
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        
        # Enable soft delete filtering by default
        # Use unfiltered queryset with .all() for admin
        constraints = []

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.user.username}"

    def mark_as_read(self):
        """Mark this notification as read and record the time."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at', 'updated_at'])

    def is_expired(self):
        """Check if notification has expired."""
        if self.expires_at is None:
            return False
        return timezone.now() > self.expires_at

    def get_priority_level(self):
        """Return numeric priority level for sorting (higher = more urgent)."""
        priority_map = {
            NotificationPriority.LOW: 1,
            NotificationPriority.NORMAL: 2,
            NotificationPriority.HIGH: 3,
            NotificationPriority.URGENT: 4,
        }
        return priority_map.get(self.priority, 2)

    @classmethod
    def get_active_notifications(cls, user):
        """
        Get non-deleted, non-expired notifications for a user.
        Optimized query for frontend dropdown.
        """
        return cls.objects.filter(
            user=user,
            is_deleted=False
        ).exclude(
            expires_at__lt=timezone.now()
        ).select_related('user').only(
            'id', 'uuid', 'title', 'message', 'notification_type',
            'priority', 'is_read', 'action_url', 'created_at', 'metadata'
        )

    @classmethod
    def get_unread_count(cls, user):
        """
        Get unread notification count for real-time badge.
        Highly optimized - uses .count() directly on database.
        """
        return cls.objects.filter(
            user=user,
            is_deleted=False,
            is_read=False
        ).exclude(
            expires_at__lt=timezone.now()
        ).count()


class NotificationPreference(models.Model):
    """
    User preferences for notification behavior.
    Allows fine-grained control over notification delivery.
    
    Future Enhancement: Add channels (email, SMS, push, web)
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preference',
        help_text='User whose preferences these are'
    )
    
    # Toggles for notification types
    order_notifications = models.BooleanField(
        default=True,
        help_text='Receive order confirmation, shipped, delivered notifications'
    )
    promotional_notifications = models.BooleanField(
        default=True,
        help_text='Receive promotional and loyalty point notifications'
    )
    admin_notifications = models.BooleanField(
        default=True,
        help_text='Receive messages from administrators'
    )
    support_notifications = models.BooleanField(
        default=True,
        help_text='Receive warranty and support updates'
    )
    
    # Delivery preferences
    quiet_hours_enabled = models.BooleanField(
        default=False,
        help_text='Whether quiet hours are enabled'
    )
    quiet_hours_start = models.TimeField(
        null=True,
        blank=True,
        help_text='Start time for quiet hours (e.g., 22:00)'
    )
    quiet_hours_end = models.TimeField(
        null=True,
        blank=True,
        help_text='End time for quiet hours (e.g., 08:00)'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'

    def __str__(self):
        return f"Notification preferences for {self.user.username}"

    def should_notify(self, notification_type):
        """
        Determine if user should receive this notification type
        based on preferences.
        """
        type_to_preference = {
            NotificationType.ORDER_CONFIRMED: 'order_notifications',
            NotificationType.PAYMENT_RECEIVED: 'order_notifications',
            NotificationType.ORDER_SHIPPED: 'order_notifications',
            NotificationType.DELIVERY_UPDATE: 'order_notifications',
            NotificationType.DELIVERED: 'order_notifications',
            NotificationType.DELIVERY_FAILED: 'order_notifications',
            NotificationType.ADMIN_MESSAGE: 'admin_notifications',
            NotificationType.WARRANTY_UPDATE: 'support_notifications',
            NotificationType.REFUND_STATUS: 'order_notifications',
            NotificationType.LOYALTY_POINTS: 'promotional_notifications',
            NotificationType.RESTOCKED_ITEM: 'promotional_notifications',
            NotificationType.REVIEW_REMINDER: 'promotional_notifications',
            NotificationType.INVOICE_READY: 'order_notifications',
            NotificationType.DELIVERY_ETA: 'order_notifications',
        }
        
        pref_field = type_to_preference.get(notification_type, 'order_notifications')
        return getattr(self, pref_field, True)


class NotificationLog(models.Model):
    """
    Optional model for audit logging of notification delivery.
    Useful for debugging delivery issues and compliance.
    
    Can be indexed for analytics: "Which notifications are most frequently opened?"
    """
    
    DELIVERY_STATUS_CHOICES = [
        ('CREATED', 'Created'),
        ('QUEUED', 'Queued'),
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('FAILED', 'Failed'),
    ]
    
    notification = models.OneToOneField(
        Notification,
        on_delete=models.CASCADE,
        related_name='log',
        help_text='Associated notification'
    )
    
    delivery_status = models.CharField(
        max_length=20,
        choices=DELIVERY_STATUS_CHOICES,
        default='CREATED',
        help_text='Current delivery status'
    )
    
    websocket_delivered = models.BooleanField(
        default=False,
        help_text='Whether delivered via WebSocket'
    )
    
    delivery_attempts = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text='Number of delivery attempts'
    )
    
    last_error = models.TextField(
        blank=True,
        help_text='Last error message if delivery failed'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Notification Log'
        verbose_name_plural = 'Notification Logs'

    def __str__(self):
        return f"Log for notification {self.notification.id}"
