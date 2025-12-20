from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import UserMessage
from .serializers import (
    UserMessageCreateSerializer, 
    UserMessageListSerializer,
    UserMessageReplySerializer
)


class UserMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for customer contact messages.
    
    Permissions:
    - Create: Public (contact form)
    - List/Detail: Admin only
    - Reply: Admin only
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
        """Public can create, admins can view/reply."""
        if self.action == 'create':
            return []
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
        """Send email notification to admin about new message."""
        try:
            email_body = f"""
New Customer Message
{'='*50}

From: {message.name}
Email: {message.email}
Phone: {message.phone or 'N/A'}

Message:
{message.message}

{'='*50}
Received: {message.created_at.strftime('%Y-%m-%d %H:%M:%S')}
Message ID: {message.id}
            """
            
            send_mail(
                subject=f"New Message from {message.name}",
                message=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['pieglobal308@gmail.com'],
                fail_silently=False,
            )
            print(f"Notification email sent successfully for message #{message.id}")
        except Exception as e:
            print(f"Error sending notification email: {e}")
    
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
