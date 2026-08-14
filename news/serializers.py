from rest_framework import serializers
from common.utils import build_absolute_media_url
from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category_display', read_only=True)
    headlineTag = serializers.CharField(source='headline_tag', read_only=True)
    reference = serializers.CharField(source='reference_url', read_only=True)
    referenceName = serializers.CharField(source='reference_name', read_only=True)
    date = serializers.CharField(source='formatted_date', read_only=True)
    readTime = serializers.CharField(source='formatted_read_time', read_only=True)
    image = serializers.SerializerMethodField()
    documentUrl = serializers.SerializerMethodField()
    isHeadline = serializers.BooleanField(source='is_headline', read_only=True)
    publishedAt = serializers.DateTimeField(source='published_at', read_only=True)

    class Meta:
        model = Article
        fields = [
            'id',
            'title',
            'slug',
            'category',
            'headlineTag',
            'summary',
            'body',
            'reference',
            'referenceName',
            'date',
            'readTime',
            'image',
            'documentUrl',
            'isHeadline',
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

