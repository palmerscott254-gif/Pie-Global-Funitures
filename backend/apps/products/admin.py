from django.contrib import admin
from django.utils.html import format_html
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Enhanced admin interface for Product model."""
    
    list_display = (
        "id", "name", "category", "formatted_price", 
        "stock", "stock_status", "featured", "is_active", "created_at"
    )
    list_filter = ("category", "featured", "is_active", "on_sale", "created_at")
    list_editable = ("featured", "is_active", "stock")
    search_fields = ("name", "description", "sku")
    prepopulated_fields = {"slug": ("name",)}
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at", "in_stock", "discount_percentage")
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("name", "slug", "short_description", "description")
        }),
        ("Pricing", {
            "fields": ("price", "compare_at_price", "discount_percentage")
        }),
        ("Categorization", {
            "fields": ("category", "tags")
        }),
        ("Media", {
            "fields": ("main_image", "gallery")
        }),
        ("Inventory", {
            "fields": ("stock", "sku", "in_stock")
        }),
        ("Specifications", {
            "fields": ("dimensions", "material", "color", "weight"),
            "classes": ("collapse",)
        }),
        ("Flags", {
            "fields": ("featured", "is_active", "on_sale")
        }),
        ("SEO", {
            "fields": ("meta_title", "meta_description"),
            "classes": ("collapse",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def formatted_price(self, obj):
        """Display formatted price with currency."""
        return f"KSh {obj.price:,.0f}"
    formatted_price.short_description = "Price"
    formatted_price.admin_order_field = "price"
    
    def stock_status(self, obj):
        """Display stock status with color indicator."""
        if obj.stock == 0:
            color = "red"
            status = "Out of Stock"
        elif obj.stock < 5:
            color = "orange"
            status = "Low Stock"
        else:
            color = "green"
            status = "In Stock"
        return format_html(
            '<span style="color: {};">{}</span>',
            color, status
        )
    stock_status.short_description = "Status"
