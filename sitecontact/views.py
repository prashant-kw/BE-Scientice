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
        info = SiteInfo.get_solo()
        serializer = SiteInfoSerializer(info)
        return Response(serializer.data)

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
