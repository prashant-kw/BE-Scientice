from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q
from drf_spectacular.utils import extend_schema
from common.throttling import ConferenceRegistrationRateThrottle
from .models import Conference, ConferenceRegistration
from .serializers import ConferenceSerializer, ConferenceRegistrationSerializer

class ConferenceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing upcoming medical conferences and registering attendees.
    """
    serializer_class = ConferenceSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'location', 'category_name_override']
    ordering_fields = ['start_date', 'title']
    ordering = ['start_date']

    def get_queryset(self):
        qs = Conference.objects.filter(is_published=True).select_related('category')

        therapy_param = self.request.query_params.get('therapy_area') or self.request.query_params.get('category')
        if therapy_param:
            clean_param = therapy_param.replace(' Conferences', '').replace(' Specialties', '').strip()
            qs = qs.filter(
                Q(category__name__icontains=clean_param) |
                Q(category__slug__iexact=clean_param) |
                Q(category_name_override__icontains=clean_param)
            )

        return qs

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """
        List conferences starting today or in the future.
        """
        today = timezone.now().date()
        qs = self.get_queryset().filter(end_date__gte=today).order_by('start_date')
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=ConferenceRegistrationSerializer,
        responses={201: ConferenceRegistrationSerializer},
        description="Register an attendee for this conference"
    )
    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.AllowAny],
        throttle_classes=[ConferenceRegistrationRateThrottle]
    )
    def register(self, request, pk=None):
        """
        Submit a conference registration / RSVP.
        """
        conference = self.get_object()
        serializer = ConferenceRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user if request.user.is_authenticated else None
            registration = serializer.save(conference=conference, user=user)
            return Response(
                ConferenceRegistrationSerializer(registration).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
