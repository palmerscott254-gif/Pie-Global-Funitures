from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminDashboardViewSet

router = DefaultRouter()
router.register(r'dashboard', AdminDashboardViewSet, basename='admin-dashboard')

urlpatterns = [
    path('', include(router.urls)),
    # Backwards-compatible active alerts endpoint expected by frontend
    path('alerts/active/', AdminDashboardViewSet.as_view({'get': 'alerts'}), name='admin-active-alerts'),
]
