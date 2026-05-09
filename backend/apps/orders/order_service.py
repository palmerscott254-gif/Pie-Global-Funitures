"""Order service for order lifecycle management."""
import logging
from typing import Dict, Any, Optional
from decimal import Decimal
from django.db import transaction

from apps.orders.models import Order
from apps.core.audit import AuditLogger, extract_client_ip
from apps.core.email_service import EmailService, AdminNotificationEmail
from apps.core.tasks import BackgroundTaskMixin

logger = logging.getLogger(__name__)


class OrderService(BackgroundTaskMixin):
    """Handle order operations."""

    @staticmethod
    @transaction.atomic
    def create_order(
        name: str,
        email: str,
        phone: str,
        address: str,
        items: list,
        total_amount: Decimal,
        city: str = None,
        postal_code: str = None,
        payment_method: str = None,
        request=None,
    ) -> Order:
        """Create a new order.
        
        Args:
            name: Customer name
            email: Customer email
            phone: Customer phone
            address: Shipping address
            items: List of order items (with product_id, name, price, qty)
            total_amount: Total order amount
            city: City
            postal_code: Postal code
            payment_method: Payment method used
            request: HTTP request (for IP extraction)
            
        Returns:
            Created Order instance
        """
        try:
            order = Order.objects.create(
                name=name,
                email=email,
                phone=phone,
                address=address,
                city=city or "",
                postal_code=postal_code or "",
                items=items,
                total_amount=total_amount,
                status="pending",
                paid=False,
                payment_method=payment_method or "",
            )

            logger.info(f"Order created: {order.id} from {email} (${total_amount})")

            # Log audit event
            ip = extract_client_ip(request) if request else None
            AuditLogger.log_order_created(str(order.id), email, str(total_amount), ip)

            return order

        except Exception as e:
            logger.exception(f"Failed to create order: {e}")
            raise

    @staticmethod
    def send_admin_notification(order: Order) -> bool:
        """Send admin notification for new order (background task).
        
        Args:
            order: Order instance
            
        Returns:
            True if sent successfully
        """
        try:
            subject, body = AdminNotificationEmail.new_order(order)
            return EmailService.send_admin_notification(
                subject=subject,
                body=body,
                metadata={"order_id": str(order.id), "total": str(order.total_amount)},
            )
        except Exception:
            logger.exception(f"Failed to send admin notification for order {order.id}")
            return False

    @staticmethod
    @transaction.atomic
    def update_order_status(
        order: Order,
        new_status: str,
        user_id: str = None,
    ) -> Order:
        """Update order status.
        
        Args:
            order: Order instance
            new_status: New status value
            user_id: Admin user ID
            
        Returns:
            Updated Order instance
        """
        if new_status == order.status:
            logger.debug(f"Order status unchanged: {order.id}")
            return order

        old_status = order.status

        try:
            order.status = new_status
            order.save()

            logger.info(f"Order status updated: {order.id} ({old_status} -> {new_status})")

            # Log audit event
            AuditLogger.log_order_status_change(
                user_id=user_id or "system",
                order_id=str(order.id),
                old_status=old_status,
                new_status=new_status,
            )

            return order

        except Exception as e:
            logger.exception(f"Failed to update order status {order.id}: {e}")
            raise

    @staticmethod
    @transaction.atomic
    def mark_order_paid(
        order: Order,
        payment_method: str = None,
        user_id: str = None,
    ) -> Order:
        """Mark order as paid.
        
        Args:
            order: Order instance
            payment_method: Payment method used
            user_id: Admin user ID
            
        Returns:
            Updated Order instance
        """
        try:
            order.paid = True
            if payment_method:
                order.payment_method = payment_method
            order.save()

            logger.info(f"Order marked as paid: {order.id}")

            # Log audit event
            AuditLogger.log_event(
                AuditLogger.ORDER_PAID,
                user_id=user_id or "system",
                resource_id=str(order.id),
                resource_type="order",
                details={"payment_method": payment_method or "N/A"},
                status="success",
            )

            return order

        except Exception as e:
            logger.exception(f"Failed to mark order paid {order.id}: {e}")
            raise

    @staticmethod
    def get_order_by_id(order_id) -> Optional[Order]:
        """Retrieve order by ID."""
        try:
            return Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return None
