from rest_framework import serializers
from django.utils import timezone
from django.utils.timesince import timesince
from .models import Notification, NotificationPreference, NotificationLog


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for Notification model.
    Provides clean API response with human-readable timestamps.
    Optimized for frontend dropdown rendering.
    """
    
    # Human-readable timestamp (e.g., "2 minutes ago")
    created_at_relative = serializers.SerializerMethodField()
    
    # Display-friendly priority label
    priority_display = serializers.CharField(
        source='get_priority_display',
        read_only=True
    )
    
    # Display-friendly type label
    type_display = serializers.CharField(
        source='get_notification_type_display',
        read_only=True
    )

    class Meta:
        model = Notification
        fields = [
            'id',
            'uuid',
            'title',
            'message',
            'notification_type',
            'type_display',
            'priority',
            'priority_display',
            'is_read',
            'read_at',
            'action_url',
            'metadata',
            'created_at',
            'created_at_relative',
            'is_expired'
        ]
        read_only_fields = [
            'id', 'uuid', 'created_at', 'is_expired'
        ]

    def get_created_at_relative(self, obj):
        """
        Convert created_at to human-readable format.
        Example: "2 minutes ago", "1 day ago"
        Frontend can use this directly or convert to locale-specific format.
        """
        return timesince(obj.created_at) + ' ago'


class NotificationListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for notification list endpoint.
    Excludes large metadata field to reduce payload size.
    Used for paginated list responses.
    """
    
    created_at_relative = serializers.SerializerMethodField()
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    type_display = serializers.CharField(source='get_notification_type_display', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id',
            'uuid',
            'title',
            'notification_type',
            'type_display',
            'priority',
            'priority_display',
            'is_read',
            'action_url',
            'created_at_relative',
            'created_at'
        ]
        read_only_fields = fields

    def get_created_at_relative(self, obj):
        return timesince(obj.created_at) + ' ago'


class NotificationDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer with all fields including metadata.
    Used when fetching specific notification details.
    """
    
    created_at_relative = serializers.SerializerMethodField()
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    type_display = serializers.CharField(source='get_notification_type_display', read_only=True)

    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['id', 'uuid', 'user', 'created_at', 'updated_at', 'read_at']

    def get_created_at_relative(self, obj):
        return timesince(obj.created_at) + ' ago'


class UnreadCountSerializer(serializers.Serializer):
    """
    Simple serializer for unread count endpoint.
    Used by frontend for badge updates.
    """
    unread_count = serializers.IntegerField()
    
    def to_representation(self, instance):
        """
        Ensure we return the actual count value.
        Instance is passed as {'unread_count': <value>}
        """
        return instance


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """
    Serializer for user notification preferences.
    Allows users to customize which notifications they receive.
    """
    
    user_username = serializers.CharField(
        source='user.username',
        read_only=True
    )

    class Meta:
        model = NotificationPreference
        fields = [
            'id',
            'user_username',
            'order_notifications',
            'promotional_notifications',
            'admin_notifications',
            'support_notifications',
            'quiet_hours_enabled',
            'quiet_hours_start',
            'quiet_hours_end',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Validate that if quiet_hours_enabled is True,
        both start and end times must be provided.
        """
        quiet_hours_enabled = data.get('quiet_hours_enabled', self.instance.quiet_hours_enabled)
        quiet_hours_start = data.get('quiet_hours_start', self.instance.quiet_hours_start)
        quiet_hours_end = data.get('quiet_hours_end', self.instance.quiet_hours_end)
        
        if quiet_hours_enabled and (not quiet_hours_start or not quiet_hours_end):
            raise serializers.ValidationError(
                "Both quiet_hours_start and quiet_hours_end must be provided when quiet_hours_enabled is True"
            )
        
        return data


class NotificationLogSerializer(serializers.ModelSerializer):
    """
    Serializer for notification delivery logs.
    Admin use only for debugging and analytics.
    """
    
    notification_title = serializers.CharField(
        source='notification.title',
        read_only=True
    )

    class Meta:
        model = NotificationLog
        fields = [
            'id',
            'notification',
            'notification_title',
            'delivery_status',
            'websocket_delivered',
            'delivery_attempts',
            'last_error',
            'created_at',
            'updated_at'
        ]
        read_only_fields = fields


class BulkNotificationActionSerializer(serializers.Serializer):
    """
    Serializer for bulk operations on notifications.
    Used for marking all as read, deleting multiple, etc.
    """
    
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text='List of notification IDs to act upon'
    )
    action = serializers.ChoiceField(
        choices=['mark_read', 'mark_unread', 'delete'],
        help_text='Action to perform on notifications'
    )

    def validate_notification_ids(self, value):
        if not value:
            raise serializers.ValidationError("At least one notification ID must be provided")
        if len(value) > 100:
            raise serializers.ValidationError("Maximum 100 notifications can be affected at once")
        return value


class AdminBroadcastNotificationSerializer(serializers.Serializer):
    """
    Serializer for admin broadcasting notifications to users.
    Supports single user, multiple users, or all users.
    """
    
    title = serializers.CharField(max_length=255, required=True)
    message = serializers.CharField(required=True)
    
    # Recipient selection
    recipient_type = serializers.ChoiceField(
        choices=['single', 'multiple', 'all'],
        required=True,
        help_text='Type of recipients'
    )
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        help_text='List of user IDs (required if recipient_type is "single" or "multiple")'
    )
    
    # Optional fields
    action_url = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True
    )
    priority = serializers.ChoiceField(
        choices=['LOW', 'NORMAL', 'HIGH', 'URGENT'],
        default='NORMAL'
    )
    metadata = serializers.JSONField(
        required=False,
        default=dict
    )
    
    expires_in_hours = serializers.IntegerField(
        required=False,
        help_text='Hours until notification expires'
    )

    def validate(self, data):
        """
        Validate recipient selection logic.
        """
        recipient_type = data.get('recipient_type')
        user_ids = data.get('user_ids', [])
        
        if recipient_type in ['single', 'multiple'] and not user_ids:
            raise serializers.ValidationError(
                {
                    'user_ids': f'User IDs must be provided when recipient_type is "{recipient_type}"'
                }
            )
        
        if recipient_type == 'single' and len(user_ids) != 1:
            raise serializers.ValidationError(
                {'user_ids': 'Exactly one user ID must be provided for "single" recipient type'}
            )
        
        return data
