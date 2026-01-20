from rest_framework import serializers
from apps.core.media_utils import get_absolute_media_url
from .models import SliderImage, HomeVideo
import logging

logger = logging.getLogger('django')


class SliderImageSerializer(serializers.ModelSerializer):
    """Serializer for slider images with proper URL construction."""
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = SliderImage
        fields = ['id', 'title', 'image', 'order', 'active', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']
    
    def get_image(self, obj):
        """Return absolute URL for image. Always absolute for S3 CORS compliance."""
        if not obj.image:
            return None
        try:
            return get_absolute_media_url(obj.image.url)
        except Exception as e:
            logger.error(f"[SliderImageSerializer] Error getting image URL for slider {obj.id}: {str(e)}")
            return None


class HomeVideoSerializer(serializers.ModelSerializer):
    """Serializer for hero videos with proper URL construction."""
    video = serializers.SerializerMethodField()
    
    class Meta:
        model = HomeVideo
        fields = ['id', 'title', 'video', 'active', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']
    
    def get_video(self, obj):
        """Return absolute URL for video. Always absolute for S3 CORS compliance."""
        if not obj.video:
            return None
        try:
            return get_absolute_media_url(obj.video.url)
        except Exception as e:
            logger.error(f"[HomeVideoSerializer] Error getting video URL for video {obj.id}: {str(e)}")
            return None
