import logging
import threading

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from django.utils.html import escape

from .models import UserMessage
from .serializers import (
    UserMessageCreateSerializer,
    UserMessageListSerializer,
    UserMessageReplySerializer,
)

logger = logging.getLogger(__name__)


# CSRF-exempt SessionAuthentication for public API POST (contact form)
class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return None


# Rate limiting: prevent spam - 5 messages per hour per IP
@method_decorator(ratelimit(key='ip', rate='5/h', method='POST', block=True), name='create')
class UserMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for customer contact messages.
    
    Permissions:
    - Create: Public (contact form) with rate limiting
    - List/Detail: Public read access
    - Reply/Resolve: Admin only
    
    Security: Rate limited to prevent spam/abuse
    """
    queryset = UserMessage.objects.all()
    # Use CSRF-exempt for public contact form; admin actions protected by IsAdminUser
    authentication_classes = [CsrfExemptSessionAuthentication]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return UserMessageCreateSerializer
        elif self.action == 'reply':
            return UserMessageReplySerializer
        return UserMessageListSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAdminUser()]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exc:
            logger.info("Contact form validation failed: %s", exc.detail)
            return Response(
                {'success': False, 'errors': exc.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            message = serializer.save()
            logger.info(f"New contact message saved: ID={message.id}, Name={message.name}, Email={message.email}")
        except Exception:
            logger.exception("Failed to save contact message")
            return Response(
                {
                    'success': False,
                    'error': 'Unable to save your message right now. Please try again later.',
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Send admin notification in background to avoid delaying response
        self._send_admin_notification_async(message)

        return Response(
            {
                'success': True,
                'message': 'Thank you! We will get back to you soon.',
                'id': str(message.id),
            },
            status=status.HTTP_201_CREATED,
        )
    
    def perform_create(self, serializer):
        """Save the message and return instance."""
        return serializer.save()
    
    def _send_admin_notification_safe(self, message):
        try:
            # Skip sending if SMTP is not properly configured to avoid long hangs
            email_backend = getattr(settings, 'EMAIL_BACKEND', '') or ''
            is_smtp_backend = 'smtp' in email_backend.lower()
            missing_creds = not getattr(settings, 'EMAIL_HOST_USER', None) or not str(getattr(settings, 'EMAIL_HOST_PASSWORD', '')).strip()

            if is_smtp_backend and missing_creds:
                logger.warning("Skipping admin notification email: SMTP credentials missing or not configured.")
                return False

            safe_name = (message.name or '').replace('\n', '').replace('\r', '')[:100]
            safe_email = (message.email or '').replace('\n', '').replace('\r', '')[:254]
            safe_phone = (message.phone or 'N/A').replace('\n', '').replace('\r', '')[:20]

            # Admin dashboard URL
            admin_url = f"{settings.BACKEND_URL}/admin/messages/usermessage/{message.id}/change/"

            email_body = f"""
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

            safe_subject = f"New Message from {safe_name}".replace('\n', '').replace('\r', '')[:200]

            recipients = getattr(settings, 'EMAIL_NOTIFICATIONS_TO', [settings.DEFAULT_FROM_EMAIL])
            
            send_mail(
                subject=safe_subject,
                message=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=False,  # bubble up SMTP errors so we can log them
            )
            logger.info(f"Admin notification email sent for message #{message.id} to {recipients}")
            return True
        except Exception:
            logger.exception("Failed to send notification email for message #%s", message.id)
            return False

    def _send_admin_notification_async(self, message):
        try:
            thread = threading.Thread(
                target=self._send_admin_notification_safe,
                args=(message,),
                daemon=True,
            )
            thread.start()
            return True
        except Exception:
            logger.exception("Failed to schedule async notification email for message #%s", message.id)
            return False
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reply(self, request, pk=None):
        """Admin replies to a message."""
        message = self.get_object()
        reply_text = request.data.get('reply_text', '').strip()
        
        if not reply_text:
            return Response(
                {'error': 'reply_text is required and cannot be empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(reply_text) < 5:
            return Response(
                {'error': 'Reply must be at least 5 characters long'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(reply_text) > 2000:
            return Response(
                {'error': 'Reply is too long (max 2000 characters)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Sanitize reply text to prevent XSS
        message.reply_text = escape(reply_text)
        message.status = 'replied'
        message.replied_at = timezone.now()
        message.save()
        
        return Response(
            {
                'success': True,
                'message': 'Reply saved successfully',
                'data': UserMessageListSerializer(message).data
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def mark_resolved(self, request, pk=None):
        """Mark a message as resolved."""
        message = self.get_object()
        message.status = 'resolved'
        message.save()
        
        return Response(
            {
                'success': True,
                'message': 'Message marked as resolved',
                'data': UserMessageListSerializer(message).data
            },
            status=status.HTTP_200_OK
        )
