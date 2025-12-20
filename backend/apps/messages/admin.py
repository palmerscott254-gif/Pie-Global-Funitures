from django.contrib import admin
from django.utils.html import format_html
from .models import UserMessage


@admin.register(UserMessage)
class UserMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'phone', 'message')
    readonly_fields = ('created_at', 'updated_at', 'formatted_message')
    list_editable = ('status',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_per_page = 25
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone'),
            'description': 'Customer contact details'
        }),
        ('Message', {
            'fields': ('formatted_message', 'status'),
        }),
        ('Reply', {
            'fields': ('reply_text', 'replied_at'),
            'description': 'Admin response to customer'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def formatted_message(self, obj):
        """Display message with better formatting."""
        return format_html(
            '<div style="padding: 15px; background: #f9f9f9; border: 1px solid #ddd; border-radius: 5px; max-width: 600px; white-space: pre-wrap; color: #333; line-height: 1.5;">{}</div>',
            obj.message
        )
    formatted_message.short_description = 'Message Content'
