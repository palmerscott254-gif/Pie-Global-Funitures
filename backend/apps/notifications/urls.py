from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for ViewSets
router = DefaultRouter()
router.register(
    r'notifications',
    views.NotificationViewSet,
    basename='notification'
)

app_name = 'notifications'

urlpatterns = [
    # REST API routes from ViewSet
    path('', include(router.urls)),
    
    # Notification preferences endpoints
    path(
        'preferences/',
        views.NotificationPreferenceViewSet.as_view(
            {'get': 'list', 'put': 'update'}
        ),
        name='notification-preferences'
    ),
    
    # Admin broadcast endpoint
    path(
        'admin/send-notification/',
        views.AdminNotificationViewSet.as_view({'post': 'create'}),
        name='admin-broadcast-notification'
    ),
    
    # Admin logs endpoint
    path(
        'admin/logs/',
        views.AdminNotificationViewSet.as_view({'get': 'logs'}),
        name='admin-notification-logs'
    ),
]
