"""
URL configuration for core utilities.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import S3PresignedURLViewSet

router = DefaultRouter()
router.register(r"upload", S3PresignedURLViewSet, basename="upload")

urlpatterns = [
    path("", include(router.urls)),
]
