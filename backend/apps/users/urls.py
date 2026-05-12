from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet
from .simplejwt_views import token_obtain_pair_view, token_refresh_view

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    # Simple JWT endpoints (optional - project already exposes custom token endpoints)
    path('token/', token_obtain_pair_view, name='token_obtain_pair'),
    path('token/refresh/', token_refresh_view, name='token_refresh'),
]
