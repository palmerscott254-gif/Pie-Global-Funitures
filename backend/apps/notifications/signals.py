"""
Django signals for automatic notification triggers.

These signals automatically create notifications when specific events occur:
- Order created → Order Confirmed notification
- Payment processed → Payment Received notification
- Order shipped → Order Shipped notification
- Delivery status changes → Delivery Update notification
- etc.

Benefits:
- Decoupled: Notification creation doesn't require explicit calls
- Reliable: Triggers even if called from multiple places
- Maintainable: Centralized notification logic
- Scalable: Can be extended to more events easily
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
import logging

from .models import Notification, NotificationPreference
from .notification_service import NotificationFactory

logger = logging.getLogger(__name__)
User = get_user_model()


def _resolve_order_user(order_instance):
    user = getattr(order_instance, 'user', None)
    if user:
        return user

    email = getattr(order_instance, 'email', None)
    if not email:
        return None

    return User.objects.filter(email__iexact=email).first()


# ============================================
# USER-RELATED SIGNALS
# ============================================

@receiver(post_save, sender=User)
def create_notification_preference_for_new_user(sender, instance, created, **kwargs):
    """
    Create default NotificationPreference when new user is created.
    Ensures every user has preference settings (with defaults enabled).
    
    Allows users to customize preferences later.
    """
    if created:
        try:
            NotificationPreference.objects.create(user=instance)
            logger.debug(f"Created default notification preferences for user {instance.id}")
        except Exception as exc:
            logger.error(
                f"Error creating notification preferences for user {instance.id}: {str(exc)}",
                exc_info=True
            )


# ============================================
# ORDER-RELATED SIGNALS
# ============================================

@receiver(post_save, sender='orders.Order')
def notify_order_confirmed(sender, instance, created, **kwargs):
    """
    Trigger ORDER_CONFIRMED notification when order is created.
    
    Condition: Only on creation, not on updates
    """
    if created:
        try:
            user = _resolve_order_user(instance)
            if not user:
                return
            NotificationFactory.order_confirmed(user, instance)
            logger.info(f"Order confirmed notification sent for order {instance.id}")
        except Exception as exc:
            logger.error(
                f"Error sending order confirmed notification: {str(exc)}",
                exc_info=True
            )


@receiver(pre_save, sender='orders.Order')
def notify_order_status_change(sender, instance, **kwargs):
    """
    Trigger notifications when order status changes.
    
    Track status transitions and create appropriate notifications:
    - PENDING → SHIPPED: Notify with ORDER_SHIPPED
    - SHIPPED → DELIVERED: Notify with DELIVERED
    - SHIPPED → DELIVERY_FAILED: Notify with DELIVERY_FAILED
    - Any → REFUND_INITIATED: Notify with REFUND_STATUS
    
    Uses pre_save to compare old vs new status.
    """
    if not instance.pk:
        # New order, skip (handled by post_save)
        return
    
    try:
        # Get old instance from database
        old_instance = sender.objects.get(pk=instance.pk)
        old_status = old_instance.status
        new_status = instance.status
        user = _resolve_order_user(instance)

        if not user:
            return
        
        # Only act if status changed
        if old_status == new_status:
            return
        
        logger.info(
            f"Order {instance.id} status changed: {old_status} → {new_status}"
        )
        
        # RECEIVED (order acknowledged) notification for pending -> received
        if old_status == 'pending' and new_status == 'received':
            try:
                NotificationFactory.order_received(user, instance)
            except Exception:
                logger.exception('Failed to send order received notification')

        # received -> shipped notification
        if old_status == 'received' and new_status == 'shipped':
            try:
                NotificationFactory.order_shipped(user, instance,
                                                  tracking_number=getattr(instance, 'tracking_number', None),
                                                  carrier=getattr(instance, 'carrier', None))
            except Exception:
                logger.exception('Failed to send shipped notification after RECEIVED')

        # Delivery progress updates
        if new_status in {'out_for_delivery', 'delayed'}:
            status_message = 'Out for delivery' if new_status == 'out_for_delivery' else 'Delivery delayed'
            try:
                NotificationFactory.delivery_update(
                    user,
                    instance,
                    status_message,
                    tracking_info={'status': new_status},
                )
            except Exception:
                logger.exception('Failed to send delivery update notification')
        
        # DELIVERED notification
        elif new_status == 'delivered':
            NotificationFactory.delivered(user, instance)
            
            # Schedule review reminder for 3-7 days after delivery
            from apps.notifications.tasks import schedule_review_reminder
            from celery import current_app
            
            # Schedule task for 5 days from now
            schedule_review_reminder.apply_async(
                args=[instance.id],
                countdown=5 * 24 * 60 * 60  # 5 days in seconds
            )
        
        # DELIVERY_FAILED notification
        elif new_status == 'delivery_failed':
            reason = getattr(instance, 'delivery_failure_reason', None)
            NotificationFactory.delivery_failed(
                user,
                instance,
                reason=reason
            )
        
        # Handle refund status changes
        elif new_status == 'refund_initiated':
            refund_amount = getattr(instance, 'refund_amount', None)
            NotificationFactory.refund_status(
                user,
                instance,
                'initiated',
                amount=refund_amount
            )
        
        elif new_status == 'refund_completed':
            refund_amount = getattr(instance, 'refund_amount', None)
            NotificationFactory.refund_status(
                user,
                instance,
                'completed',
                amount=refund_amount
            )
    
    except sender.DoesNotExist:
        # Shouldn't happen, but handle gracefully
        logger.warning(f"Could not find existing order {instance.pk} for comparison")
    
    except Exception as exc:
        logger.error(
            f"Error handling order status change for order {instance.pk}: {str(exc)}",
            exc_info=True
        )


# ============================================
# PAYMENT-RELATED SIGNALS
# ============================================

def notify_payment_received(sender, instance, created, **kwargs):
    """
    Trigger PAYMENT_RECEIVED notification when payment is successfully processed.
    
    Condition: Only when payment status changes to SUCCESS
    """
    if instance.status == 'SUCCESS':
        try:
            order = instance.order
            if order.user:
                NotificationFactory.payment_received(
                    order.user,
                    order,
                    transaction_id=instance.transaction_id
                )
                logger.info(f"Payment confirmation notification sent for order {order.id}")
        except Exception as exc:
            logger.error(
                f"Error sending payment received notification: {str(exc)}",
                exc_info=True
            )


# ============================================
# PRODUCT-RELATED SIGNALS
# ============================================

@receiver(post_save, sender='products.Product')
def notify_restocked_items(sender, instance, **kwargs):
    """
    Trigger RESTOCKED_ITEM notification when product becomes available.
    
    Scenario:
    1. Product was out of stock (stock = 0)
    2. Admin restocks it (stock > 0)
    3. Notify users who viewed or wishlisted the product
    
    Note: Requires tracking of viewed products and wishlists.
    """
    if not instance.pk:
        return
    
    try:
        # Skip if product is still out of stock
        if instance.stock <= 0:
            return
        
        # Get old stock level
        old_instance = sender.objects.get(pk=instance.pk)
        old_stock = old_instance.stock
        
        # Only notify if going from out-of-stock to in-stock
        if old_stock > 0 or instance.stock <= 0:
            return
        
        logger.info(f"Product {instance.id} restocked, notifying interested users")
        
        # Find users who viewed this product
        # Note: Requires ProductView model to track user views
        try:
            from apps.products.models import ProductView
            
            product_viewers = ProductView.objects.filter(
                product=instance
            ).values_list('user_id', flat=True).distinct()
            
            for user_id in product_viewers:
                try:
                    user = User.objects.get(id=user_id)
                    NotificationFactory.item_restocked(user, instance)
                except User.DoesNotExist:
                    pass
        
        except ImportError:
            logger.warning("ProductView model not found, skipping restock notifications")
        
        # Also check wishlisted items
        try:
            from apps.products.models import Wishlist
            
            wishlist_users = Wishlist.objects.filter(
                product=instance
            ).values_list('user_id', flat=True).distinct()
            
            for user_id in wishlist_users:
                try:
                    user = User.objects.get(id=user_id)
                    NotificationFactory.item_restocked(user, instance)
                except User.DoesNotExist:
                    pass
        
        except ImportError:
            logger.warning("Wishlist model not found, skipping wishlist restock notifications")
    
    except sender.DoesNotExist:
        pass
    
    except Exception as exc:
        logger.error(
            f"Error handling product restock notification: {str(exc)}",
            exc_info=True
        )


# ============================================
# SUPPORT/WARRANTY-RELATED SIGNALS
# ============================================

def notify_warranty_updates(sender, instance, created, **kwargs):
    """
    Trigger WARRANTY_UPDATE notification when support ticket status changes.
    
    Covers:
    - Warranty claims
    - Support tickets
    - Product issues
    
    Note: Requires 'support' app with SupportTicket model
    """
    if created:
        return  # Handle changes, not creation
    
    try:
        old_instance = sender.objects.get(pk=instance.pk)
        
        if old_instance.status != instance.status:
            warranty_info = {
                'message': f"Your support ticket #{instance.ticket_number} status: {instance.get_status_display()}",
                'action_url': f"/support/tickets/{instance.id}",
                'metadata': {
                    'ticket_id': instance.id,
                    'ticket_number': instance.ticket_number,
                    'status': instance.status,
                }
            }
            
            from .notification_service import NotificationFactory
            NotificationFactory.warranty_update(instance.user, warranty_info)
    
    except sender.DoesNotExist:
        pass
    
    except Exception as exc:
        logger.error(
            f"Error handling warranty update notification: {str(exc)}",
            exc_info=True
        )


# ============================================
# ADMIN REPLY / MESSAGES
# ============================================

@receiver(pre_save, sender='user_messages.UserMessage')
def capture_message_previous_state(sender, instance, **kwargs):
    if not instance.pk:
        instance._previous_status = None
        instance._previous_reply_text = None
        return

    try:
        previous = sender.objects.get(pk=instance.pk)
        instance._previous_status = previous.status
        instance._previous_reply_text = previous.reply_text
    except sender.DoesNotExist:
        instance._previous_status = None
        instance._previous_reply_text = None


@receiver(post_save, sender='user_messages.UserMessage')
def notify_admin_reply(sender, instance, created, **kwargs):
    """
    Notify user when admin replies to their message. Trigger when status becomes 'replied'
    and `reply_text` is present. Avoid duplicate notifications if status unchanged.
    """
    if created:
        return

    previous_status = getattr(instance, '_previous_status', None)
    previous_reply_text = getattr(instance, '_previous_reply_text', None)

    # If status changed to replied or new reply_text was added, notify once per update
    became_replied = previous_status != 'replied' and instance.status == 'replied'
    got_new_reply = instance.reply_text and previous_reply_text != instance.reply_text
    if (became_replied or got_new_reply) and instance.reply_text:
        try:
            from .notification_service import NotificationFactory
            # Try to find user by email if available
            try:
                user = User.objects.filter(email__iexact=instance.email).first()
            except Exception:
                user = None

            if user:
                NotificationFactory.admin_reply_to_message(user, instance)
            else:
                logger.info(f"No registered user for message reply notification (email={instance.email})")

        except Exception:
            logger.exception('Failed to send admin reply notification')


# ============================================
# INVOICE-RELATED SIGNALS
# ============================================

def notify_invoice_ready(sender, instance, created, **kwargs):
    """
    Trigger INVOICE_READY notification when invoice is generated.
    
    Note: Requires 'orders' app with Invoice model
    """
    if created and instance.order.user:
        try:
            NotificationFactory.invoice_ready(
                instance.order.user,
                instance.order,
                invoice_url=instance.file_url if hasattr(instance, 'file_url') else None
            )
            logger.info(f"Invoice ready notification sent for order {instance.order.id}")
        except Exception as exc:
            logger.error(
                f"Error sending invoice ready notification: {str(exc)}",
                exc_info=True
            )


# ============================================
# LOYALTY/REWARDS-RELATED SIGNALS
# ============================================

def notify_loyalty_points(sender, instance, created, **kwargs):
    """
    Trigger LOYALTY_POINTS notification when points are earned or redeemed.
    
    Note: Requires 'loyalty' app with LoyaltyTransaction model
    """
    if created and instance.user:
        try:
            action_map = {
                'EARN': 'earned',
                'REDEEM': 'redeemed',
                'EXPIRE': 'expired',
            }
            
            action = action_map.get(instance.transaction_type, 'earned')
            points = abs(instance.points)  # Use absolute value
            
            NotificationFactory.loyalty_points(instance.user, points, action_type=action)
            logger.info(f"Loyalty points notification sent for user {instance.user.id}")
        
        except Exception as exc:
            logger.error(
                f"Error sending loyalty points notification: {str(exc)}",
                exc_info=True
            )


# ============================================
# DELIVERY TRACKING SIGNALS
# ============================================

def notify_delivery_update(sender, instance, created, **kwargs):
    """
    Trigger DELIVERY_UPDATE notification when tracking status is updated.
    
    Integrates with courier APIs (FedEx, UPS, DHL).
    Sends update whenever status changes.
    
    Note: Requires 'orders' app with TrackingUpdate model
    """
    if created and instance.order.user:
        try:
            NotificationFactory.delivery_update(
                instance.order.user,
                instance.order,
                instance.status_message or instance.get_status_display(),
                tracking_info={
                    'tracking_number': instance.order.tracking_number,
                    'status': instance.status,
                    'location': getattr(instance, 'location', None),
                    'timestamp': instance.updated_at.isoformat(),
                }
            )
            logger.info(f"Delivery update notification sent for order {instance.order.id}")
        
        except Exception as exc:
            logger.error(
                f"Error sending delivery update notification: {str(exc)}",
                exc_info=True
            )


# ============================================
# DELIVERY ETA SIGNALS
# ============================================

def notify_delivery_eta(sender, instance, created, **kwargs):
    """
    Trigger DELIVERY_ETA notification when estimated arrival is set.
    
    Example: "Expected tomorrow before 5PM"
    
    Note: Requires 'orders' app with DeliveryETA model
    """
    if created and instance.order.user:
        try:
            eta_time = instance.estimated_delivery.strftime('%A, %B %d at %I:%M %p')
            
            NotificationFactory.delivery_eta(
                instance.order.user,
                instance.order,
                eta_time,
                carrier=getattr(instance, 'carrier', None)
            )
            logger.info(f"Delivery ETA notification sent for order {instance.order.id}")
        
        except Exception as exc:
            logger.error(
                f"Error sending delivery ETA notification: {str(exc)}",
                exc_info=True
            )
