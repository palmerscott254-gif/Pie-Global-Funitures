from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminDashboardViewSet

router = DefaultRouter()
router.register(r'dashboard', AdminDashboardViewSet, basename='admin-dashboard')

urlpatterns = [
    path(
        'dashboard/products/',
        AdminDashboardViewSet.as_view({'get': 'products', 'post': 'create_product'}),
        name='admin-dashboard-products'
    ),
    path(
        'dashboard/products/<int:product_id>/',
        AdminDashboardViewSet.as_view({'patch': 'update_product', 'put': 'update_product', 'delete': 'delete_product'}),
        name='admin-dashboard-product-detail'
    ),
    path(
        'dashboard/top-products/',
        AdminDashboardViewSet.as_view({'get': 'top_products'}),
        name='admin-dashboard-top-products'
    ),
    # Backwards-compatible active alerts endpoint expected by frontend
    path('alerts/active/', AdminDashboardViewSet.as_view({'get': 'alerts'}), name='admin-active-alerts'),
]

urlpatterns += [path('', include(router.urls))]
