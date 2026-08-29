from rest_framework import serializers
from .models import SiteInfo, ContactMessage

class SiteInfoSerializer(serializers.ModelSerializer):
    facebookUrl = serializers.SerializerMethodField()
    instagramUrl = serializers.SerializerMethodField()
    websiteUrl = serializers.SerializerMethodField()
    showHeroBanner = serializers.SerializerMethodField()
    showGuidelinesShowcase = serializers.SerializerMethodField()
    showHeadlineSlider = serializers.SerializerMethodField()
    showNewsWidget = serializers.SerializerMethodField()
    showTherapyAreasWidget = serializers.SerializerMethodField()
    showConferencesWidget = serializers.SerializerMethodField()
    showEducationWidget = serializers.SerializerMethodField()
    showGuidelinesWidget = serializers.SerializerMethodField()

    def get_facebookUrl(self, obj):
        return getattr(obj, 'facebook_url', 'https://facebook.com/scientice') or ''

    def get_instagramUrl(self, obj):
        return getattr(obj, 'instagram_url', 'https://instagram.com/scientice') or ''

    def get_websiteUrl(self, obj):
        return getattr(obj, 'website_url', 'https://scientice.org') or ''

    def get_showHeroBanner(self, obj):
        return getattr(obj, 'show_hero_banner', True)

    def get_showGuidelinesShowcase(self, obj):
        return getattr(obj, 'show_guidelines_showcase', True)

    def get_showHeadlineSlider(self, obj):
        return getattr(obj, 'show_headline_slider', True)

    def get_showNewsWidget(self, obj):
        return getattr(obj, 'show_news_widget', True)

    def get_showTherapyAreasWidget(self, obj):
        return getattr(obj, 'show_therapy_areas_widget', True)

    def get_showConferencesWidget(self, obj):
        return getattr(obj, 'show_conferences_widget', True)

    def get_showEducationWidget(self, obj):
        return getattr(obj, 'show_education_widget', False)

    def get_showGuidelinesWidget(self, obj):
        return getattr(obj, 'show_guidelines_widget', True)

    class Meta:
        model = SiteInfo
        fields = [
            'phone', 'email', 'address', 'facebookUrl', 'instagramUrl', 'websiteUrl',
            'showHeroBanner', 'showGuidelinesShowcase', 'showHeadlineSlider',
            'showNewsWidget', 'showTherapyAreasWidget', 'showConferencesWidget',
            'showEducationWidget', 'showGuidelinesWidget',
            'show_after_event_guidelines', 'after_event_guidelines_badge_text', 'after_event_guidelines_list'
        ]

class ContactMessageSerializer(serializers.ModelSerializer):
    isRead = serializers.BooleanField(source='is_read', read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = ContactMessage
        fields = ['id', 'name', 'email', 'subject', 'message', 'isRead', 'createdAt']
        read_only_fields = ['id', 'isRead', 'createdAt']
