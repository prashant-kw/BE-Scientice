from rest_framework import serializers
from common.utils import build_absolute_media_url
from .models import EducationCategory, EducationResource

class EducationCategorySerializer(serializers.ModelSerializer):
    isActive = serializers.BooleanField(source='is_active', read_only=True)

    class Meta:
        model = EducationCategory
        fields = ['id', 'key', 'title', 'description', 'icon', 'order', 'is_active', 'isActive']

class EducationResourceSerializer(serializers.ModelSerializer):
    categoryKey = serializers.CharField(source='category.key', read_only=True)
    categoryTitle = serializers.CharField(source='category.title', read_only=True)
    fileUrl = serializers.SerializerMethodField()
    externalUrl = serializers.CharField(source='external_url', read_only=True)
    publishedAt = serializers.DateTimeField(source='published_at', read_only=True)

    class Meta:
        model = EducationResource
        fields = [
            'id',
            'title',
            'description',
            'body',
            'icon',
            'categoryKey',
            'categoryTitle',
            'fileUrl',
            'externalUrl',
            'publishedAt',
        ]

    def get_fileUrl(self, obj):
        request = self.context.get('request')
        if obj.file:
            return build_absolute_media_url(request, obj.file)
        return ''

