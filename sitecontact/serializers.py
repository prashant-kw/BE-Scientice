from rest_framework import serializers
from .models import SiteInfo, ContactMessage

class SiteInfoSerializer(serializers.ModelSerializer):
    facebookUrl = serializers.CharField(source='facebook_url', read_only=True)
    instagramUrl = serializers.CharField(source='instagram_url', read_only=True)
    websiteUrl = serializers.CharField(source='website_url', read_only=True)

    class Meta:
        model = SiteInfo
        fields = ['phone', 'email', 'address', 'facebookUrl', 'instagramUrl', 'websiteUrl']

class ContactMessageSerializer(serializers.ModelSerializer):
    isRead = serializers.BooleanField(source='is_read', read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = ContactMessage
        fields = ['id', 'name', 'email', 'subject', 'message', 'isRead', 'createdAt']
        read_only_fields = ['id', 'isRead', 'createdAt']
