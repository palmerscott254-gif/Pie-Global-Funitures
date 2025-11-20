from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import SliderImage, HomeVideo
from .serializers import SliderImageSerializer, HomeVideoSerializer


class SliderImageViewSet(viewsets.ModelViewSet):
    """ViewSet for homepage slider images."""
    
    queryset = SliderImage.objects.filter(active=True)
    serializer_class = SliderImageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    ordering = ['order', '-uploaded_at']
    pagination_class = None  # Disable pagination for sliders
    
    def get_queryset(self):
        """Show all sliders to staff, only active to public."""
        if self.request.user.is_staff:
            return SliderImage.objects.all()
        return SliderImage.objects.filter(active=True)


class HomeVideoViewSet(viewsets.ModelViewSet):
    """ViewSet for homepage hero videos."""
    
    queryset = HomeVideo.objects.filter(active=True)
    serializer_class = HomeVideoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None  # Disable pagination for videos
    
    def get_queryset(self):
        """Show all videos to staff, only active to public."""
        if self.request.user.is_staff:
            return HomeVideo.objects.all()
        return HomeVideo.objects.filter(active=True)
