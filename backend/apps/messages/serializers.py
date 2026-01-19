from rest_framework import serializers
from django.utils.html import escape
import re
from .models import UserMessage

class UserMessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new messages (public use)."""
    # Honeypot field: bots often fill this; real users won't. Must be empty.
    honeypot = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = UserMessage
        fields = ('name', 'email', 'phone', 'message', 'honeypot')

    def validate(self, attrs):
        # Basic honeypot check
        hp = attrs.get('honeypot', '')
        if hp and hp.strip():
            raise serializers.ValidationError({
                'non_field_errors': ['Invalid submission.']
            })
        return super().validate(attrs)

    def validate_name(self, value):
        """Validate and sanitize name input."""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters long.")
        # Sanitize to prevent XSS - escape HTML characters
        return escape(value.strip()[:100])  # Limit length

    def validate_email(self, value):
        """Validate email is provided and properly formatted."""
        if not value:
            raise serializers.ValidationError("Email is required.")
        # Additional email format validation (DRF does basic validation)
        value = value.strip().lower()
        if len(value) > 254:  # RFC 5321
            raise serializers.ValidationError("Email address is too long.")
        return value

    def validate_phone(self, value):
        """Validate and sanitize phone number."""
        if value:
            # Remove non-numeric characters except + and -
            cleaned = re.sub(r'[^0-9+\-\s()]', '', value)
            return cleaned[:20]  # Limit length
        return value

    def validate_message(self, value):
        """Validate and sanitize message content."""
        if not value or len(value.strip()) < 5:
            raise serializers.ValidationError("Message must be at least 5 characters long.")
        # Sanitize to prevent XSS - escape HTML characters
        cleaned = escape(value.strip())
        if len(cleaned) > 2000:  # Limit message length
            raise serializers.ValidationError("Message is too long (max 2000 characters).")
        # Basic spam heuristic: excessive links
        link_count = len(re.findall(r'https?://', cleaned))
        if link_count > 3:
            raise serializers.ValidationError("Message contains too many links.")
        return cleaned

    def create(self, validated_data):
        # Remove honeypot before saving to model
        validated_data.pop('honeypot', None)
        return super().create(validated_data)

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
