from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "status", "paid", "total_amount", "created_at")
    list_filter = ("status", "paid", "created_at")
    search_fields = ("name", "email", "phone", "address", "city", "postal_code")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
