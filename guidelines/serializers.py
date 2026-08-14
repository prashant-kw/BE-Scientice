from rest_framework import serializers
from common.utils import build_absolute_media_url
from .models import Guideline

class GuidelineSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category_display', read_only=True)
    date = serializers.CharField(source='formatted_date', read_only=True)
    image = serializers.SerializerMethodField()
    documentUrl = serializers.SerializerMethodField()
    publishedAt = serializers.DateTimeField(source='published_at', read_only=True)

    class Meta:
        model = Guideline
        fields = [
            'id',
            'title',
            'authority',
            'date',
            'category',
            'image',
            'summary',
            'documentUrl',
            'publishedAt',
        ]

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return build_absolute_media_url(request, obj.image)
        return build_absolute_media_url(request, obj.image_url)

    def get_documentUrl(self, obj):
        request = self.context.get('request')
        if obj.document_file:
            return build_absolute_media_url(request, obj.document_file)
        return build_absolute_media_url(request, obj.document_url)

