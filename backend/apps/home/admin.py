from django.contrib import admin
from .models import SliderImage, HomeVideo

@admin.register(SliderImage)
class SliderImageAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "order", "active", "uploaded_at")
    list_editable = ("order", "active")

@admin.register(HomeVideo)
class HomeVideoAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "active", "uploaded_at")
