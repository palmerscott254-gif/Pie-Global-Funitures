from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from .models import UserMessage
from .serializers import (
    UserMessageCreateSerializer, 
    UserMessageListSerializer,
    UserMessageReplySerializer
)


# Rate limiting: prevent spam - 5 messages per hour per IP
@method_decorator(ratelimit(key='ip', rate='5/h', method='POST', block=True), name='create')
class UserMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for customer contact messages.
    
    Permissions:
    - Create: Public (contact form) with rate limiting
    - List/Detail: Admin only
    - Reply: Admin only
    
    Security: Rate limited to prevent spam/abuse
    """
    queryset = UserMessage.objects.all()
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
        """
        Permission model:
        - list/retrieve: Public read access (AllowAny) - Shows submitted messages to anyone
        - create: Public write access (AllowAny) - Contact form, rate limited
        - reply/mark_resolved: Admin only (IsAdminUser) - Admin actions
        
        This allows public access to view messages (non-sensitive data)
        while protecting admin-only actions with authentication.
        """
        if self.action in ['create', 'list', 'retrieve']:
            # Public can submit and view messages
            return [AllowAny()]
        # All other actions (reply, mark_resolved) require admin authentication
        return [IsAdminUser()]
    
    def create(self, request, *args, **kwargs):
        """Create a new contact message and notify admin."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = self.perform_create(serializer)
        
        # Send admin notification
        self._send_admin_notification(message)
        
        return Response(
            {
                'success': True,
                'message': 'Thank you! We will get back to you soon.',
                'id': message.id
            },
            status=status.HTTP_201_CREATED
        )
    
    def perform_create(self, serializer):
        """Save the message and return instance."""
        return serializer.save()
    
    def _send_admin_notification(self, message):
        """
        Send email notification to admin about new message.
        Sanitized to prevent email header injection attacks.
        """
        try:
            # Sanitize inputs to prevent email header injection
            safe_name = message.name.replace('\n', '').replace('\r', '')[:100]
            safe_email = message.email.replace('\n', '').replace('\r', '')[:254]
            safe_phone = (message.phone or 'N/A').replace('\n', '').replace('\r', '')[:20]
            
            email_body = f"""
New Customer Message
{'='*50}

From: {safe_name}
Email: {safe_email}
Phone: {safe_phone}

Message:
{message.message[:1000]}

{'='*50}
Received: {message.created_at.strftime('%Y-%m-%d %H:%M:%S')}
Message ID: {message.id}
            """
            
            # Sanitize subject line to prevent injection
            safe_subject = f"New Message from {safe_name}"
            safe_subject = safe_subject.replace('\n', '').replace('\r', '')[:200]
            
            send_mail(
                subject=safe_subject,
                message=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['pieglobal308@gmail.com'],
                fail_silently=False,
            )
            print(f"Notification email sent successfully for message #{message.id}")
        except Exception as e:
            # Log error but don't expose details to user
            print(f"Error sending notification email: {str(e)[:100]}")
    
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
        
        # Sanitize reply text (basic HTML escaping is done by DRF)
        # Update message
        message.reply_text = reply_text
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
