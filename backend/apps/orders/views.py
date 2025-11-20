from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import Order
from .serializers import OrderSerializer, OrderListSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Order management.
    
    Create: Public (for customers)
    List/Update/Delete: Admin only
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
        
        # TODO: Send confirmation email
        # TODO: Integrate payment gateway
        
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
        
        # TODO: Send status update email to customer
        
        return Response(OrderSerializer(order).data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def mark_paid(self, request, pk=None):
        """Mark order as paid."""
        order = self.get_object()
        order.paid = True
        order.payment_method = request.data.get('payment_method', 'Manual')
        order.save()
        
        return Response(OrderSerializer(order).data)
