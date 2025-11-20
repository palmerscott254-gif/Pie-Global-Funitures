from rest_framework import serializers
from .models import SliderImage, HomeVideo

class SliderImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = SliderImage
        fields = "__all__"
    
    def get_image(self, obj):
        """Return absolute URL for image"""
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            # Fallback if no request in context
            from django.conf import settings
            return f"{settings.BACKEND_URL}{obj.image.url}"
        return None

class HomeVideoSerializer(serializers.ModelSerializer):
    video = serializers.SerializerMethodField()
    
    class Meta:
        model = HomeVideo
        fields = "__all__"
    
    def get_video(self, obj):
        """Return absolute URL for video"""
        request = self.context.get('request')
        if obj.video and hasattr(obj.video, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.video.url)
            # Fallback if no request in context
            from django.conf import settings
            return f"{settings.BACKEND_URL}{obj.video.url}"
        return None
