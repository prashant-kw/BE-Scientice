from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import TherapyArea
from .serializers import TherapyAreaSerializer, TherapyAreaDetailSerializer

class TherapyAreaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for listing and retrieving Therapy Areas / Medical Specialties.
    Supports filtering and search by name.
    """
    queryset = TherapyArea.objects.filter(is_active=True).order_by('order', 'name')
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['order', 'name']
    lookup_field = 'slug'
    pagination_class = None  # Return all therapy areas for widgets & dropdown menus

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TherapyAreaDetailSerializer
        return TherapyAreaSerializer

    def get_object(self):
        # Support lookup by slug or by primary key ID
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup_value = self.kwargs[lookup_url_kwarg]
        if str(lookup_value).isdigit():
            return TherapyArea.objects.get(id=int(lookup_value))
        return super().get_object()
