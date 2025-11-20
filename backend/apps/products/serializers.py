from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model with computed fields."""
    
    in_stock = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    main_image = serializers.SerializerMethodField()
    gallery = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'short_description',
            'price', 'compare_at_price', 'category', 'tags',
            'main_image', 'gallery', 'stock', 'sku',
            'dimensions', 'material', 'color', 'weight',
            'featured', 'is_active', 'on_sale',
            'meta_title', 'meta_description',
            'in_stock', 'discount_percentage',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at', 'in_stock', 'discount_percentage']
    
    def get_main_image(self, obj):
        """Return absolute URL for main image"""
        request = self.context.get('request')
        if obj.main_image and hasattr(obj.main_image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.main_image.url)
            # Fallback if no request in context
            from django.conf import settings
            return f"{settings.BACKEND_URL}{obj.main_image.url}"
        return None
    
    def get_gallery(self, obj):
        """Return absolute URLs for gallery images"""
        request = self.context.get('request')
        if obj.gallery:
            if isinstance(obj.gallery, list):
                gallery_urls = []
                for image_path in obj.gallery:
                    if image_path:
                        # Construct absolute URL for each gallery image
                        if request is not None:
                            full_url = request.build_absolute_uri(f"/media/{image_path}")
                        else:
                            from django.conf import settings
                            full_url = f"{settings.BACKEND_URL}/media/{image_path}"
                        gallery_urls.append(full_url)
                return gallery_urls
        return []
    
    def validate_price(self, value):
        """Ensure price is positive."""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value
    
    def validate(self, data):
        """Cross-field validation."""
        compare_price = data.get('compare_at_price')
        price = data.get('price')
        
        if compare_price and price and compare_price <= price:
            raise serializers.ValidationError({
                'compare_at_price': 'Compare at price must be greater than the regular price.'
            })
        
        return data


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product lists."""
    
    in_stock = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    main_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'short_description',
            'price', 'compare_at_price', 'category',
            'main_image', 'stock', 'featured', 'on_sale',
            'in_stock', 'discount_percentage'
        ]
    
    def get_main_image(self, obj):
        """Return absolute URL for main image"""
        request = self.context.get('request')
        if obj.main_image and hasattr(obj.main_image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.main_image.url)
            # Fallback if no request in context
            from django.conf import settings
            return f"{settings.BACKEND_URL}{obj.main_image.url}"
        return None
