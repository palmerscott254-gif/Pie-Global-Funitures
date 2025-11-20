from rest_framework import viewsets
from .models import AboutPage
from .serializers import AboutPageSerializer

class AboutPageViewSet(viewsets.ModelViewSet):
    queryset = AboutPage.objects.all()
    serializer_class = AboutPageSerializer
    pagination_class = None  # Disable pagination
