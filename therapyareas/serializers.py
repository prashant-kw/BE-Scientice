from rest_framework import serializers
from .models import TherapyArea

class TherapyAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TherapyArea
        fields = ['id', 'name', 'slug', 'icon', 'description', 'order']

class TherapyAreaDetailSerializer(serializers.ModelSerializer):
    newsCount = serializers.SerializerMethodField()
    guidelinesCount = serializers.SerializerMethodField()
    conferencesCount = serializers.SerializerMethodField()

    class Meta:
        model = TherapyArea
        fields = ['id', 'name', 'slug', 'icon', 'description', 'order', 'newsCount', 'guidelinesCount', 'conferencesCount']

    def get_newsCount(self, obj):
        return getattr(obj, 'news_articles', None).filter(is_published=True).count() if hasattr(obj, 'news_articles') else 0

    def get_guidelinesCount(self, obj):
        return getattr(obj, 'guidelines', None).filter(is_published=True).count() if hasattr(obj, 'guidelines') else 0

    def get_conferencesCount(self, obj):
        return getattr(obj, 'conferences', None).filter(is_published=True).count() if hasattr(obj, 'conferences') else 0
