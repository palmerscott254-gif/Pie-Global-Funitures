from rest_framework import serializers
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
    
    def validate_items(self, value):
        """Validate items structure."""
        if not isinstance(value, list) or len(value) == 0:
            raise serializers.ValidationError("Items must be a non-empty array.")
        
        for item in value:
            required_fields = ['product_id', 'name', 'price', 'qty']
            for field in required_fields:
                if field not in item:
                    raise serializers.ValidationError(f"Each item must have '{field}' field.")
            
            if item['qty'] <= 0:
                raise serializers.ValidationError("Quantity must be greater than zero.")
            if item['price'] <= 0:
                raise serializers.ValidationError("Price must be greater than zero.")
        
        return value
    
    def validate_phone(self, value):
        """Basic phone validation."""
        if not value or len(value) < 8:
            raise serializers.ValidationError("Please provide a valid phone number.")
        return value


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
