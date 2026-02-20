from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
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
    
    def get_serializer_class(self):
        """Use lightweight serializer for list views."""
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer
    
    def get_queryset(self):
        """Show all products regardless of is_active status. Only hide placeholder products (price <= 1)."""
        queryset = Product.objects.all().filter(price__gt=1)  # Hide placeholder products with price = 1.00
        # Do NOT filter by is_active or name prefix - show all real products
        return queryset
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products only."""
        products = self.get_queryset().filter(featured=True)
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def on_sale(self, request):
        """Get products on sale."""
        products = self.get_queryset().filter(on_sale=True)
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get products grouped by category."""
        categories = Product.CATEGORY_CHOICES
        result = {}
        for cat_key, cat_name in categories:
            products = self.get_queryset().filter(category=cat_key)
            result[cat_key] = ProductListSerializer(
                products, 
                many=True, 
                context={'request': request}
            ).data
        return Response(result)
