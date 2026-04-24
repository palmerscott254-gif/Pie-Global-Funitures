from django.conf import settings
from django.core.cache import cache
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from apps.core.db import ensure_db_connection
from .models import SliderImage, HomeVideo
from .serializers import SliderImageSerializer, HomeVideoSerializer


class SliderImageViewSet(viewsets.ModelViewSet):
    """ViewSet for homepage slider images."""
    
    queryset = SliderImage.objects.filter(active=True)
    serializer_class = SliderImageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None  # Disable pagination for sliders

    def _cache_timeout(self):
        return int(getattr(settings, 'API_RESPONSE_CACHE_TTL', 120))

    def _cache_key(self, action_name, request):
        user_scope = 'staff' if request.user.is_staff else 'public'
        return f"home:sliders:{action_name}:{user_scope}:{request.get_full_path()}"
    
    def get_queryset(self):
        """Show all sliders to staff, only active to public."""
        ensure_db_connection()
        if self.request.user.is_staff:
            return SliderImage.objects.all()
        return SliderImage.objects.filter(active=True)

    def list(self, request, *args, **kwargs):
        cache_key = self._cache_key('list', request)
        cached_payload = cache.get(cache_key)
        if cached_payload is not None:
            return Response(cached_payload)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=self._cache_timeout())
        return response

    def perform_create(self, serializer):
        super().perform_create(serializer)
        cache.clear()

    def perform_update(self, serializer):
        super().perform_update(serializer)
        cache.clear()

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        cache.clear()


class HomeVideoViewSet(viewsets.ModelViewSet):
    """ViewSet for homepage hero videos."""
    
    queryset = HomeVideo.objects.filter(active=True)
    serializer_class = HomeVideoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None  # Disable pagination for videos

    def _cache_timeout(self):
        return int(getattr(settings, 'API_RESPONSE_CACHE_TTL', 120))

    def _cache_key(self, action_name, request):
        user_scope = 'staff' if request.user.is_staff else 'public'
        return f"home:videos:{action_name}:{user_scope}:{request.get_full_path()}"
    
    def get_queryset(self):
        """Show all videos to staff, only active to public."""
        ensure_db_connection()
        if self.request.user.is_staff:
            return HomeVideo.objects.all()
        return HomeVideo.objects.filter(active=True)

    def list(self, request, *args, **kwargs):
        cache_key = self._cache_key('list', request)
        cached_payload = cache.get(cache_key)
        if cached_payload is not None:
            return Response(cached_payload)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=self._cache_timeout())
        return response

    def perform_create(self, serializer):
        super().perform_create(serializer)
        cache.clear()

    def perform_update(self, serializer):
        super().perform_update(serializer)
        cache.clear()

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        cache.clear()
