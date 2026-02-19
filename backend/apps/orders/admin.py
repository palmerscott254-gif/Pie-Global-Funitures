from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Enhanced admin interface for Order model."""
    
    list_display = (
        "id", "name", "phone", "email", "status", 
        "paid", "formatted_total", "created_at"
    )
    list_filter = ("status", "paid", "created_at")
    list_editable = ("status", "paid")
    search_fields = ("name", "email", "phone", "address", "city", "postal_code")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    
    fieldsets = (
        ("Customer Information", {
            "fields": ("name", "email", "phone")
        }),
        ("Shipping Address", {
            "fields": ("address", "city", "postal_code")
        }),
        ("Order Details", {
            "fields": ("items", "total_amount", "status", "paid", "payment_method")
        }),
        ("Additional Information", {
            "fields": ("notes",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def formatted_total(self, obj):
        """Display formatted total with currency."""
        return f"KSh {obj.total_amount:,.0f}"
    formatted_total.short_description = "Total Amount"
    formatted_total.admin_order_field = "total_amount"
