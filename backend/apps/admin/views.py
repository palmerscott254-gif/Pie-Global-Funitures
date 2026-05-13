import logging
from datetime import timedelta
from django.utils import timezone
from django.db import IntegrityError
from django.db.models import Sum, Avg, Q, F, Case, When, Value
from django.db.models.functions import Coalesce
from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from apps.orders.models import Order
from apps.messages.models import UserMessage
from apps.products.models import Product
from apps.admin.models import AdminAuditLog
from apps.admin.permissions import IsAdminOrStaff, HasRole
from apps.admin.serializers import (
    DashboardSummarySerializer,
    AdminOrderSerializer,
    AdminMessageSerializer,
    OrderStatusUpdateSerializer,
    MessageReplySerializer,
    AlertSerializer,
    AdminAuditLogSerializer,
)

logger = logging.getLogger(__name__)


class AdminDashboardViewSet(viewsets.ViewSet):
    """
    ViewSet for admin dashboard endpoints.
    Requires admin or staff permissions.
    """
    permission_classes = [IsAuthenticated, HasRole]

    def get_client_ip(self, request):
        """Extract client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def log_action(self, request, action, obj, changes=None):
        """Log an admin action to audit trail."""
        try:
            content_type = ContentType.objects.get_for_model(obj.__class__)
            AdminAuditLog.objects.create(
                admin_user=request.user,
                content_type=content_type,
                object_id=obj.id,
                action=action,
                changes=changes or {},
                ip_address=self.get_client_ip(request)
            )
        except Exception as e:
            logger.exception(f"Failed to log admin action: {e}")

    def get_product_sales_map(self):
        """Build a map of product_id -> sales metrics from delivered orders."""
        product_sales = {}
        delivered_orders = Order.objects.filter(status='delivered')

        for order in delivered_orders:
            if not order.items:
                continue

            for item in order.items:
                product_id = item.get('product_id')
                if not product_id:
                                        continue

                qty = int(item.get('qty', 0) or 0)
                price = float(item.get('price', 0) or 0)
                revenue = qty * price

                if product_id not in product_sales:
                    product_sales[product_id] = {
                        'units_sold': 0,
                        'revenue': 0,
                    }

                product_sales[product_id]['units_sold'] += qty
                product_sales[product_id]['revenue'] += revenue

        return product_sales

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get dashboard summary with KPI metrics.
        /api/admin/dashboard/summary/
        """
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Order counts
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='pending').count()
        processing_orders = Order.objects.filter(status='processing').count()
        delivered_orders = Order.objects.filter(status='delivered').count()
        cancelled_orders = Order.objects.filter(status='cancelled').count()

        # Message counts
        # only messages with status 'new' should be considered unread
        unread_messages = UserMessage.objects.filter(status='new').count()
        total_messages = UserMessage.objects.count()

        # Revenue metrics
        revenue_data_today = Order.objects.filter(
            status='delivered',
            created_at__gte=today_start
        ).aggregate(
            total=Sum('total_amount')
        )
        revenue_today = revenue_data_today['total'] or 0

        revenue_data_month = Order.objects.filter(
            status='delivered',
            created_at__gte=month_start
        ).aggregate(
            total=Sum('total_amount')
        )
        revenue_this_month = revenue_data_month['total'] or 0

        revenue_data_all = Order.objects.filter(
            status='delivered'
        ).aggregate(
            total=Sum('total_amount')
        )
        revenue_all_time = revenue_data_all['total'] or 0

        # Average order value (use DB aggregation)
        avg_order = Order.objects.aggregate(avg=Avg('total_amount'))
        average_order_value = avg_order['avg'] or 0

        # Recent orders (last 5)
        recent_orders = Order.objects.order_by('-created_at')[:5]

        # Recent messages (last 5)
        recent_messages = UserMessage.objects.order_by('-created_at')[:5]

        data = {
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'processing_orders': processing_orders,
            'delivered_orders': delivered_orders,
            'cancelled_orders': cancelled_orders,
            'unread_messages': unread_messages,
            'total_messages': total_messages,
            'revenue_today': revenue_today,
            'revenue_this_month': revenue_this_month,
            'revenue_all_time': revenue_all_time,
            'average_order_value': average_order_value,
            'recent_orders': recent_orders,
            'recent_messages': recent_messages,
        }

        serializer = DashboardSummarySerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def alerts(self, request):
        """
        Get active alerts that need admin attention.
        /api/admin/dashboard/alerts/
        """
        alerts = []

        # Pending orders alert
        pending = Order.objects.filter(
            Q(status='pending') | Q(status='received') | Q(status='confirmed')
        ).count()
        if pending > 0:
            alerts.append({
                'type': 'pending_orders',
                'severity': 'warning' if pending < 5 else 'danger',
                'message': f'{pending} order{"s" if pending != 1 else ""} awaiting confirmation',
                'count': pending,
                'action_url': '/admin/orders/?status=pending',
            })

        # Unread messages alert
        unread = UserMessage.objects.filter(
            Q(status='new') | Q(status='read')
        ).count()
        if unread > 0:
            alerts.append({
                'type': 'unread_messages',
                'severity': 'info' if unread < 3 else 'warning',
                'message': f'{unread} message{"s" if unread != 1 else ""} awaiting reply',
                'count': unread,
                'action_url': '/admin/messages/?status=new',
            })

        # Processing orders alert
        processing = Order.objects.filter(status='processing').count()
        if processing > 0:
            alerts.append({
                'type': 'processing_orders',
                'severity': 'info',
                'message': f'{processing} order{"s" if processing != 1 else ""} being processed',
                'count': processing,
                'action_url': '/admin/orders/?status=processing',
            })

        # Out for delivery alert
        in_transit = Order.objects.filter(Q(status='shipped') | Q(status='out_for_delivery')).count()
        if in_transit > 0:
            alerts.append({
                'type': 'in_transit_orders',
                'severity': 'info',
                'message': f'{in_transit} order{"s" if in_transit != 1 else ""} in transit',
                'count': in_transit,
                'action_url': '/admin/orders/?status=out_for_delivery',
            })

        serializer = AlertSerializer(alerts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recent_orders(self, request):
        """
        Get recent orders with pagination and filtering.
        /api/admin/dashboard/recent_orders/?limit=10&status=pending
        """
        limit = int(request.query_params.get('limit', 10))
        status_filter = request.query_params.get('status')

        queryset = Order.objects.all()
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        orders = queryset[:limit]
        serializer = AdminOrderSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recent_messages(self, request):
        """
        Get recent messages with pagination and filtering.
        /api/admin/dashboard/recent_messages/?limit=10&status=new
        """
        limit = int(request.query_params.get('limit', 10))
        status_filter = request.query_params.get('status')

        queryset = UserMessage.objects.all()
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        messages = queryset[:limit]
        serializer = AdminMessageSerializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='orders/(?P<order_id>[^/.]+)/status')
    def update_order_status(self, request, pk=None, order_id=None):
        """
        Update order status.
        POST /api/admin/dashboard/orders/{order_id}/status/
        """
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data['status']
        notes = serializer.validated_data.get('notes', '')

        # Track changes
        old_status = order.status
        changes = {
            'status': {'old': old_status, 'new': new_status}
        }

        order.status = new_status
        if notes:
            order.notes = notes

        order.save()

        # Log the action
        self.log_action(request, 'status_change', order, changes)

        logger.info(
            f"Order {order.id} status changed from {old_status} to {new_status} by {request.user.email}"
        )

        return Response(
            {
                'message': f'Order status updated to {new_status}',
                'order': AdminOrderSerializer(order).data
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'], url_path='orders/(?P<order_id>[^/.]+)/mark-paid')
    def mark_order_paid(self, request, pk=None, order_id=None):
        """
        Mark order as paid (cash on delivery).
        POST /api/admin/dashboard/orders/{order_id}/mark-paid/
        """
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Only mark as paid if delivered
        if order.status != 'delivered':
            return Response(
                {'error': 'Can only mark delivered orders as paid'},
                status=status.HTTP_400_BAD_REQUEST
            )

        changes = {
            'paid': {'old': order.paid, 'new': True},
            'payment_method': {'old': order.payment_method, 'new': 'cash_on_delivery'}
        }

        order.paid = True
        order.payment_method = 'cash_on_delivery'
        order.save()

        # Log the action
        self.log_action(request, 'marked_paid', order, changes)

        logger.info(
            f"Order {order.id} marked as paid by {request.user.email}"
        )

        return Response(
            {
                'message': 'Order marked as paid',
                'order': AdminOrderSerializer(order).data
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'], url_path='messages/(?P<message_id>[^/.]+)/reply')
    def reply_to_message(self, request, pk=None, message_id=None):
        """
        Reply to a customer message.
        POST /api/admin/dashboard/messages/{message_id}/reply/
        """
        try:
            message = UserMessage.objects.get(id=message_id)
        except UserMessage.DoesNotExist:
            return Response(
                {'error': 'Message not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = MessageReplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reply_text = serializer.validated_data['reply_text']
        new_status = serializer.validated_data.get('status', 'replied')

        changes = {
            'reply_text': {'old': message.reply_text, 'new': reply_text},
            'status': {'old': message.status, 'new': new_status},
            'replied_at': {'old': str(message.replied_at), 'new': str(timezone.now())}
        }

        message.reply_text = reply_text
        message.status = new_status
        message.replied_at = timezone.now()
        message.save()

        # Log the action
        self.log_action(request, 'message_reply', message, changes)

        logger.info(
            f"Message {message.id} replied by {request.user.email}"
        )

        return Response(
            {
                'message': 'Reply sent successfully',
                'data': AdminMessageSerializer(message).data
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'], url_path='messages/(?P<message_id>[^/.]+)/resolve')
    def resolve_message(self, request, pk=None, message_id=None):
        """
        Mark message as resolved.
        POST /api/admin/dashboard/messages/{message_id}/resolve/
        """
        try:
            message = UserMessage.objects.get(id=message_id)
        except UserMessage.DoesNotExist:
            return Response(
                {'error': 'Message not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        changes = {
            'status': {'old': message.status, 'new': 'resolved'}
        }

        message.status = 'resolved'
        message.save()

        # Log the action
        self.log_action(request, 'message_resolved', message, changes)

        logger.info(
            f"Message {message.id} marked as resolved by {request.user.email}"
        )

        return Response(
            {
                'message': 'Message marked as resolved',
                'data': AdminMessageSerializer(message).data
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def audit_logs(self, request):
        """
        Get admin audit logs.
        /api/admin/dashboard/audit_logs/?limit=50
        """
        limit = int(request.query_params.get('limit', 50))
        logs = AdminAuditLog.objects.all()[:limit]
        serializer = AdminAuditLogSerializer(logs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def top_products(self, request):
        """
        Get top-selling products (by units sold).
        /api/admin/dashboard/top-products/?limit=10
        """
        limit = int(request.query_params.get('limit', 10))
        product_sales = self.get_product_sales_map()
        
        # Get product details and sort by units sold
        top_product_ids = sorted(
            product_sales.items(),
            key=lambda x: x[1]['units_sold'],
            reverse=True
        )[:limit]
        
        result = []
        for product_id, sales_data in top_product_ids:
            try:
                product = Product.objects.get(id=product_id)
                result.append({
                    'id': product.id,
                    'name': product.name,
                    'units_sold': sales_data['units_sold'],
                    'revenue': sales_data['revenue'],
                })
            except Product.DoesNotExist:
                pass
        
        return Response(result)

    @action(detail=False, methods=['get'])
    def products(self, request):
        """
        Get all products (paged).
        GET /api/admin/dashboard/products/?search=sofa&category=furniture&page=1
        """
        search = request.query_params.get('search', '')
        category = request.query_params.get('category', '')
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 20))
        
        queryset = Product.objects.all()
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) |
                Q(sku__icontains=search)
            )
        
        if category:
            queryset = queryset.filter(category=category)
        
        # Order by newest first
        queryset = queryset.order_by('-created_at')
        
        # Count total
        total_count = queryset.count()

        product_sales = self.get_product_sales_map()
        
        # Paginate
        offset = (page - 1) * limit
        products = queryset[offset:offset + limit]
        
        from apps.admin.serializers import AdminProductSerializer
        serialized = AdminProductSerializer(products, many=True).data
        results = []
        for item in serialized:
            sales = product_sales.get(item['id'], {'units_sold': 0, 'revenue': 0})
            item['units_sold'] = sales['units_sold']
            results.append(item)
        
        return Response({
            'count': total_count,
            'page': page,
            'limit': limit,
            'results': results,
        })

    @action(detail=False, methods=['post'])
    def create_product(self, request):
        """
        Create new product.
        POST /api/admin/dashboard/products/
        """
        from apps.admin.serializers import AdminProductSerializer
        
        serializer = AdminProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            product = serializer.save()
        except IntegrityError as e:
            logger.warning(f"Product create integrity error by {request.user.email}: {e}")
            return Response(
                {'error': 'Product could not be created due to duplicate unique fields (e.g., SKU).'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Log action
        self.log_action(request, 'create_product', product)
        
        logger.info(f"Product {product.id} created by {request.user.email}")
        
        return Response(
            {
                'message': 'Product created successfully',
                'data': AdminProductSerializer(product).data
            },
            status=status.HTTP_201_CREATED
        )

    def update_product(self, request, pk=None, product_id=None):
        """
        Update product.
        PATCH /api/admin/dashboard/products/{id}/
        """
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        from apps.admin.serializers import AdminProductSerializer
        
        # Track changes
        old_data = {
            'name': product.name,
            'price': str(product.price),
            'stock': product.stock,
            'featured': product.featured,
            'is_active': product.is_active,
        }
        
        serializer = AdminProductSerializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            product = serializer.save()
        except IntegrityError as e:
            logger.warning(f"Product update integrity error by {request.user.email} on product {product_id}: {e}")
            return Response(
                {'error': 'Product could not be updated due to duplicate unique fields (e.g., SKU).'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        new_data = {
            'name': product.name,
            'price': str(product.price),
            'stock': product.stock,
            'featured': product.featured,
            'is_active': product.is_active,
        }
        
        changes = {k: {'old': old_data[k], 'new': new_data[k]} for k in old_data if old_data[k] != new_data[k]}
        
        # Log action
        if changes:
            self.log_action(request, 'update_product', product, changes)
            logger.info(f"Product {product.id} updated by {request.user.email}")
        
        return Response(
            {
                'message': 'Product updated successfully',
                'data': AdminProductSerializer(product).data
            },
            status=status.HTTP_200_OK
        )

    def delete_product(self, request, pk=None, product_id=None):
        """
        Delete product.
        DELETE /api/admin/dashboard/products/{id}/
        """
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Log action before delete
        self.log_action(request, 'delete_product', product)
        
        product_name = product.name
        product.delete()
        
        logger.info(f"Product {product.id} ({product_name}) deleted by {request.user.email}")
        
        return Response(
            {'message': 'Product deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )

