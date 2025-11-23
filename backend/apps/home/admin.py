from django.contrib import admin
from .models import SliderImage, HomeVideo

@admin.register(SliderImage)
class SliderImageAdmin(admin.ModelAdmin):
    """Admin interface for homepage slider images."""
    
    list_display = ("id", "title", "order", "active", "uploaded_at")
    list_editable = ("order", "active")
    list_filter = ("active", "uploaded_at")
    search_fields = ("title",)
    ordering = ("order", "-uploaded_at")

@admin.register(HomeVideo)
class HomeVideoAdmin(admin.ModelAdmin):
    """Admin interface for homepage videos."""
    
    list_display = ("id", "title", "active", "uploaded_at")
    list_editable = ("active",)
    list_filter = ("active", "uploaded_at")
    search_fields = ("title",)
    date_hierarchy = "uploaded_at"
    ordering = ("-uploaded_at",)
