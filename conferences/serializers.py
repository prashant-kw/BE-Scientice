from rest_framework import serializers
from common.utils import build_absolute_media_url
from .models import Conference, ConferenceRegistration

class ConferenceSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category_display', read_only=True)
    date = serializers.CharField(source='formatted_date', read_only=True)
    startDate = serializers.DateField(source='start_date', read_only=True)
    endDate = serializers.DateField(source='end_date', read_only=True)
    isVirtualAvailable = serializers.BooleanField(source='is_virtual_available', read_only=True)
    cmeCredits = serializers.IntegerField(source='cme_credits', read_only=True)
    image = serializers.SerializerMethodField()
    documentUrl = serializers.SerializerMethodField()

    class Meta:
        model = Conference
        fields = [
            'id',
            'title',
            'slug',
            'description',
            'agenda',
            'category',
            'date',
            'startDate',
            'endDate',
            'location',
            'isVirtualAvailable',
            'cmeCredits',
            'image',
            'documentUrl',
            'created_at',
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


class ConferenceRegistrationSerializer(serializers.ModelSerializer):
    conferenceTitle = serializers.CharField(source='conference.title', read_only=True)
    fullName = serializers.CharField(source='full_name', required=False)
    name = serializers.CharField(source='full_name', required=False)
    attendanceMode = serializers.CharField(source='attendance_mode', required=False)
    registeredAt = serializers.DateTimeField(source='registered_at', read_only=True)

    class Meta:
        model = ConferenceRegistration
        fields = [
            'id',
            'conference',
            'conferenceTitle',
            'fullName',
            'name',
            'email',
            'attendanceMode',
            'organization',
            'registeredAt',
        ]
        read_only_fields = ['id', 'conference', 'registeredAt', 'conferenceTitle']

    def validate(self, attrs):
        # Support either fullName, name, or full_name
        full_name = attrs.get('full_name') or self.initial_data.get('fullName') or self.initial_data.get('name')
        if not full_name:
            raise serializers.ValidationError({'fullName': 'Full name is required.'})
        attrs['full_name'] = full_name

        mode = attrs.get('attendance_mode') or self.initial_data.get('attendanceMode') or 'virtual'
        # Normalize in-person / in_person
        if mode in ['in-person', 'in_person', 'inPerson']:
            attrs['attendance_mode'] = ConferenceRegistration.Mode.IN_PERSON
        else:
            attrs['attendance_mode'] = ConferenceRegistration.Mode.VIRTUAL

        return attrs
