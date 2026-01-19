from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('email', 'name')
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        ('Account Info', {'fields': ('id', 'email', 'name')}),
        ('Status', {'fields': ('is_active',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    def has_add_permission(self, request):
        """Disable direct user creation in admin; use registration form instead"""
        return False
