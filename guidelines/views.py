from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Guideline, ConferenceSociety
from .serializers import GuidelineSerializer, ConferenceSocietySerializer

DEFAULT_SOCIETIES = [
    {"code": "AAIC", "name": "Alzheimer's Association International Conference", "order": 1},
    {"code": "ACC", "name": "American College of Cardiology", "order": 2},
    {"code": "ACOG", "name": "American College of Obstetricians and Gynecologists", "order": 3},
    {"code": "ADA", "name": "American Diabetes Association", "order": 4},
    {"code": "AHA", "name": "American Heart Association", "order": 5},
    {"code": "AOS", "name": "American Orthopaedic Society", "order": 6},
    {"code": "ASN", "name": "American Society of Nephrology", "order": 7},
    {"code": "EASD", "name": "European Association for the Study of Diabetes", "order": 8},
    {"code": "ESC", "name": "European Society of Cardiology", "order": 9},
    {"code": "ESHRE", "name": "European Society of Human Reproduction and Embryology", "order": 10},
    {"code": "EFFORT", "name": "European Federation of National Associations of Orthopaedics and Traumatology", "order": 11},
    {"code": "EAU", "name": "European Association of Urology", "order": 12},
]

DEFAULT_CONFERENCE_GUIDELINES = [
    {
        "title": "2026 ESC Guidelines for the Management of Chronic Coronary Syndromes",
        "authority": "ESC",
        "guideline_type": "conference",
        "society_code": "ESC",
        "summary": "Evidence-based European Society of Cardiology recommendations on invasive physiology, intravascular imaging, and targeted anti-anginal and lipid-lowering medical strategies.",
        "category_name_override": "Cardiology",
    },
    {
        "title": "2026 ACC/AHA Key Consensus Algorithm on Heart Failure with Preserved Ejection Fraction",
        "authority": "ACC",
        "guideline_type": "conference",
        "society_code": "ACC",
        "summary": "Comprehensive clinical algorithm from ACC/AHA covering SGLT2 inhibitors, GLP-1 receptor agonists, and modern hemodynamic monitoring for HFpEF.",
        "category_name_override": "Cardiology",
    },
    {
        "title": "2026 ADA Standards of Care in Diabetes: Glycemic Targets & Renal Protection",
        "authority": "ADA",
        "guideline_type": "conference",
        "society_code": "ADA",
        "summary": "American Diabetes Association practice standards emphasizing cardio-renal protection, continuous glucose monitoring (CGM), and individualized pharmacotherapy.",
        "category_name_override": "Endocrinology",
    },
    {
        "title": "AAIC Consensus Criteria for Early Biomarker Screening in Alzheimer's Disease",
        "authority": "AAIC",
        "guideline_type": "conference",
        "society_code": "AAIC",
        "summary": "International diagnostic recommendations on blood-based biomarkers, amyloid PET imaging, and anti-amyloid monoclonal antibody therapy in early cognitive decline.",
        "category_name_override": "Neurology",
    },
    {
        "title": "AHA Scientific Statement on Primary Stroke Prevention & Lipid Management",
        "authority": "AHA",
        "guideline_type": "conference",
        "society_code": "AHA",
        "summary": "American Heart Association guidelines on intensive statin therapy, PCSK9 inhibitors, and lifestyle interventions to mitigate primary cerebrovascular events.",
        "category_name_override": "Cardiology",
    },
    {
        "title": "EASD Clinical Recommendations on Incretin Therapies in Metabolic Syndrome",
        "authority": "EASD",
        "guideline_type": "conference",
        "society_code": "EASD",
        "summary": "European Association for the Study of Diabetes recommendations on dual and triple incretin receptor agonists in obesity and type 2 diabetes.",
        "category_name_override": "Endocrinology",
    },
]

DEFAULT_CLINICAL_PRACTICE_GUIDELINES = [
    {
        "title": "Standard Treatment Guidelines: Severe Asthma & COPD Exacerbations",
        "authority": "Pulmonary Care Board",
        "guideline_type": "clinical_practice",
        "summary": "Comprehensive biologic phenotyping protocols, triple inhaled therapy algorithms, and acute non-invasive ventilation (NIV) indications in respiratory failure.",
        "category_name_override": "Pulmonology",
    },
    {
        "title": "Clinical Practice Guidelines: Multidisciplinary Management of Acute Kidney Injury",
        "authority": "National Nephrology Board",
        "guideline_type": "clinical_practice",
        "summary": "Clinical protocol for early biomarker recognition, renal replacement therapy timing, and fluid balance optimization in hospital intensive care.",
        "category_name_override": "Nephrology",
    },
    {
        "title": "Hospital Diagnostic & Treatment Protocol: Sepsis & Septic Shock in Critical Care",
        "authority": "Intensive Care Society",
        "guideline_type": "clinical_practice",
        "summary": "Standardized one-hour sepsis bundle, broad-spectrum antibiotic stewardship, and vasopressor titration protocols.",
        "category_name_override": "Critical Care",
    },
]

class GuidelineViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing clinical practice and conference guidelines.
    Supports filtering by type (conference vs clinical_practice), society, and search.
    """
    serializer_class = GuidelineSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'authority', 'summary', 'category_name_override', 'society__code', 'society__name']
    ordering_fields = ['published_at', 'title', 'authority']
    ordering = ['-published_at']

    def get_queryset(self):
        try:
            if not Guideline.objects.exists():
                for item in DEFAULT_CONFERENCE_GUIDELINES:
                    soc = ConferenceSociety.objects.filter(code=item.get("society_code")).first()
                    Guideline.objects.get_or_create(
                        title=item["title"],
                        defaults={
                            "authority": item["authority"],
                            "guideline_type": item["guideline_type"],
                            "society": soc,
                            "summary": item["summary"],
                            "category_name_override": item["category_name_override"],
                            "is_published": True,
                        }
                    )
                for item in DEFAULT_CLINICAL_PRACTICE_GUIDELINES:
                    Guideline.objects.get_or_create(
                        title=item["title"],
                        defaults={
                            "authority": item["authority"],
                            "guideline_type": item["guideline_type"],
                            "summary": item["summary"],
                            "category_name_override": item["category_name_override"],
                            "is_published": True,
                        }
                    )
        except Exception:
            pass

        qs = Guideline.objects.filter(
            Q(is_published=True) &
            (Q(category__isnull=True) | Q(category__is_active=True)) &
            (Q(society__isnull=True) | Q(society__is_active=True))
        ).select_related('category', 'society')

        # Type filter ('conference' vs 'clinical_practice')
        type_param = self.request.query_params.get('type') or self.request.query_params.get('guideline_type')
        if type_param == 'conference':
            society_codes = [s['code'] for s in DEFAULT_SOCIETIES]
            qs = qs.filter(Q(guideline_type='conference') | Q(society__isnull=False) | Q(authority__in=society_codes))
        elif type_param == 'clinical_practice':
            qs = qs.filter(guideline_type='clinical_practice')

        # Society filter
        society_param = self.request.query_params.get('society') or self.request.query_params.get('authority')
        if society_param:
            clean_soc = society_param.replace(' Guidelines', '').strip()
            qs = qs.filter(Q(society__code__iexact=clean_soc) | Q(authority__icontains=clean_soc))

        therapy_param = self.request.query_params.get('therapy_area') or self.request.query_params.get('category')
        if therapy_param:
            clean_param = therapy_param.replace(' Conferences', '').replace(' Specialties', '').replace(' Guidelines', '').strip()
            qs = qs.filter(
                Q(category__name__icontains=clean_param) |
                Q(category__slug__iexact=clean_param) |
                Q(category_name_override__icontains=clean_param) |
                Q(authority__icontains=clean_param) |
                Q(society__code__iexact=clean_param)
            )

        return qs


class ConferenceSocietyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public read-only API endpoint for active Conference Guideline Societies / Issuers.
    """
    serializer_class = ConferenceSocietySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        try:
            if not ConferenceSociety.objects.exists():
                for item in DEFAULT_SOCIETIES:
                    ConferenceSociety.objects.get_or_create(
                        code=item["code"],
                        defaults={"name": item["name"], "order": item["order"], "is_active": True}
                    )
            return ConferenceSociety.objects.filter(is_active=True).order_by('order', 'code')
        except Exception:
            return ConferenceSociety.objects.none()


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.http import HttpResponse, StreamingHttpResponse
import urllib.request


@api_view(['GET'])
@permission_classes([AllowAny])
def proxy_pdf_view(request):
    """
    Proxies remote/S3 PDF files through the backend to circumvent browser CORS restrictions.
    """
    target_url = request.GET.get('url', '').strip()
    if not target_url:
        return HttpResponse('Missing url parameter', status=400)

    if not (target_url.startswith('http://') or target_url.startswith('https://')):
        return HttpResponse('Invalid URL protocol', status=400)

    try:
        req = urllib.request.Request(
            target_url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        remote_file = urllib.request.urlopen(req, timeout=40)

        def file_iterator(file_obj, chunk_size=32768):
            while True:
                chunk = file_obj.read(chunk_size)
                if not chunk:
                    break
                yield chunk
            file_obj.close()

        response = StreamingHttpResponse(
            file_iterator(remote_file),
            content_type='application/pdf',
            status=200
        )
        response['Content-Disposition'] = 'inline; filename="document.pdf"'
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Range, Authorization, Content-Type'
        response['Access-Control-Expose-Headers'] = 'Content-Length, Content-Range, Accept-Ranges'
        return response
    except Exception as exc:
        return HttpResponse(f'Error proxying PDF: {str(exc)}', status=502)


