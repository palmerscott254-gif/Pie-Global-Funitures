"""Refactored message views using MessageService with improved error handling."""
import logging
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from apps.messages.models import UserMessage
from apps.messages.serializers import (
    UserMessageCreateSerializer,
    UserMessageListSerializer,
    UserMessageReplySerializer,
)
from apps.messages.message_service import MessageService
from apps.core.response_helpers import ResponseFormatter, PaginationHelper
from apps.core.audit import extract_client_ip

logger = logging.getLogger(__name__)


# CSRF-exempt SessionAuthentication for public API POST (contact form)
class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return None


@method_decorator(ratelimit(key='ip', rate='5/h', method='POST', block=True), name='create')
class UserMessageViewSet(viewsets.ModelViewSet):
    \"\"\"ViewSet for customer contact messages.
    
    Endpoints:
    - POST /messages/ - Create message (rate limited 5/hour per IP)
    - GET /messages/ - List messages (admin only)
    - GET /messages/{id}/ - Get message details (admin only)
    - POST /messages/{id}/reply/ - Reply to message (admin only)
    - POST /messages/{id}/mark_resolved/ - Mark resolved (admin only)
    
    Security:
    - Public create with rate limiting
    - Admin-only list/reply
    - CSRF exemption only for public POST
    \"\"\"
    queryset = UserMessage.objects.all()
    authentication_classes = [CsrfExemptSessionAuthentication]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        \"\"\"Return appropriate serializer based on action.\"\"\"
        if self.action == 'create':
            return UserMessageCreateSerializer
        elif self.action == 'reply':
            return UserMessageReplySerializer
        return UserMessageListSerializer

    def get_permissions(self):
        \"\"\"Public create, admin-only other actions.\"\"\"
        if self.action == 'create':
            return [AllowAny()]
        return [IsAdminUser()]

    def list(self, request, *args, **kwargs):
        \"\"\"List messages with pagination (admin only).\"\"\"
        queryset = self.filter_queryset(self.get_queryset())
        
        paginator = PaginationHelper.paginate_queryset(queryset, request)
        if paginator:
            serializer = self.get_serializer(paginator, many=True)
            return PaginationHelper.get_paginated_response(paginator, serializer.data, request)
        
        serializer = self.get_serializer(queryset, many=True)
        return ResponseFormatter.success(data={'results': serializer.data})

    def create(self, request, *args, **kwargs):
        \"\"\"Create a new customer message (rate limited).\"\"\"
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return ResponseFormatter.validation_error(serializer.errors)

        try:
            message = MessageService.create_message(
                name=serializer.validated_data['name'],
                email=serializer.validated_data['email'],
                phone=serializer.validated_data.get('phone'),
                message=serializer.validated_data['message'],
                request=request,
            )

            # Send admin notification in background
            MessageService().enqueue_task(
                MessageService.send_admin_notification,
                message,
            )

            logger.info(f\"Message created: {message.id} from {message.email}\")

            return ResponseFormatter.created(
                message='Thank you! We will get back to you soon.',
                data={'id': str(message.id)},
            )

        except Exception as e:
            logger.exception(f\"Failed to create message: {e}\")
            return ResponseFormatter.server_error()

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reply(self, request, pk=None):
        \"\"\"Admin replies to a message.\"\"\"
        message = self.get_object()
        reply_text = request.data.get('reply_text', '').strip()

        if not reply_text:
            return ResponseFormatter.error(
                'reply_text is required and cannot be empty',
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(reply_text) < 5:
            return ResponseFormatter.error(
                'Reply must be at least 5 characters long',
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(reply_text) > 2000:
            return ResponseFormatter.error(
                'Reply is too long (max 2000 characters)',
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            updated_message = MessageService.reply_to_message(
                message=message,
                reply_text=reply_text,
                user_id=str(request.user.id) if request.user else None,
            )

            return ResponseFormatter.success(
                message='Reply saved successfully',
                data=UserMessageListSerializer(updated_message).data,
            )
        except Exception as e:
            logger.exception(f\"Failed to reply to message: {e}\")
            return ResponseFormatter.server_error()

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def mark_resolved(self, request, pk=None):
        \"\"\"Mark a message as resolved.\"\"\"
        message = self.get_object()

        try:
            updated_message = MessageService.mark_message_resolved(
                message=message,
                user_id=str(request.user.id) if request.user else None,
            )

            return ResponseFormatter.success(
                message='Message marked as resolved',
                data=UserMessageListSerializer(updated_message).data,
            )
        except Exception as e:
            logger.exception(f\"Failed to mark message resolved: {e}\")
            return ResponseFormatter.server_error()
