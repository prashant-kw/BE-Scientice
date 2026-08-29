from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from common.throttling import ContactSubmissionRateThrottle
from .models import SiteInfo, ContactMessage
from .serializers import SiteInfoSerializer, ContactMessageSerializer

class SiteInfoView(APIView):
    """
    Public endpoint retrieving Scientice portal contact details & social links.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        responses={200: SiteInfoSerializer},
        description="Retrieve site contact information and social profiles"
    )
    def get(self, request):
        try:
            info = SiteInfo.get_solo()
            data = SiteInfoSerializer(info).data

            # Dynamically compute content availability and section flags
            try:
                from cms.views import get_section_live_counts
                from cms.models import ContentSectionVisibility

                ContentSectionVisibility.ensure_defaults()
                sections = ContentSectionVisibility.objects.all()
                section_map = {}
                for sec in sections:
                    pub_count, _ = get_section_live_counts(sec.section_key)
                    is_vis = bool(sec.is_enabled and (not sec.auto_hide_if_empty or pub_count > 0))
                    section_map[sec.section_key] = {
                        'isEnabled': sec.is_enabled,
                        'publishedCount': pub_count,
                        'isVisible': is_vis,
                        'title': sec.title,
                    }

                if 'hero_banner' in section_map:
                    data['showHeroBanner'] = section_map['hero_banner']['isVisible']
                if 'guidelines_showcase' in section_map:
                    data['showGuidelinesShowcase'] = section_map['guidelines_showcase']['isVisible']
                if 'headline_slider' in section_map:
                    data['showHeadlineSlider'] = section_map['headline_slider']['isVisible']
                if 'news_articles' in section_map:
                    data['showNewsWidget'] = section_map['news_articles']['isVisible']
                if 'therapy_areas' in section_map:
                    data['showTherapyAreasWidget'] = section_map['therapy_areas']['isVisible']
                if 'conferences' in section_map:
                    data['showConferencesWidget'] = section_map['conferences']['isVisible']
                if 'education' in section_map:
                    data['showEducationWidget'] = section_map['education']['isVisible']
                if 'guidelines_widget' in section_map:
                    data['showGuidelinesWidget'] = section_map['guidelines_widget']['isVisible']

                data['sectionVisibility'] = section_map
            except Exception as inner_err:
                print(f"Error computing dynamic section visibility: {inner_err}")

            return Response(data)
        except Exception:
            return Response({
                'phone': '+1 (800) 555-0199',
                'email': 'contact@scientice.org',
                'address': 'Scientice Medical Institute, 500 Healthcare Blvd, Suite 400, Boston, MA 02115',
                'facebookUrl': 'https://facebook.com/scientice',
                'instagramUrl': 'https://instagram.com/scientice',
                'websiteUrl': 'https://scientice.org',
                'showHeroBanner': True,
                'showGuidelinesShowcase': True,
                'showHeadlineSlider': True,
                'showNewsWidget': True,
                'showTherapyAreasWidget': True,
                'showConferencesWidget': True,
                'showEducationWidget': False,
                'showGuidelinesWidget': True,
                'show_after_event_guidelines': False,
                'after_event_guidelines_badge_text': 'New',
                'after_event_guidelines_list': [],
            })

class ContactMessageCreateView(generics.CreateAPIView):
    """
    Public endpoint for visitors to submit questions or editorial inquiries.
    Throttled to 10 requests / hour / IP to prevent bot spam.
    """
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ContactSubmissionRateThrottle]

    @extend_schema(
        request=ContactMessageSerializer,
        responses={201: ContactMessageSerializer},
        description="Submit an inbound contact inquiry"
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(
                {
                    'message': 'Thank you for reaching out! Our medical editorial team will get back to you shortly.',
                    'data': serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
