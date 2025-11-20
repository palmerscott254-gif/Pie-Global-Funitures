from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
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
        
        # TODO: Send notification to admin
        
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
