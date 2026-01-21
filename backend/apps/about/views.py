from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import AboutPage
from .serializers import AboutPageSerializer
import logging

logger = logging.getLogger('django')


class AboutPageViewSet(viewsets.ModelViewSet):
    """ViewSet for About Page with error handling and logging."""
    queryset = AboutPage.objects.all()
    serializer_class = AboutPageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None  # Disable pagination
    
    def get_queryset(self):
        """Return all about pages for staff, only first for public."""
        return AboutPage.objects.all()
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current/primary about page."""
        about = AboutPage.objects.first()
        if not about:
            logger.warning('[AboutAPI] No about page found')
            return Response(
                {'detail': 'About page not configured'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(about)
        logger.debug(f'[AboutAPI] Returning about page: {about.headline}')
        return Response(serializer.data)
