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
            # S3 storage returns full URL directly; local storage needs BACKEND_URL
            image_url = obj.image.url
            if image_url.startswith('http'):
                return image_url  # S3 URL
            # Local storage: prepend BACKEND_URL
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
            # S3 storage returns full URL directly; local storage needs BACKEND_URL
            video_url = obj.video.url
            if video_url.startswith('http'):
                return video_url  # S3 URL
            # Local storage: prepend BACKEND_URL
            return f"{settings.BACKEND_URL}{video_url}"
        return None
