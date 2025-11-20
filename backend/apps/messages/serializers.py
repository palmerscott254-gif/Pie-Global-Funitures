from rest_framework import serializers
from .models import UserMessage

class UserMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMessage
        fields = "__all__"
        read_only_fields = ("replied",)
