"""Message/contact form service."""
import logging
from typing import Dict, Any

from apps.messages.models import UserMessage
from apps.core.audit import AuditLogger, extract_client_ip
from apps.core.email_service import EmailService, AdminNotificationEmail
from apps.core.tasks import BackgroundTaskMixin

logger = logging.getLogger(__name__)


class MessageService(BackgroundTaskMixin):
    """Handle customer message operations."""

    @staticmethod
    def create_message(
        name: str,
        email: str,
        phone: str = None,
        message: str = None,
        request=None,
    ) -> UserMessage:
        """Create a new customer message.
        
        Args:
            name: Customer name
            email: Customer email
            phone: Customer phone
            message: Message content
            request: HTTP request (for IP extraction)
            
        Returns:
            Created UserMessage instance
        """
        try:
            msg = UserMessage.objects.create(
                name=name,
                email=email,
                phone=phone or "",
                message=message or "",
                status="new",
            )

            logger.info(f"Message created: {msg.id} from {email}")

            # Log audit event
            ip = extract_client_ip(request) if request else None
            AuditLogger.log_message_created(str(msg.id), email, ip)

            return msg

        except Exception as e:
            logger.exception(f"Failed to create message: {e}")
            raise

    @staticmethod
    def send_admin_notification(message: UserMessage) -> bool:
        """Send admin notification for new message (background task).
        
        Args:
            message: UserMessage instance
            
        Returns:
            True if sent successfully
        """
        try:
            subject, body = AdminNotificationEmail.new_contact_message(message)
            return EmailService.send_admin_notification(
                subject=subject,
                body=body,
                metadata={"message_id": str(message.id)},
            )
        except Exception:
            logger.exception(f"Failed to send admin notification for message {message.id}")
            return False

    @staticmethod
    def reply_to_message(message: UserMessage, reply_text: str, user_id: str = None) -> UserMessage:
        """Admin reply to a customer message.
        
        Args:
            message: UserMessage instance
            reply_text: Reply content
            user_id: Admin user ID
            
        Returns:
            Updated UserMessage instance
        """
        try:
            from django.utils import timezone

            message.reply_text = reply_text
            message.status = "replied"
            message.replied_at = timezone.now()
            message.save()

            logger.info(f"Message replied: {message.id}")

            # Log audit event
            AuditLogger.log_event(
                AuditLogger.MESSAGE_REPLIED,
                user_id=user_id,
                resource_id=str(message.id),
                resource_type="message",
                status="success",
            )

            return message

        except Exception as e:
            logger.exception(f"Failed to reply to message {message.id}: {e}")
            raise

    @staticmethod
    def mark_message_resolved(message: UserMessage, user_id: str = None) -> UserMessage:
        """Mark a message as resolved.
        
        Args:
            message: UserMessage instance
            user_id: Admin user ID
            
        Returns:
            Updated UserMessage instance
        """
        try:
            message.status = "resolved"
            message.save()

            logger.info(f"Message marked resolved: {message.id}")

            # Log audit event
            AuditLogger.log_event(
                AuditLogger.MESSAGE_RESOLVED,
                user_id=user_id,
                resource_id=str(message.id),
                resource_type="message",
                status="success",
            )

            return message

        except Exception as e:
            logger.exception(f"Failed to mark message resolved {message.id}: {e}")
            raise
