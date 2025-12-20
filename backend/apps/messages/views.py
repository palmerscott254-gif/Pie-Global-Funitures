from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.core.mail import send_mail
from django.conf import settings
from .models import UserMessage
from .serializers import UserMessageSerializer


class UserMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for customer contact messages.
    
    Create: Public (contact form)
    List/Detail/Reply: Admin only
    """
    queryset = UserMessage.objects.all()
    serializer_class = UserMessageSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['replied']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """Public can create messages, admins can view/reply."""
        if self.action == 'create':
            return []
        return [IsAdminUser()]
    
    def create(self, request, *args, **kwargs):
        """Create a new contact message."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Send notification email to admin
        try:
            message_data = serializer.data
            email_body = f"""
New Contact Form Submission

Name: {message_data.get('name', 'N/A')}
Email: {message_data.get('email', 'N/A')}
Phone: {message_data.get('phone', 'N/A')}

Message:
{message_data.get('message', 'N/A')}

---
Received at: {message_data.get('created_at', 'N/A')}
"""
            
            send_mail(
                subject=f"New Contact Form Message from {message_data.get('name', 'Customer')}",
                message=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['pieglobal308@gmail.com'],
                fail_silently=True,
            )
        except Exception as e:
            # Log error but don't fail the request
            print(f"Failed to send notification email: {e}")
        
        return Response(
            {
                'message': 'Thank you for contacting us. We will respond soon.',
                'data': serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reply(self, request, pk=None):
        """Admin replies to a message."""
        msg = self.get_object()
        reply_text = request.data.get('reply_text')
        
        if not reply_text:
            return Response(
                {'error': 'reply_text is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        msg.replied = True
        msg.reply_text = reply_text
        msg.save()
        
        # TODO: Send email to customer with reply
        
        return Response(self.get_serializer(msg).data)
