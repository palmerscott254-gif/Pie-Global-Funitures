from rest_framework import serializers
from apps.core.media_utils import get_absolute_media_url
from .models import SliderImage, HomeVideo


class SliderImageSerializer(serializers.ModelSerializer):
    """Serializer for slider images with proper URL construction."""
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = SliderImage
        fields = ['id', 'title', 'image', 'order', 'active', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']
    
    def get_image(self, obj):
        """Return absolute URL for image (S3 or local)"""
        if obj.image:
            return get_absolute_media_url(obj.image.url)
        return None


class HomeVideoSerializer(serializers.ModelSerializer):
    """Serializer for hero videos with proper URL construction."""
    video = serializers.SerializerMethodField()
    
    class Meta:
        model = HomeVideo
        fields = ['id', 'title', 'video', 'active', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']
    
    def get_video(self, obj):
        """Return absolute URL for video (S3 or local)"""
        if obj.video:
            return get_absolute_media_url(obj.video.url)
        return None
