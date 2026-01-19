from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import UserMessage


@admin.register(UserMessage)
class UserMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone_display', 'status_badge', 'created_at', 'action_links')
    list_filter = ('status', 'created_at', 'replied_at')
    search_fields = ('name', 'email', 'phone', 'message')
    readonly_fields = ('id', 'created_at', 'updated_at', 'formatted_message', 'contact_info')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_per_page = 25
    actions = ['mark_as_read', 'mark_as_resolved']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('contact_info',),
            'description': 'Customer contact details'
        }),
        ('Message', {
            'fields': ('formatted_message', 'status'),
        }),
        ('Reply', {
            'fields': ('reply_text', 'replied_at'),
            'description': 'Admin response to customer (optional)'
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def contact_info(self, obj):
        """Display formatted contact information."""
        return format_html(
            '<div style="padding: 10px; background: #f5f5f5; border-radius: 5px;">'
            '<strong>Name:</strong> {}<br>'
            '<strong>Email:</strong> <a href="mailto:{}">{}</a><br>'
            '<strong>Phone:</strong> {}'
            '</div>',
            obj.name,
            obj.email or '',
            obj.email or 'N/A',
            obj.phone or 'N/A'
        )
    contact_info.short_description = 'Contact Details'
    
    def formatted_message(self, obj):
        """Display message with better formatting."""
        return format_html(
            '<div style="padding: 15px; background: #f9f9f9; border: 1px solid #ddd; border-radius: 5px; max-width: 600px; white-space: pre-wrap; color: #333; line-height: 1.5;">{}</div>',
            obj.message
        )
    formatted_message.short_description = 'Message Content'
    
    def phone_display(self, obj):
        """Display phone number truncated."""
        return obj.phone[:15] if obj.phone else '-'
    phone_display.short_description = 'Phone'
    
    def status_badge(self, obj):
        """Display status with colored badge."""
        colors = {
            'new': '#dc3545',      # Red
            'read': '#ffc107',     # Yellow
            'replied': '#28a745',  # Green
            'resolved': '#6c757d', # Gray
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; border-radius: 3px; font-size: 12px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def action_links(self, obj):
        """Display quick action links."""
        return format_html(
            '<a href="mailto:{}" style="margin-right: 10px;">📧 Email</a>',
            obj.email or ''
        )
    action_links.short_description = 'Actions'
    
    def mark_as_read(self, request, queryset):
        """Mark selected messages as read."""
        updated = queryset.filter(status='new').update(status='read')
        self.message_user(request, f'{updated} message(s) marked as read.')
    mark_as_read.short_description = 'Mark selected as read'
    
    def mark_as_resolved(self, request, queryset):
        """Mark selected messages as resolved."""
        updated = queryset.update(status='resolved')
        self.message_user(request, f'{updated} message(s) marked as resolved.')
    mark_as_resolved.short_description = 'Mark selected as resolved'
