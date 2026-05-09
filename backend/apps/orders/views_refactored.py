"""Refactored order views using OrderService with improved error handling."""
import logging
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from apps.orders.models import Order
from apps.orders.serializers import OrderSerializer
from apps.orders.order_service import OrderService
from apps.core.response_helpers import ResponseFormatter, PaginationHelper
from apps.core.audit import AuditLogger

logger = logging.getLogger(__name__)


@method_decorator(ratelimit(key='user', rate='10/h', method='POST', block=True), name='create')
class OrderViewSet(viewsets.ModelViewSet):
    \"\"\"ViewSet for customer orders.
    
    Endpoints:
    - POST /orders/ - Create order (rate limited 10/hour per user)
    - GET /orders/ - List orders (own orders for users, all for admins)
    - GET /orders/{id}/ - Get order details
    - POST /orders/{id}/mark_paid/ - Mark as paid (admin only)
    - POST /orders/{id}/update_status/ - Update status (admin only)
    
    Security:
    - Must be authenticated (users see own orders, admins see all)
    - Status updates only admins
    - Payment tracking with method logging
    \"\"\"
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']
    serializer_class = OrderSerializer

    def get_queryset(self):
        \"\"\"Return user's own orders or all if admin.\"\"\"
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(email=user.email)

    def list(self, request, *args, **kwargs):
        \"\"\"List orders with pagination.\"\"\"
        queryset = self.filter_queryset(self.get_queryset())

        paginator = PaginationHelper.paginate_queryset(queryset, request)
        if paginator:
            serializer = self.get_serializer(paginator, many=True)
            return PaginationHelper.get_paginated_response(paginator, serializer.data, request)

        serializer = self.get_serializer(queryset, many=True)
        return ResponseFormatter.success(data={'results': serializer.data})

    def create(self, request, *args, **kwargs):
        \"\"\"Create a new order (rate limited).\"\"\"
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return ResponseFormatter.validation_error(serializer.errors)

        try:
            order = OrderService.create_order(
                email=serializer.validated_data['email'],
                phone=serializer.validated_data.get('phone'),
                items=serializer.validated_data['items'],
                total_amount=serializer.validated_data['total_amount'],
                shipping_address=serializer.validated_data.get('shipping_address'),
                notes=serializer.validated_data.get('notes'),
                request=request,
            )

            # Send admin notification in background
            service = OrderService()
            service.enqueue_task(
                OrderService.send_admin_notification,
                order,
            )

            logger.info(f\"Order created: {order.id} for {order.email}\")

            return ResponseFormatter.created(
                message='Order placed successfully. We will contact you soon.',
                data=OrderSerializer(order).data,
            )

        except Exception as e:
            logger.exception(f\"Failed to create order: {e}\")
            return ResponseFormatter.server_error()

    def retrieve(self, request, *args, **kwargs):
        \"\"\"Get order details.\"\"\"
        order = self.get_object()
        
        # Verify ownership (non-admins can only view their own orders)
        if not request.user.is_staff and order.email != request.user.email:
            return ResponseFormatter.forbidden('You do not have access to this order')

        return ResponseFormatter.success(data=OrderSerializer(order).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def mark_paid(self, request, pk=None):
        \"\"\"Mark an order as paid (admin only).\"\"\"
        order = self.get_object()
        payment_method = request.data.get('payment_method', 'manual').strip()

        if not payment_method:
            return ResponseFormatter.error(
                'payment_method is required',
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(payment_method) > 50:
            return ResponseFormatter.error(
                'payment_method is too long (max 50 characters)',
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            updated_order = OrderService.mark_order_paid(
                order=order,
                payment_method=payment_method,
                user_id=str(request.user.id) if request.user else None,
            )

            logger.info(f\"Order {order.id} marked as paid via {payment_method}\")

            return ResponseFormatter.success(
                message='Order marked as paid',
                data=OrderSerializer(updated_order).data,
            )
        except Exception as e:
            logger.exception(f\"Failed to mark order paid: {e}\")
            return ResponseFormatter.server_error()

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def update_status(self, request, pk=None):
        \"\"\"Update order status (admin only).\"\"\"
        order = self.get_object()
        new_status = request.data.get('status', '').strip().lower()

        if not new_status:
            return ResponseFormatter.error(
                'status is required',
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate status choice
        if new_status not in dict(Order.STATUS_CHOICES):
            valid_statuses = ', '.join([choice[0] for choice in Order.STATUS_CHOICES])
            return ResponseFormatter.error(
                f'Invalid status. Valid values: {valid_statuses}',
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            updated_order = OrderService.update_order_status(
                order=order,
                new_status=new_status,
                user_id=str(request.user.id) if request.user else None,
            )

            logger.info(f\"Order {order.id} status changed to {new_status}\")

            return ResponseFormatter.success(
                message=f'Order status updated to {new_status}',
                data=OrderSerializer(updated_order).data,
            )
        except Exception as e:
            logger.exception(f\"Failed to update order status: {e}\")
            return ResponseFormatter.server_error()
