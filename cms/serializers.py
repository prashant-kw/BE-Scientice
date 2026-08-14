from django.db import transaction
from rest_framework import serializers

from common.utils import build_absolute_media_url
from accounts.models import User
from news.models import Article
from guidelines.models import Guideline
from conferences.models import Conference, ConferenceRegistration
from education.models import EducationResource, EducationCategory
from infographics.models import Infographic, InfographicPoint
from therapyareas.models import TherapyArea
from sitecontact.models import SiteInfo, ContactMessage

from .sanitizers import sanitize_html, sanitize_plain_text
from .validators import validate_and_clean_image, validate_and_clean_pdf

# ----------------------------------------------------------------------
# 1. Article CMS Serializer
# ----------------------------------------------------------------------
class ArticleCMSSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(read_only=True)
    image_display_url = serializers.SerializerMethodField()
    effective_document_url = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'summary', 'body',
            'category', 'category_display', 'category_name_override',
            'image', 'image_url', 'image_display_url',
            'reference_url', 'reference_name',
            'document_url', 'document_file', 'effective_document_url',
            'headline_tag', 'is_headline', 'is_published',
            'read_time_minutes', 'published_at',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_image_display_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return build_absolute_media_url(request, obj.image)
        return build_absolute_media_url(request, obj.image_url)

    def get_effective_document_url(self, obj):
        request = self.context.get('request')
        if obj.document_file:
            return build_absolute_media_url(request, obj.document_file)
        return build_absolute_media_url(request, obj.document_url)

    def validate_title(self, value):
        return sanitize_plain_text(value)

    def validate_summary(self, value):
        return sanitize_plain_text(value)

    def validate_body(self, value):
        return sanitize_html(value)

    def validate_image(self, value):
        return validate_and_clean_image(value)

    def validate_document_file(self, value):
        return validate_and_clean_pdf(value)

# ----------------------------------------------------------------------
# 2. Guideline CMS Serializer
# ----------------------------------------------------------------------
class GuidelineCMSSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(read_only=True)
    image_display_url = serializers.SerializerMethodField()
    effective_document_url = serializers.SerializerMethodField()

    class Meta:
        model = Guideline
        fields = [
            'id', 'title', 'authority',
            'category', 'category_display', 'category_name_override',
            'summary', 'image', 'image_url', 'image_display_url',
            'document_url', 'document_file', 'effective_document_url',
            'is_published', 'published_at',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_image_display_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return build_absolute_media_url(request, obj.image)
        return build_absolute_media_url(request, obj.image_url)

    def get_effective_document_url(self, obj):
        request = self.context.get('request')
        if obj.document_file:
            return build_absolute_media_url(request, obj.document_file)
        return build_absolute_media_url(request, obj.document_url)

    def validate_title(self, value):
        return sanitize_plain_text(value)

    def validate_authority(self, value):
        return sanitize_plain_text(value)

    def validate_summary(self, value):
        return sanitize_html(value)

    def validate_image(self, value):
        return validate_and_clean_image(value)

    def validate_document_file(self, value):
        return validate_and_clean_pdf(value)

# ----------------------------------------------------------------------
# 3. Conference CMS Serializer & Registration Serializer
# ----------------------------------------------------------------------
class ConferenceCMSSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(read_only=True)
    image_display_url = serializers.SerializerMethodField()
    effective_document_url = serializers.SerializerMethodField()
    registrations_count = serializers.IntegerField(source='registrations.count', read_only=True)

    class Meta:
        model = Conference
        fields = [
            'id', 'title', 'slug', 'description', 'agenda',
            'category', 'category_display', 'category_name_override',
            'start_date', 'end_date', 'location',
            'is_virtual_available', 'cme_credits',
            'image', 'image_url', 'image_display_url',
            'document_url', 'document_file', 'effective_document_url',
            'is_published', 'registrations_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'registrations_count']

    def get_image_display_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return build_absolute_media_url(request, obj.image)
        return build_absolute_media_url(request, obj.image_url)

    def get_effective_document_url(self, obj):
        request = self.context.get('request')
        if obj.document_file:
            return build_absolute_media_url(request, obj.document_file)
        return build_absolute_media_url(request, obj.document_url)

    def validate_title(self, value):
        return sanitize_plain_text(value)

    def validate_description(self, value):
        return sanitize_html(value)

    def validate_agenda(self, value):
        if value is None:
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError("Agenda must be a JSON array / list of topics.")
        
        clean_agenda = []
        for item in value:
            if isinstance(item, str):
                cleaned = sanitize_plain_text(item)
                if cleaned:
                    clean_agenda.append(cleaned)
            elif isinstance(item, dict):
                clean_item = {}
                for k, v in item.items():
                    if isinstance(v, str):
                        clean_item[k] = sanitize_plain_text(v)
                    else:
                        clean_item[k] = v
                clean_agenda.append(clean_item)
            else:
                clean_agenda.append(str(item))
        return clean_agenda

    def validate_image(self, value):
        return validate_and_clean_image(value)

    def validate_document_file(self, value):
        return validate_and_clean_pdf(value)

class ConferenceRegistrationCMSListSerializer(serializers.ModelSerializer):
    conference_title = serializers.CharField(source='conference.title', read_only=True)
    attendance_mode_display = serializers.CharField(source='get_attendance_mode_display', read_only=True)

    class Meta:
        model = ConferenceRegistration
        fields = [
            'id', 'conference', 'conference_title',
            'full_name', 'email', 'attendance_mode', 'attendance_mode_display',
            'organization', 'registered_at',
        ]
        read_only_fields = [
            'id', 'conference', 'conference_title',
            'full_name', 'email', 'attendance_mode', 'attendance_mode_display',
            'organization', 'registered_at',
        ]

# ----------------------------------------------------------------------
# 4. Education Resource CMS Serializer
# ----------------------------------------------------------------------
class EducationResourceCMSSerializer(serializers.ModelSerializer):
    category_title = serializers.CharField(source='category.title', read_only=True)
    category_key = serializers.CharField(source='category.key', read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = EducationResource
        fields = [
            'id', 'category', 'category_title', 'category_key',
            'title', 'description', 'body', 'icon',
            'file', 'file_url', 'external_url',
            'is_published', 'published_at',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file:
            return build_absolute_media_url(request, obj.file)
        return ''

    def validate_title(self, value):
        return sanitize_plain_text(value)

    def validate_description(self, value):
        return sanitize_plain_text(value)

    def validate_body(self, value):
        return sanitize_html(value)

    def validate_file(self, value):
        return validate_and_clean_pdf(value)

# ----------------------------------------------------------------------
# 5. Infographic & Points CMS Serializers (Atomic Nested Points)
# ----------------------------------------------------------------------
class InfographicPointCMSSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = InfographicPoint
        fields = ['id', 'order', 'title', 'description']

    def validate_title(self, value):
        return sanitize_plain_text(value)

    def validate_description(self, value):
        return sanitize_plain_text(value)

class InfographicCMSSerializer(serializers.ModelSerializer):
    image_display_url = serializers.SerializerMethodField()
    effective_document_url = serializers.SerializerMethodField()
    points = InfographicPointCMSSerializer(many=True, required=False)

    class Meta:
        model = Infographic
        fields = [
            'id', 'title', 'tag', 'subtitle', 'category',
            'image', 'image_url', 'image_display_url',
            'reference', 'reference_url',
            'document_url', 'document_file', 'effective_document_url',
            'quote', 'alert',
            'is_published', 'published_at',
            'created_at', 'updated_at',
            'points',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_image_display_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return build_absolute_media_url(request, obj.image)
        return build_absolute_media_url(request, obj.image_url)

    def get_effective_document_url(self, obj):
        request = self.context.get('request')
        if obj.document_file:
            return build_absolute_media_url(request, obj.document_file)
        return build_absolute_media_url(request, obj.document_url)


    def validate_title(self, value):
        return sanitize_plain_text(value)

    def validate_subtitle(self, value):
        return sanitize_plain_text(value)

    def validate_quote(self, value):
        return sanitize_plain_text(value)

    def validate_alert(self, value):
        return sanitize_plain_text(value)

    def validate_image(self, value):
        return validate_and_clean_image(value)

    def validate_document_file(self, value):
        return validate_and_clean_pdf(value)

    @transaction.atomic
    def create(self, validated_data):
        points_data = validated_data.pop('points', [])
        infographic = Infographic.objects.create(**validated_data)
        for idx, point_data in enumerate(points_data, start=1):
            InfographicPoint.objects.create(
                infographic=infographic,
                order=point_data.get('order', idx),
                title=point_data.get('title', ''),
                description=point_data.get('description', '')
            )
        return infographic

    @transaction.atomic
    def update(self, instance, validated_data):
        points_data = validated_data.pop('points', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if points_data is not None:
            # Replace points atomically for this specific infographic
            instance.points.all().delete()
            for idx, point_data in enumerate(points_data, start=1):
                InfographicPoint.objects.create(
                    infographic=instance,
                    order=point_data.get('order', idx),
                    title=point_data.get('title', ''),
                    description=point_data.get('description', '')
                )
        return instance

# ----------------------------------------------------------------------
# 6. Therapy Area CMS Serializer
# ----------------------------------------------------------------------
class TherapyAreaCMSSerializer(serializers.ModelSerializer):
    icon_name = serializers.CharField(source='icon', required=False, allow_blank=True)

    class Meta:
        model = TherapyArea
        fields = ['id', 'name', 'slug', 'icon', 'icon_name', 'description', 'order', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        return sanitize_plain_text(value)

    def validate_description(self, value):
        return sanitize_plain_text(value)

# ----------------------------------------------------------------------
# 7. SiteInfo CMS Serializer (Singleton)
# ----------------------------------------------------------------------
class SiteInfoCMSSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteInfo
        fields = ['id', 'phone', 'email', 'address', 'facebook_url', 'instagram_url', 'website_url', 'updated_at']
        read_only_fields = ['id', 'updated_at']

    def validate_phone(self, value):
        return sanitize_plain_text(value)

    def validate_address(self, value):
        return sanitize_plain_text(value)

# ----------------------------------------------------------------------
# 8. ContactMessage CMS Serializer (Read-Only + PATCH is_read)
# ----------------------------------------------------------------------
class ContactMessageCMSReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['id', 'name', 'email', 'subject', 'message', 'is_read', 'created_at']
        read_only_fields = ['id', 'name', 'email', 'subject', 'message', 'created_at']

# ----------------------------------------------------------------------
# 9. User CMS Serializer (Registered Healthcare Professionals & Users)
# ----------------------------------------------------------------------
class UserCMSListSerializer(serializers.ModelSerializer):
    fullName = serializers.CharField(source='full_name', read_only=True)
    licenseNumber = serializers.CharField(source='license_number', read_only=True)
    isVerified = serializers.BooleanField(source='is_verified')
    isStaff = serializers.BooleanField(source='is_staff', read_only=True)
    isSuperuser = serializers.BooleanField(source='is_superuser', read_only=True)
    isActive = serializers.BooleanField(source='is_active')
    dateJoined = serializers.DateTimeField(source='date_joined', read_only=True)
    lastLogin = serializers.DateTimeField(source='last_login', read_only=True)
    roleDisplay = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'fullName',
            'role',
            'roleDisplay',
            'specialty',
            'licenseNumber',
            'city',
            'state',
            'isVerified',
            'isStaff',
            'isSuperuser',
            'isActive',
            'dateJoined',
            'lastLogin',
        ]
        read_only_fields = ['id', 'email', 'fullName', 'role', 'roleDisplay', 'specialty', 'licenseNumber', 'city', 'state', 'dateJoined', 'lastLogin', 'isStaff', 'isSuperuser']

# ----------------------------------------------------------------------
# 10. Page CMS Serializer
# ----------------------------------------------------------------------
from .models import Page

class PageCMSSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ['id', 'title', 'slug', 'content', 'is_published', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_title(self, value):
        return sanitize_plain_text(value)

    def validate_slug(self, value):
        return sanitize_plain_text(value)

    def validate_content(self, value):
        return sanitize_html(value)

class PagePublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ['title', 'slug', 'content', 'updated_at']
