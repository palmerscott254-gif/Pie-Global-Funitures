"""
URL configuration for Pie Global Furniture project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
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

# DEVELOPMENT ONLY: Serve static and media files via Django development server
# In production, these are served by WhiteNoise (static) and reverse proxy (media)
if settings.DEBUG:
    # Development server serves both static and media files
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize admin site
admin.site.site_header = 'Pie Global Furniture Admin'
admin.site.site_title = 'Pie Global Admin'
admin.site.index_title = 'Welcome to Pie Global Furniture Administration'
