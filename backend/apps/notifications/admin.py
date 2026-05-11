from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Q
from .models import Notification, NotificationPreference, NotificationLog


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Admin interface for managing notifications.
    Provides filtering, searching, and bulk actions.
    """
    
    list_display = (
        'id',
        'user',
        'notification_type',
        'title',
        'priority_badge',
        'read_status',
        'created_at_formatted',
    )
    
    list_filter = (
        'notification_type',
        'priority',
        'is_read',
        'is_deleted',
        'created_at',
    )
    
    search_fields = (
        'user__username',
        'user__email',
        'title',
        'message',
        'notification_type',
    )
    
    readonly_fields = (
        'id',
        'uuid',
        'created_at',
        'updated_at',
        'read_at',
        'message_preview',
    )
    
    fieldsets = (
        ('Notification Info', {
            'fields': ('id', 'uuid', 'user', 'title')
        }),
        ('Content', {
            'fields': ('notification_type', 'message_preview', 'action_url')
        }),
        ('Classification', {
            'fields': ('priority', 'metadata')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at', 'is_deleted')
        }),
        ('Lifecycle', {
            'fields': ('expires_at', 'created_at', 'updated_at')
        }),
    )
    
    actions = (
        'mark_as_read',
        'mark_as_unread',
        'delete_notifications',
    )
    
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    def priority_badge(self, obj):
        """Display priority with color-coded badge."""
        colors = {
            'LOW': '#90EE90',         # Light green
            'NORMAL': '#87CEEB',      # Sky blue
            'HIGH': '#FFD700',        # Gold
            'URGENT': '#FF6347',      # Tomato red
        }
        
        color = colors.get(obj.priority, '#87CEEB')
        return format_html(
            '<span style="background-color: {}; padding: 3px 10px; '
            'border-radius: 3px; color: white; font-weight: bold;">{}</span>',
            color,
            obj.get_priority_display()
        )
    
    priority_badge.short_description = 'Priority'

    def read_status(self, obj):
        """Display read/unread status with icon."""
        if obj.is_read:
            return format_html('✅ Read')
        else:
            return format_html('📬 Unread')
    
    read_status.short_description = 'Status'

    def created_at_formatted(self, obj):
        """Display created_at with relative time."""
        from django.utils.timesince import timesince
        return f"{obj.created_at.strftime('%b %d, %Y')} ({timesince(obj.created_at)} ago)"
    
    created_at_formatted.short_description = 'Created'

    def message_preview(self, obj):
        """Display message preview (first 200 chars)."""
        if len(obj.message) > 200:
            return obj.message[:200] + '...'
        return obj.message
    
    message_preview.short_description = 'Message'

    def mark_as_read(self, request, queryset):
        """Bulk action: Mark selected notifications as read."""
        from django.utils import timezone
        count = queryset.filter(is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
        self.message_user(request, f'{count} notification(s) marked as read.')
    
    mark_as_read.short_description = "Mark selected as read"

    def mark_as_unread(self, request, queryset):
        """Bulk action: Mark selected notifications as unread."""
        count = queryset.filter(is_read=True).update(is_read=False, read_at=None)
        self.message_user(request, f'{count} notification(s) marked as unread.')
    
    mark_as_unread.short_description = "Mark selected as unread"

    def delete_notifications(self, request, queryset):
        """Bulk action: Soft delete selected notifications."""
        from django.utils import timezone
        count = queryset.filter(is_deleted=False).update(
            is_deleted=True,
            updated_at=timezone.now()
        )
        self.message_user(request, f'{count} notification(s) deleted.')
    
    delete_notifications.short_description = "Delete selected notifications"


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """
    Admin interface for managing user notification preferences.
    """
    
    list_display = (
        'user',
        'order_notifications',
        'promotional_notifications',
        'admin_notifications',
        'support_notifications',
        'quiet_hours_enabled',
    )
    
    list_filter = (
        'order_notifications',
        'promotional_notifications',
        'admin_notifications',
        'support_notifications',
        'quiet_hours_enabled',
        'updated_at',
    )
    
    search_fields = (
        'user__username',
        'user__email',
    )
    
    readonly_fields = (
        'created_at',
        'updated_at',
    )
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Notification Types', {
            'fields': (
                'order_notifications',
                'promotional_notifications',
                'admin_notifications',
                'support_notifications',
            )
        }),
        ('Quiet Hours', {
            'fields': (
                'quiet_hours_enabled',
                'quiet_hours_start',
                'quiet_hours_end',
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-updated_at',)


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    """
    Admin interface for viewing notification delivery logs.
    Used for debugging and analytics.
    """
    
    list_display = (
        'notification_id',
        'notification_title',
        'delivery_status',
        'delivery_attempts',
        'websocket_delivered',
        'created_at_formatted',
    )
    
    list_filter = (
        'delivery_status',
        'websocket_delivered',
        'created_at',
    )
    
    search_fields = (
        'notification__title',
        'notification__user__username',
        'last_error',
    )
    
    readonly_fields = (
        'notification',
        'created_at',
        'updated_at',
        'last_error_display',
    )
    
    fieldsets = (
        ('Notification', {
            'fields': ('notification', 'notification_title')
        }),
        ('Delivery Status', {
            'fields': (
                'delivery_status',
                'delivery_attempts',
                'websocket_delivered',
            )
        }),
        ('Error Details', {
            'fields': ('last_error_display',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    def notification_title(self, obj):
        """Display notification title."""
        return obj.notification.title
    notification_title.short_description = 'Notification Title'

    def created_at_formatted(self, obj):
        """Display created_at with relative time."""
        from django.utils.timesince import timesince
        return f"{obj.created_at.strftime('%b %d, %Y %H:%M')} ({timesince(obj.created_at)} ago)"
    
    created_at_formatted.short_description = 'Created'

    def last_error_display(self, obj):
        """Display last error in a readable way."""
        if not obj.last_error:
            return "No errors"
        return f"<pre>{obj.last_error}</pre>"
    
    last_error_display.short_description = 'Last Error'

    def has_add_permission(self, request):
        """Prevent manual creation of logs (auto-generated only)."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of logs (for audit trail)."""
        return False
