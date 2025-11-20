from django.contrib import admin
from .models import AboutPage


@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    list_display = ('id', 'headline', 'updated_at')
    readonly_fields = ('updated_at',)
    
    fieldsets = (
        ('Main Content', {
            'fields': ('headline', 'body')
        }),
        ('Mission & Vision', {
            'fields': ('mission', 'vision')
        }),
        ('Meta', {
            'fields': ('updated_at',)
        }),
    )
