from django.conf import settings
from django.core.cache import cache
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from apps.core.db import ensure_db_connection
from .models import Product
from .serializers import ProductSerializer, ProductListSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product CRUD operations.
    
    List/Retrieve: Public access
    Create/Update/Delete: Admin only
    """
    queryset = Product.objects.all()  # Start with all products, filtering happens in get_queryset()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'featured', 'on_sale']
    search_fields = ['name', 'description', 'short_description', 'sku']
    ordering_fields = ['price', 'created_at', 'name']
    ordering = ['-created_at']

    def _cache_timeout(self):
        return int(getattr(settings, 'API_RESPONSE_CACHE_TTL', 120))

    def _cache_key(self, action_name, request):
        return f"products:{action_name}:{request.get_full_path()}"

    def _cache_response_or_fetch(self, key, fetcher):
        cached_payload = cache.get(key)
        if cached_payload is not None:
            return Response(cached_payload)

        payload = fetcher()
        cache.set(key, payload, timeout=self._cache_timeout())
        return Response(payload)
    
    def get_serializer_class(self):
        """Use lightweight serializer for list views."""
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer
    
    def get_queryset(self):
        """Show all products without placeholder filtering."""
        ensure_db_connection()
        return Product.objects.all()

    def list(self, request, *args, **kwargs):
        cache_key = self._cache_key('list', request)

        def fetch_payload():
            response = super(ProductViewSet, self).list(request, *args, **kwargs)
            return response.data

        return self._cache_response_or_fetch(cache_key, fetch_payload)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products only."""
        cache_key = self._cache_key('featured', request)

        def fetch_payload():
            products = self.get_queryset().filter(featured=True)
            serializer = ProductListSerializer(products, many=True, context={'request': request})
            return serializer.data

        return self._cache_response_or_fetch(cache_key, fetch_payload)
    
    @action(detail=False, methods=['get'])
    def on_sale(self, request):
        """Get products on sale."""
        cache_key = self._cache_key('on_sale', request)

        def fetch_payload():
            products = self.get_queryset().filter(on_sale=True)
            serializer = ProductListSerializer(products, many=True, context={'request': request})
            return serializer.data

        return self._cache_response_or_fetch(cache_key, fetch_payload)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get products grouped by category."""
        cache_key = self._cache_key('by_category', request)

        def fetch_payload():
            categories = Product.CATEGORY_CHOICES
            result = {}
            for cat_key, cat_name in categories:
                products = self.get_queryset().filter(category=cat_key)
                result[cat_key] = ProductListSerializer(
                    products,
                    many=True,
                    context={'request': request}
                ).data
            return result

        return self._cache_response_or_fetch(cache_key, fetch_payload)

    def perform_create(self, serializer):
        super().perform_create(serializer)
        cache.clear()

    def perform_update(self, serializer):
        super().perform_update(serializer)
        cache.clear()

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        cache.clear()
