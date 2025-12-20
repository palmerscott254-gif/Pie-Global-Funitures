from rest_framework import serializers
from .models import UserMessage

class UserMessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new messages (public use)."""
    class Meta:
        model = UserMessage
        fields = ('name', 'email', 'phone', 'message')
    
    def validate_email(self, value):
        """Validate email is provided."""
        if not value:
            raise serializers.ValidationError("Email is required.")
        return value
    
    def validate_message(self, value):
        """Validate message is not empty."""
        if not value or len(value.strip()) < 5:
            raise serializers.ValidationError("Message must be at least 5 characters long.")
        return value

class UserMessageReplySerializer(serializers.ModelSerializer):
    """Serializer for admin replies."""
    class Meta:
        model = UserMessage
        fields = ('id', 'name', 'email', 'message', 'status', 'reply_text', 'replied_at', 'created_at')
        read_only_fields = ('id', 'name', 'email', 'message', 'created_at')

class UserMessageListSerializer(serializers.ModelSerializer):
    """Serializer for listing messages."""
    class Meta:
        model = UserMessage
        fields = ('id', 'name', 'email', 'phone', 'message', 'status', 'reply_text', 'created_at', 'updated_at')
        read_only_fields = fields
