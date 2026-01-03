from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from .models import Order
from .serializers import OrderSerializer, OrderListSerializer


# Rate limiting: prevent abuse - 10 orders per hour per IP
@method_decorator(ratelimit(key='ip', rate='10/h', method='POST', block=True), name='create')
class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Order management.
    
    Create: Public (for customers) with rate limiting
    List/Update/Delete: Admin only
    
    Security: Rate limited to prevent order spam/abuse
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'paid']
    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """Allow public order creation, but restrict other actions."""
        if self.action == 'create':
            return []
        return [IsAdminUser()]
    
    def get_serializer_class(self):
        """Use lightweight serializer for lists."""
        if self.action == 'list':
            return OrderListSerializer
        return OrderSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new order."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response(
            {
                'message': 'Order created successfully',
                'order': serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def update_status(self, request, pk=None):
        """Update order status."""
        order = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = new_status
        order.save()
        
        return Response(OrderSerializer(order).data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def mark_paid(self, request, pk=None):
        """Mark order as paid."""
        order = self.get_object()
        order.paid = True
        order.payment_method = request.data.get('payment_method', 'Manual')
        order.save()
        
        return Response(OrderSerializer(order).data)
