"""
URL configuration for Pie Global Furniture project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from django.views.generic import RedirectView
from django.http import JsonResponse

def health_check(request):
    """Health check endpoint for Render and monitoring."""
    return JsonResponse({'status': 'healthy', 'service': 'pie-global-backend'})

urlpatterns = [
    # Health check
    path('api/health/', health_check, name='health_check'),
    
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

# Serve media files in all environments (including production)
# WhiteNoise doesn't serve media by default, so we need to add it explicitly
from django.views.static import serve
from django.urls import re_path

if not settings.DEBUG:
    # In production, serve media files directly
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
else:
    # In development, use standard static serve
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize admin site
admin.site.site_header = 'Pie Global Furniture Admin'
admin.site.site_title = 'Pie Global Admin'
admin.site.index_title = 'Welcome to Pie Global Furniture Administration'
