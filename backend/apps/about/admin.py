from django.contrib import admin
from django.utils.html import format_html
from .models import AboutPage


@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    list_display = ('id', 'short_headline', 'last_updated')
    readonly_fields = ('updated_at', 'word_counts')
    search_fields = ('headline', 'body', 'mission', 'vision')
    
    fieldsets = (
        ('Main Content', {
            'fields': ('headline', 'body'),
            'description': 'Main about page headline and body content'
        }),
        ('Mission & Vision', {
            'fields': ('mission', 'vision'),
            'description': 'Company mission and vision statements'
        }),
        ('Statistics', {
            'fields': ('word_counts',),
            'classes': ('collapse',)
        }),
        ('Meta', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
    
    def short_headline(self, obj):
        """Display truncated headline"""
        if len(obj.headline) > 50:
            return obj.headline[:50] + '...'
        return obj.headline
    short_headline.short_description = 'Headline'
    
    def last_updated(self, obj):
        """Display formatted update time"""
        return format_html(
            '<span style="color: #666;">{}</span>',
            obj.updated_at.strftime('%B %d, %Y at %I:%M %p')
        )
    last_updated.short_description = 'Last Updated'
    
    def word_counts(self, obj):
        """Display word counts for content fields"""
        body_words = len(obj.body.split()) if obj.body else 0
        mission_words = len(obj.mission.split()) if obj.mission else 0
        vision_words = len(obj.vision.split()) if obj.vision else 0
        
        return format_html(
            '<ul style="list-style: none; padding: 0;">'
            '<li><strong>Body:</strong> {} words</li>'
            '<li><strong>Mission:</strong> {} words</li>'
            '<li><strong>Vision:</strong> {} words</li>'
            '</ul>',
            body_words, mission_words, vision_words
        )
    word_counts.short_description = 'Content Statistics'
    
    def has_add_permission(self, request):
        """Limit to one about page instance"""
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of about page"""
        return False
