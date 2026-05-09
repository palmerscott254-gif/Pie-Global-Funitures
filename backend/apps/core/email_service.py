"""Email service with robust error handling."""
import logging
from typing import List, Optional, Dict, Any
from django.conf import settings
from django.core.mail import send_mail
from django.utils.html import escape

logger = logging.getLogger(__name__)


class EmailService:
    """Handle email sending with safety checks and error handling."""

    @staticmethod
    def is_configured() -> bool:
        """Check if email backend is properly configured."""
        email_backend = getattr(settings, "EMAIL_BACKEND", "") or ""
        is_smtp = "smtp" in email_backend.lower()
        
        if not is_smtp:
            return False

        # Check credentials
        has_host = bool(getattr(settings, "EMAIL_HOST", None))
        has_user = bool(getattr(settings, "EMAIL_HOST_USER", None))
        has_password = bool(str(getattr(settings, "EMAIL_HOST_PASSWORD", "")).strip())

        return has_host and has_user and has_password

    @staticmethod
    def send_email(
        subject: str,
        message: str,
        recipient_list: List[str],
        from_email: Optional[str] = None,
        fail_silently: bool = False,
    ) -> bool:
        """Send email with safety checks.
        
        Args:
            subject: Email subject
            message: Email body
            recipient_list: List of recipient emails
            from_email: Sender email (defaults to DEFAULT_FROM_EMAIL)
            fail_silently: If True, log failures instead of raising
            
        Returns:
            True if successful, False otherwise
        """
        if not EmailService.is_configured():
            logger.warning("Email not configured. Skipping send.")
            return False

        try:
            from_email = from_email or settings.DEFAULT_FROM_EMAIL
            
            # Sanitize inputs
            subject = str(subject).replace("\n", "").replace("\r", "")[:200]
            message = str(message)[:10000]
            recipient_list = [str(r).strip() for r in recipient_list if r]

            if not recipient_list:
                logger.warning("No recipients provided for email")
                return False

            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=recipient_list,
                fail_silently=False,
            )

            logger.info(f"Email sent: {subject} to {recipient_list}")
            return True

        except Exception as e:
            msg = f"Failed to send email: {e}"
            if fail_silently:
                logger.error(msg)
                return False
            logger.exception(msg)
            raise

    @staticmethod
    def send_admin_notification(
        subject: str,
        body: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Send notification to admin(s).
        
        Args:
            subject: Email subject
            body: Email body
            metadata: Additional context (message_id, order_id, etc.)
            
        Returns:
            True if successful
        """
        recipients = getattr(settings, "EMAIL_NOTIFICATIONS_TO", [settings.DEFAULT_FROM_EMAIL])
        
        # Build detailed message with metadata
        full_body = body
        if metadata:
            full_body += "\n\n" + "=" * 50 + "\nMetadata:\n"
            for key, value in metadata.items():
                full_body += f"{key}: {value}\n"

        return EmailService.send_email(
            subject=subject,
            message=full_body,
            recipient_list=recipients,
            fail_silently=True,
        )


class AdminNotificationEmail:
    """Build admin notification emails."""

    @staticmethod
    def new_contact_message(message) -> tuple:
        """Build email for new contact message.
        
        Returns:
            Tuple of (subject, body)
        """
        safe_name = escape(message.name or "").replace("\n", "").replace("\r", "")[:100]
        safe_email = escape(message.email or "").replace("\n", "").replace("\r", "")[:254]
        safe_phone = escape(message.phone or "N/A").replace("\n", "").replace("\r", "")[:20]

        admin_url = f"{settings.BACKEND_URL}/admin/messages/usermessage/{message.id}/change/"

        subject = f"New Message from {safe_name}"

        body = f"""
New Customer Message Received
{'='*50}

From: {safe_name}
Email: {safe_email}
Phone: {safe_phone}

Message:
{message.message[:1000]}

{'='*50}
Received: {message.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}
Message ID: {message.id}

View in Admin: {admin_url}

---
This is an automated notification from Pie Global Furniture.
        """

        return subject, body

    @staticmethod
    def new_order(order) -> tuple:
        """Build email for new order.
        
        Returns:
            Tuple of (subject, body)
        """
        safe_name = escape(order.name or "").replace("\n", "").replace("\r", "")[:100]
        safe_email = escape(order.email or "").replace("\n", "").replace("\r", "")[:254]

        admin_url = f"{settings.BACKEND_URL}/admin/orders/order/{order.id}/change/"

        subject = f"New Order from {safe_name} - ${order.total_amount}"

        item_list = "\n".join(
            [f"  - {item.get('name')}: {item.get('qty')} x ${item.get('price')}"
             for item in (order.items or [])]
        )

        body = f"""
New Order Received
{'='*50}

Order ID: {order.id}
Customer: {safe_name}
Email: {safe_email}
Phone: {order.phone}

Address: {order.address}
City: {order.city}
Postal Code: {order.postal_code}

Items:
{item_list}

Total: ${order.total_amount}

{'='*50}
Received: {order.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}

View in Admin: {admin_url}

---
This is an automated notification from Pie Global Furniture.
        """

        return subject, body
