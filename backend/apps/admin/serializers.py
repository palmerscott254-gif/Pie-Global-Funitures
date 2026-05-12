"""
Comprehensive Admin Dashboard Serializers

Includes serializers for:
- Authentication & authorization
- Role management
- Orders, messages, products
- Audit logging
- Dashboard analytics
- Alerts and notifications
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.orders.models import Order
from apps.messages.models import UserMessage
from apps.admin.models import AdminAuditLog, AdminRole, AdminAuditLog, DashboardSettings, StockAlert, ReviewRequest
from apps.products.models import Product

User = get_user_model()


# ============================================================================
# CORE ADMIN SERIALIZERS
# ============================================================================

class AdminRoleSerializer(serializers.ModelSerializer):
    """Serialize admin user roles and permissions."""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    
    class Meta:
        model = AdminRole
        fields = [
            'id', 'user', 'user_email', 'user_name', 'role',
            'can_manage_products', 'can_manage_orders', 'can_manage_customers',
            'can_manage_support', 'can_manage_delivery', 'can_view_analytics',
            'can_manage_settings', 'can_manage_coupons',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AdminUserSerializer(serializers.ModelSerializer):
    """Serializer for admin users with role information."""
    
    admin_role = AdminRoleSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'is_active', 'is_staff', 'is_superuser',
            'admin_role', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AdminLoginSerializer(serializers.Serializer):
    """Serializer for admin login credentials."""
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        """Validate admin credentials."""
        email = attrs.get('email')
        password = attrs.get('password')
        
        try:
            user = User.objects.get(email=email)
        except User.objects.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")
        
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password.")
        
        if not user.is_active:
            raise serializers.ValidationError("User account is inactive.")
        
        if not user.is_staff:
            raise serializers.ValidationError("User does not have admin access.")
        
        attrs['user'] = user
        return attrs


# ============================================================================
# ORDERS & MESSAGES
# ============================================================================

class AdminOrderSerializer(serializers.ModelSerializer):
    """Serializer for admin order view (with all fields)."""
    
    class Meta:
        model = Order
        fields = [
            'id', 'name', 'email', 'phone', 'address', 'city', 'postal_code',
            'items', 'total_amount', 'status', 'paid', 'payment_method',
            'notes', 'created_at', 'updated_at', 'item_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'item_count']


class AdminMessageSerializer(serializers.ModelSerializer):
    """Serializer for admin message view."""
    
    days_since_created = serializers.SerializerMethodField()
    
    class Meta:
        model = UserMessage
        fields = [
            'id', 'name', 'email', 'phone', 'message', 'status',
            'reply_text', 'replied_at', 'created_at', 'updated_at',
            'days_since_created'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_days_since_created(self, obj):
        """Calculate days since creation."""
        from django.utils import timezone
        return (timezone.now() - obj.created_at).days


class AdminProductSerializer(serializers.ModelSerializer):
    """Serializer for admin product management."""
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'short_description',
            'price', 'compare_at_price', 'category', 'tags',
            'main_image', 'gallery', 'stock', 'sku',
            'dimensions', 'material', 'color', 'weight',
            'featured', 'is_active', 'on_sale',
            'meta_title', 'meta_description',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class OrderStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating order status."""
    
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
    notes = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        help_text="Internal notes about the status change"
    )


class MessageReplySerializer(serializers.Serializer):
    """Serializer for replying to messages."""
    
    reply_text = serializers.CharField(
        max_length=2000,
        min_length=5,
        help_text="Reply message to send to customer"
    )
    status = serializers.ChoiceField(
        choices=UserMessage.STATUS_CHOICES,
        required=False,
        help_text="New message status"
    )


# ============================================================================
# AUDIT LOGGING
# ============================================================================

class AdminAuditLogSerializer(serializers.ModelSerializer):
    """Serializer for audit logs."""
    
    admin_user_name = serializers.CharField(
        source='admin_user.name',
        read_only=True
    )
    content_type_name = serializers.CharField(
        source='content_type.model',
        read_only=True
    )
    
    class Meta:
        model = AdminAuditLog
        fields = [
            'id', 'admin_user', 'admin_user_name', 'content_type_name',
            'object_id', 'object_repr', 'action', 'changes',
            'timestamp', 'ip_address'
        ]
        read_only_fields = fields


# ============================================================================
# ALERTS & SETTINGS
# ============================================================================

class StockAlertSerializer(serializers.ModelSerializer):
    """Serializer for stock alerts."""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    resolved_by_name = serializers.CharField(source='resolved_by.name', read_only=True)
    
    class Meta:
        model = StockAlert
        fields = [
            'id', 'product', 'product_name', 'product_sku',
            'current_stock', 'threshold', 'is_active', 'is_resolved',
            'resolved_at', 'resolved_by', 'resolved_by_name', 'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'current_stock', 'threshold']


class ReviewRequestSerializer(serializers.ModelSerializer):
    """Serializer for review requests."""
    
    order_number = serializers.SerializerMethodField()
    customer_name = serializers.CharField(source='order.name', read_only=True)
    customer_email = serializers.CharField(source='order.email', read_only=True)
    
    class Meta:
        model = ReviewRequest
        fields = [
            'id', 'order', 'order_number', 'customer_name', 'customer_email',
            'sent_at', 'responded_at', 'is_sent', 'retry_count',
            'next_retry_at', 'created_at',
        ]
        read_only_fields = fields
    
    def get_order_number(self, obj):
        return str(obj.order.id)


class DashboardSettingsSerializer(serializers.ModelSerializer):
    """Serializer for dashboard global configuration."""
    
    class Meta:
        model = DashboardSettings
        fields = [
            'dashboard_title', 'logo_url', 'favicon_url',
            'email_notifications_enabled', 'sms_notifications_enabled',
            'items_per_page', 'search_debounce_ms', 'dark_mode_enabled',
            'low_stock_threshold', 'high_order_alert_threshold',
            'max_refund_without_approval',
            'enable_support_tickets', 'enable_review_requests',
            'enable_delivery_tracking', 'enable_coupons',
            'updated_at',
        ]
        read_only_fields = ['updated_at']


# ============================================================================
# DASHBOARD ANALYTICS
# ============================================================================

class DashboardSummarySerializer(serializers.Serializer):
    """Summary metrics for dashboard overview."""
    
    total_orders = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    processing_orders = serializers.IntegerField()
    delivered_orders = serializers.IntegerField()
    cancelled_orders = serializers.IntegerField()
    
    unread_messages = serializers.IntegerField()
    total_messages = serializers.IntegerField()
    
    revenue_today = serializers.DecimalField(max_digits=12, decimal_places=2)
    revenue_this_month = serializers.DecimalField(max_digits=12, decimal_places=2)
    revenue_all_time = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    average_order_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # Recent data
    recent_orders = AdminOrderSerializer(many=True)
    recent_messages = AdminMessageSerializer(many=True)


class OrderAnalyticsSerializer(serializers.Serializer):
    """Serialize order analytics data."""
    
    date = serializers.DateField()
    order_count = serializers.IntegerField()
    revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_order_value = serializers.DecimalField(max_digits=12, decimal_places=2)


class ProductAnalyticsSerializer(serializers.Serializer):
    """Serialize product analytics data."""
    
    product_id = serializers.CharField()
    product_name = serializers.CharField()
    total_sold = serializers.IntegerField()
    revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, required=False)


class RevenueAnalyticsSerializer(serializers.Serializer):
    """Serialize revenue analytics data."""
    
    period = serializers.CharField()
    revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    orders = serializers.IntegerField()
    average_order_value = serializers.DecimalField(max_digits=12, decimal_places=2)


class AlertSerializer(serializers.Serializer):
    """Serializer for dashboard alerts."""
    
    type = serializers.CharField(
        max_length=50,
        help_text="Type: pending_orders, low_stock, unread_messages, etc"
    )
    severity = serializers.ChoiceField(
        choices=['info', 'warning', 'danger'],
        help_text="Alert severity level"
    )
    message = serializers.CharField(help_text="Human-readable message")
    count = serializers.IntegerField(help_text="Number of items")
    action_url = serializers.CharField(required=False, allow_blank=True)
