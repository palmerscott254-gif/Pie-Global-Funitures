from rest_framework import serializers
from apps.orders.models import Order
from apps.messages.models import UserMessage
from apps.admin.models import AdminAuditLog
from apps.users.models import User


class AdminUserSerializer(serializers.ModelSerializer):
    """Minimal user serializer for admin context."""
    
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'is_staff', 'is_superuser']
        read_only_fields = fields


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


class AlertSerializer(serializers.Serializer):
    """Serializer for dashboard alerts."""
    
    type = serializers.CharField(
        max_length=50,
        help_text="Type of alert: pending_orders, unread_messages, etc"
    )
    severity = serializers.ChoiceField(
        choices=['info', 'warning', 'danger'],
        help_text="Alert severity"
    )
    message = serializers.CharField(
        help_text="Human-readable alert message"
    )
    count = serializers.IntegerField(
        help_text="Number of items for this alert"
    )
    action_url = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Optional URL to navigate to"
    )


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
            'id', 'admin_user_name', 'content_type_name', 'object_id',
            'action', 'changes', 'timestamp', 'ip_address'
        ]
        read_only_fields = fields
