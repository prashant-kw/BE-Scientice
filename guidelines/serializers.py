from rest_framework import serializers
from common.utils import build_absolute_media_url
from .models import Guideline, ConferenceSociety

class GuidelineSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category_display', read_only=True)
    date = serializers.CharField(source='formatted_date', read_only=True)
    image = serializers.SerializerMethodField()
    documentUrl = serializers.SerializerMethodField()
    publishedAt = serializers.DateTimeField(source='published_at', read_only=True)
    society_code = serializers.CharField(source='society.code', read_only=True, default='')
    society_name = serializers.CharField(source='society.name', read_only=True, default='')

    class Meta:
        model = Guideline
        fields = [
            'id',
            'title',
            'guideline_type',
            'society',
            'society_code',
            'society_name',
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


class ConferenceSocietySerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceSociety
        fields = [
            'id',
            'code',
            'name',
            'description',
            'website_url',
            'order',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


