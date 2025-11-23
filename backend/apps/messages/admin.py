from django.contrib import admin
from django.utils.html import format_html
from .models import UserMessage


@admin.register(UserMessage)
class UserMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'reply_status', 'created_at')
    list_filter = ('replied', 'created_at')
    search_fields = ('name', 'email', 'phone', 'message')
    readonly_fields = ('created_at', 'formatted_message')
    list_editable = ('replied',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_per_page = 25
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone'),
            'description': 'Customer contact details'
        }),
        ('Message', {
            'fields': ('formatted_message',),
            'description': 'Customer inquiry or feedback'
        }),
        ('Reply', {
            'fields': ('replied', 'reply_text'),
            'description': 'Mark as replied and add response notes'
        }),
        ('Meta', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def reply_status(self, obj):
        """Display reply status with color coding"""
        if obj.replied:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Replied</span>'
            )
        return format_html(
            '<span style="color: orange; font-weight: bold;">⏳ Pending</span>'
        )
    reply_status.short_description = 'Status'
    
    def formatted_message(self, obj):
        """Display message with better formatting"""
        return format_html(
            '<div style="padding: 10px; background: #f5f5f5; border-radius: 5px; max-width: 600px;">{}</div>',
            obj.message
        )
    formatted_message.short_description = 'Message Content'
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related()
