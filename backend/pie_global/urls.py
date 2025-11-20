"""
URL configuration for Pie Global Furniture project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from django.views.generic import RedirectView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include('apps.products.urls')),
    path('api/', include('apps.home.urls')),
    path('api/', include('apps.messages.urls')),
    path('api/', include('apps.orders.urls')),
    path('api/', include('apps.about.urls')),
    
    # Redirect root to admin or API docs
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
]

# Serve media and static files
# Note: In production, use a proper web server (Nginx, Apache) or CDN
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize admin site
admin.site.site_header = 'Pie Global Furniture Admin'
admin.site.site_title = 'Pie Global Admin'
admin.site.index_title = 'Welcome to Pie Global Furniture Administration'
