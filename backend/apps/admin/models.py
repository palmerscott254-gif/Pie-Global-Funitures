"""
Comprehensive Admin Dashboard Models

Includes:
- Admin role management with granular permissions
- Audit logging for security & compliance
- Dashboard configuration
- Review request automation
- Stock alerts
"""

from django.db import models
from django.contrib.contenttypes.models import ContentType
from apps.users.models import User
import uuid


# ============================================================================
# ADMIN ROLE & PERMISSIONS
# ============================================================================

class AdminRole(models.Model):
    """Admin user roles with granular permissions.
    
    Defines what each admin can do:
    - Super Admin: Full access to everything
    - Staff Admin: Can manage products, orders, customers
    - Support Agent: Can manage support tickets, view orders
    - Delivery Manager: Can track deliveries, update statuses
    """
    
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('staff_admin', 'Staff Admin'),
        ('support_agent', 'Support Agent'),
        ('delivery_manager', 'Delivery Manager'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_role')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff_admin')
    
    # Granular permissions (can be overridden per role)
    can_manage_products = models.BooleanField(default=False)
    can_manage_orders = models.BooleanField(default=False)
    can_manage_customers = models.BooleanField(default=False)
    can_manage_support = models.BooleanField(default=False)
    can_manage_delivery = models.BooleanField(default=False)
    can_view_analytics = models.BooleanField(default=False)
    can_manage_settings = models.BooleanField(default=False)
    can_manage_coupons = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Admin Role'
        verbose_name_plural = 'Admin Roles'
        db_table = 'admin_roles'
    
    def __str__(self):
        return f"{self.user.name} - {self.get_role_display()}"
    
    def save(self, *args, **kwargs):
        """Auto-assign permissions based on role."""
        # Reset all permissions
        self.can_manage_products = False
        self.can_manage_orders = False
        self.can_manage_customers = False
        self.can_manage_support = False
        self.can_manage_delivery = False
        self.can_view_analytics = False
        self.can_manage_settings = False
        self.can_manage_coupons = False
        
        # Assign based on role
        if self.role == 'super_admin':
            self.can_manage_products = True
            self.can_manage_orders = True
            self.can_manage_customers = True
            self.can_manage_support = True
            self.can_manage_delivery = True
            self.can_view_analytics = True
            self.can_manage_settings = True
            self.can_manage_coupons = True
        elif self.role == 'staff_admin':
            self.can_manage_products = True
            self.can_manage_orders = True
            self.can_manage_customers = True
            self.can_view_analytics = True
            self.can_manage_coupons = True
        elif self.role == 'support_agent':
            self.can_manage_support = True
            self.can_manage_orders = True
        elif self.role == 'delivery_manager':
            self.can_manage_delivery = True
            self.can_manage_orders = True
        
        super().save(*args, **kwargs)


# ============================================================================
# AUDIT LOGGING
# ============================================================================

class AdminAuditLog(models.Model):
    """Audit trail for admin actions on orders and messages.
    
    Tracks who did what, when, and on which object.
    Supports reverting changes if needed in future.
    
    Examples:
    - Admin John changed Order #123 status from pending to shipped
    - Admin Jane deleted Product #456 (Lounge Chair)
    - Admin Bob replied to customer message with answer
    """
    
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('status_change', 'Status Changed'),
        ('marked_paid', 'Marked as Paid'),
        ('message_reply', 'Message Replied'),
        ('message_resolved', 'Message Resolved'),
        ('media_upload', 'Media Uploaded'),
        ('media_delete', 'Media Deleted'),
    ]

    # Who did it
    admin_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admin_audit_logs',
        help_text="Admin user who performed the action"
    )

    # What object was affected
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255)  # Changed to CharField to support UUIDs

    # What changed
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        db_index=True
    )
    
    # Human readable object representation
    object_repr = models.CharField(max_length=255, blank=True)
    
    # Store old and new values for auditing
    changes = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON of {field: {old: value, new: value}}"
    )

    # When & where
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Admin Audit Log'
        verbose_name_plural = 'Admin Audit Logs'
        db_table = 'admin_audit_logs'
        indexes = [
            models.Index(fields=['admin_user', '-timestamp']),
            models.Index(fields=['content_type', 'action', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]

    def __str__(self):
        admin_name = getattr(self.admin_user, 'name', 'Unknown admin')
        return f"{self.get_action_display()} by {admin_name} on {self.object_repr or self.content_type}"


# ============================================================================
# DASHBOARD CONFIGURATION
# ============================================================================

class DashboardSettings(models.Model):
    """Global admin dashboard configuration (singleton pattern).
    
    Stores settings applied to entire dashboard:
    - Branding (logo, title)
    - Notification preferences
    - Display preferences
    - Alert thresholds
    """
    
    # Branding
    dashboard_title = models.CharField(
        max_length=255,
        default='Pie Global Admin Dashboard'
    )
    logo_url = models.URLField(blank=True)
    favicon_url = models.URLField(blank=True)
    
    # Notification settings
    email_notifications_enabled = models.BooleanField(default=True)
    sms_notifications_enabled = models.BooleanField(default=False)
    
    # Display settings
    items_per_page = models.PositiveIntegerField(default=25)
    search_debounce_ms = models.PositiveIntegerField(default=300)
    dark_mode_enabled = models.BooleanField(default=False)
    
    # Alert thresholds
    low_stock_threshold = models.PositiveIntegerField(
        default=10,
        help_text="Alert when product stock falls below this"
    )
    high_order_alert_threshold = models.PositiveIntegerField(
        default=100,
        help_text="Alert when order total exceeds this"
    )
    max_refund_without_approval = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=500.00,
        help_text="Refunds above this require approval"
    )
    
    # Feature flags
    enable_support_tickets = models.BooleanField(default=True)
    enable_review_requests = models.BooleanField(default=True)
    enable_delivery_tracking = models.BooleanField(default=True)
    enable_coupons = models.BooleanField(default=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dashboard_settings'
        verbose_name = 'Dashboard Settings'
        verbose_name_plural = 'Dashboard Settings'
    
    def __str__(self):
        return self.dashboard_title
    
    def save(self, *args, **kwargs):
        """Ensure only one instance exists (singleton pattern)."""
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create singleton instance."""
        instance, created = cls.objects.get_or_create(pk=1)
        return instance


# ============================================================================
# AUTOMATED REQUESTS
# ============================================================================

class ReviewRequest(models.Model):
    """Auto-request reviews from customers after delivery.
    
    When order is marked delivered, automatically queue review request.
    Sends email to customer asking for feedback on products.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='review_request'
    )
    
    # Status tracking
    sent_at = models.DateTimeField(null=True, blank=True, db_index=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    is_sent = models.BooleanField(default=False, db_index=True)
    
    # Retry logic
    retry_count = models.PositiveIntegerField(default=0)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Review Request'
        verbose_name_plural = 'Review Requests'
        db_table = 'review_requests'
        indexes = [
            models.Index(fields=['is_sent', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"Review Request for Order #{self.order.id}"


class StockAlert(models.Model):
    """Alert when product stock falls below threshold.
    
    Helps admin track which products need restocking.
    Can be dismissed or marked as resolved.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='stock_alerts'
    )
    
    current_stock = models.PositiveIntegerField()
    threshold = models.PositiveIntegerField()
    
    # Status
    is_active = models.BooleanField(default=True, db_index=True)
    is_resolved = models.BooleanField(default=False, db_index=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        verbose_name = 'Stock Alert'
        verbose_name_plural = 'Stock Alerts'
        db_table = 'stock_alerts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', '-created_at']),
            models.Index(fields=['product', 'is_active']),
        ]
    
    def __str__(self):
        return f"Stock Alert: {self.product.name} ({self.current_stock})"
