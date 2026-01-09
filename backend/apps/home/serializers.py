from rest_framework import serializers
from .models import SliderImage, HomeVideo

class SliderImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = SliderImage
        fields = "__all__"
    
    def get_image(self, obj):
        """Return absolute URL for image (S3 or local)"""
        from django.conf import settings
        if obj.image:
            # If using S3 storage, image.url is already the S3 URL
            if settings.USE_S3:
                return obj.image.url
            
            # Local storage: prepend BACKEND_URL
            image_url = obj.image.url
            if image_url.startswith('http'):
                return image_url
            return f"{settings.BACKEND_URL}{image_url}"
        return None

class HomeVideoSerializer(serializers.ModelSerializer):
    video = serializers.SerializerMethodField()
    
    class Meta:
        model = HomeVideo
        fields = "__all__"
    
    def get_video(self, obj):
        """Return absolute URL for video (S3 or local)"""
        from django.conf import settings
        if obj.video:
            # If using S3 storage, video.url is already the S3 URL
            if settings.USE_S3:
                return obj.video.url
            
            # Local storage: prepend BACKEND_URL
            video_url = obj.video.url
            if video_url.startswith('http'):
                return video_url
            return f"{settings.BACKEND_URL}{video_url}"
        return None
