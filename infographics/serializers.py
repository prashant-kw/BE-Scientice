from rest_framework import serializers
from common.utils import build_absolute_media_url
from .models import Infographic, InfographicPoint

class InfographicPointSerializer(serializers.ModelSerializer):
    num = serializers.SerializerMethodField()
    desc = serializers.CharField(source='description')

    class Meta:
        model = InfographicPoint
        fields = ['num', 'title', 'desc']

    def get_num(self, obj):
        return str(obj.order)

class InfographicSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    documentUrl = serializers.SerializerMethodField()
    referenceUrl = serializers.CharField(source='reference_url', read_only=True)
    points = InfographicPointSerializer(many=True, read_only=True)

    class Meta:
        model = Infographic
        fields = [
            'id',
            'tag',
            'title',
            'subtitle',
            'image',
            'documentUrl',
            'category',
            'reference',
            'referenceUrl',
            'quote',
            'alert',
            'points',
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

