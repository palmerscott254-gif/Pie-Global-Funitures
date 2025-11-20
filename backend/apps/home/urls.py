from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SliderImageViewSet, HomeVideoViewSet

router = DefaultRouter()
router.register(r"sliders", SliderImageViewSet, basename="sliders")
router.register(r"videos", HomeVideoViewSet, basename="videos")

urlpatterns = [
    path("", include(router.urls)),
]
