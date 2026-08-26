from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import EducationCategory, EducationResource
from .serializers import EducationCategorySerializer, EducationResourceSerializer

DEFAULT_CATEGORIES = [
    {
        "key": EducationCategory.Key.PATIENT,
        "title": "Patient Education",
        "description": "Patient health awareness, prevention booklets, and lifestyle management guides.",
        "icon": "Users",
        "order": 1,
    },
    {
        "key": EducationCategory.Key.MEDICAL,
        "title": "Medical Education",
        "description": "Physician clinical case series, diagnostic modules, and specialist learning decks.",
        "icon": "GraduationCap",
        "order": 2,
    },
    {
        "key": EducationCategory.Key.CME,
        "title": "CME & Guidelines",
        "description": "Continuing medical education literature, clinical algorithms, and practice protocols.",
        "icon": "FileCheck",
        "order": 3,
    },
]

def ensure_default_education_data():
    try:
        for c in DEFAULT_CATEGORIES:
            cat, _ = EducationCategory.objects.get_or_create(
                key=c["key"],
                defaults={
                    "title": c["title"],
                    "description": c["description"],
                    "icon": c["icon"],
                    "order": c["order"],
                }
            )

        if not EducationResource.objects.exists():
            p_cat = EducationCategory.objects.filter(key=EducationCategory.Key.PATIENT).first()
            m_cat = EducationCategory.objects.filter(key=EducationCategory.Key.MEDICAL).first()
            c_cat = EducationCategory.objects.filter(key=EducationCategory.Key.CME).first()

            if p_cat:
                EducationResource.objects.get_or_create(
                    title="Patient Awareness Handbook: Comprehensive Diabetes & Cardiovascular Health",
                    defaults={
                        "category": p_cat,
                        "description": "Step-by-step patient guidance on glycemic management, blood pressure monitoring, and heart-healthy lifestyle interventions.",
                        "body": "<p>This comprehensive patient education handbook covers essential self-management strategies for individuals with type 2 diabetes and hypertension.</p>",
                        "is_published": True,
                    }
                )
            if m_cat:
                EducationResource.objects.get_or_create(
                    title="Clinical Specialist Module: Advanced Echocardiography & Hemodynamic Assessment",
                    defaults={
                        "category": m_cat,
                        "description": "Physician educational booklet on Doppler assessment, strain imaging protocols, and diastolic dysfunction evaluation.",
                        "body": "<p>A high-yield clinical booklet designed for cardiology fellows and practicing clinicians.</p>",
                        "is_published": True,
                    }
                )
            if c_cat:
                EducationResource.objects.get_or_create(
                    title="CME Clinical Review: Early Multi-Targeted Pharmacotherapy in Metabolic Disease",
                    defaults={
                        "category": c_cat,
                        "description": "Accredited medical learning guide on dual incretin therapies, SGLT2 inhibition, and renal preservation algorithms.",
                        "body": "<p>Structured clinical training module reviewing evidence-based pharmacology.</p>",
                        "is_published": True,
                    }
                )
    except Exception:
        pass

class EducationCategoryListView(generics.ListAPIView):
    """
    List all high-level education categories.
    """
    serializer_class = EducationCategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        ensure_default_education_data()
        return EducationCategory.objects.all().order_by('order', 'id')


class PatientEducationListView(generics.ListAPIView):
    """
    List patient education resources.
    """
    serializer_class = EducationResourceSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title', 'description', 'body']

    def get_queryset(self):
        ensure_default_education_data()
        return EducationResource.objects.filter(
            category__key=EducationCategory.Key.PATIENT,
            is_published=True
        ).select_related('category').order_by('-published_at')

class MedicalEducationListView(generics.ListAPIView):
    """
    List healthcare professional / medical education resources.
    """
    serializer_class = EducationResourceSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title', 'description', 'body']

    def get_queryset(self):
        return EducationResource.objects.filter(
            category__key=EducationCategory.Key.MEDICAL,
            is_published=True
        ).select_related('category').order_by('-published_at')

class CMEEducationListView(generics.ListAPIView):
    """
    List continuing medical education (CME) resources and courseware.
    """
    serializer_class = EducationResourceSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title', 'description', 'body']

    def get_queryset(self):
        return EducationResource.objects.filter(
            category__key=EducationCategory.Key.CME,
            is_published=True
        ).select_related('category').order_by('-published_at')

class EducationResourceDetailView(generics.RetrieveAPIView):
    """
    Retrieve single education resource.
    """
    queryset = EducationResource.objects.filter(is_published=True).select_related('category')
    serializer_class = EducationResourceSerializer
    permission_classes = [permissions.AllowAny]
