from rest_framework import serializers
from django.conf import settings
from apps.core.media_utils import get_absolute_media_url
from .models import Product
import logging

logger = logging.getLogger('django')


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
        """Return absolute URL for main image. Always returns absolute URL for S3 CORS compliance."""
        if not obj.main_image:
            return None
        try:
            raw_url = str(obj.main_image.url)
            sanitized = self._sanitize_media_url(raw_url)
            return get_absolute_media_url(sanitized)
        except Exception as e:
            logger.error(f"[ProductSerializer] Error getting image URL for product {obj.id}: {str(e)}")
            return None
    
    def get_gallery(self, obj):
        """Return absolute URLs for gallery images"""
        if not obj.gallery or not isinstance(obj.gallery, list):
            return []
        
        gallery_urls = []
        for image_path in obj.gallery:
            if image_path:
                try:
                    sanitized = self._sanitize_media_url(image_path)
                    if not sanitized:
                        continue

                    if sanitized.startswith('http://') or sanitized.startswith('https://'):
                        absolute_url = sanitized
                    else:
                        # gallery items are stored as relative paths
                        gallery_url = f"{settings.MEDIA_URL.rstrip('/')}/{sanitized.lstrip('/')}"
                        absolute_url = get_absolute_media_url(gallery_url)

                    if absolute_url:
                        gallery_urls.append(absolute_url)
                except Exception as e:
                    logger.error(f"[ProductSerializer] Error processing gallery image {image_path}: {str(e)}")
                    continue
        
        return gallery_urls

    @staticmethod
    def _sanitize_media_url(url_value: str):
        """Normalize stored media paths to avoid double /media/ prefixes."""
        if not url_value:
            return None
        url_str = str(url_value)
        # Deduplicate a single extra media/ prefix
        url_str = url_str.replace('/media/media/', '/media/', 1)
        url_str = url_str.replace('media/media/', 'media/', 1)
        return url_str
    
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
        """Return absolute URL for main image. Always returns absolute URL for S3 CORS compliance."""
        if not obj.main_image:
            return None
        try:
            return get_absolute_media_url(obj.main_image.url)
        except Exception as e:
            logger.error(f"[ProductListSerializer] Error getting image URL for product {obj.id}: {str(e)}")
            return None
