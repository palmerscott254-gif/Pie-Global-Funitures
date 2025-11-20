from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserMessageViewSet

router = DefaultRouter()
router.register(r"messages", UserMessageViewSet, basename="messages")

urlpatterns = [
    path("", include(router.urls)),
]
