from rest_framework import serializers
from django.utils.html import escape
from decimal import Decimal, InvalidOperation
import re
from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for creating and viewing orders."""
    
    class Meta:
        model = Order
        fields = [
            'id', 'name', 'email', 'phone', 'address', 'city', 'postal_code',
            'items', 'total_amount', 'status', 'paid', 'payment_method',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_name(self, value):
        """Validate and sanitize name."""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters long.")
        return escape(value.strip()[:100])
    
    def validate_email(self, value):
        """Validate email format."""
        if not value:
            raise serializers.ValidationError("Email is required.")
        value = value.strip().lower()
        if len(value) > 254:
            raise serializers.ValidationError("Email address is too long.")
        return value
    
    def validate_address(self, value):
        """Sanitize address to prevent XSS."""
        if value:
            return escape(value.strip()[:200])
        return value
    
    def validate_city(self, value):
        """Sanitize city name."""
        if value:
            return escape(value.strip()[:100])
        return value
    
    def validate_postal_code(self, value):
        """Sanitize postal code."""
        if value:
            # Allow alphanumeric and basic punctuation for international postal codes
            cleaned = re.sub(r'[^A-Za-z0-9\s\-]', '', value)
            return cleaned[:20]
        return value
    
    def validate_notes(self, value):
        """Sanitize order notes."""
        if value:
            cleaned = escape(value.strip())
            if len(cleaned) > 500:
                raise serializers.ValidationError("Notes are too long (max 500 characters).")
            return cleaned
        return value
    
    def validate_items(self, value):
        """Validate items structure and prevent manipulation."""
        if not isinstance(value, list) or len(value) == 0:
            raise serializers.ValidationError("Items must be a non-empty array.")
        
        if len(value) > 100:  # Prevent excessive items
            raise serializers.ValidationError("Too many items in order (max 100).")
        
        for idx, item in enumerate(value):
            required_fields = ['product_id', 'name', 'price', 'qty']
            for field in required_fields:
                if field not in item:
                    raise serializers.ValidationError(f"Item {idx}: missing '{field}' field.")
            
            # Validate quantity
            try:
                qty = int(item['qty'])
                if qty <= 0 or qty > 1000:
                    raise serializers.ValidationError(f"Item {idx}: invalid quantity.")
            except (ValueError, TypeError):
                raise serializers.ValidationError(f"Item {idx}: quantity must be a number.")
            
            # Validate price
            try:
                price = Decimal(str(item['price']))
                if price <= 0 or price > Decimal('1000000'):
                    raise serializers.ValidationError(f"Item {idx}: invalid price.")
            except (InvalidOperation, ValueError, TypeError):
                raise serializers.ValidationError(f"Item {idx}: price must be a valid number.")
            
            # Sanitize item name
            if 'name' in item:
                item['name'] = escape(str(item['name'])[:200])
        
        return value
    
    def validate_phone(self, value):
        """Validate and sanitize phone number."""
        if not value or len(value) < 8:
            raise serializers.ValidationError("Please provide a valid phone number.")
        # Remove potentially malicious characters
        cleaned = re.sub(r'[^0-9+\-\s()]', '', value)
        return cleaned[:20]


class OrderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for order lists."""
    
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'name', 'phone', 'total_amount', 
            'status', 'paid', 'item_count', 'created_at'
        ]
    
    def get_item_count(self, obj):
        """Calculate total items in order."""
        return len(obj.items) if obj.items else 0
