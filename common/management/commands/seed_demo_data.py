from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from accounts.models import User
from therapyareas.models import TherapyArea
from news.models import Article
from infographics.models import Infographic, InfographicPoint
from conferences.models import Conference
from education.models import EducationCategory, EducationResource
from guidelines.models import Guideline
from sitecontact.models import SiteInfo
from cms.models import VideoBulletin

class Command(BaseCommand):
    help = 'Seeds realistic medical and scientific demonstration data for Scientice'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting Scientice demo database seeding...'))

        # 1. Setup Roles & Content Editor Group
        editor_group, _ = Group.objects.get_or_create(name='Content Editor')
        content_apps = ['news', 'infographics', 'guidelines', 'conferences', 'education', 'therapyareas']
        content_types = ContentType.objects.filter(app_label__in=content_apps)
        editor_permissions = Permission.objects.filter(content_type__in=content_types)
        editor_group.permissions.set(editor_permissions)
        self.stdout.write(self.style.SUCCESS(f'Configured group "Content Editor" with {editor_permissions.count()} permissions.'))

        # 2. Setup Superuser and Demo Doctor
        admin_user, created = User.objects.get_or_create(
            email='admin@scientice.org',
            defaults={
                'full_name': 'Scientice Editorial Administrator',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'is_verified': True,
            }
        )
        if created:
            admin_user.set_password('Admin@12345')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created default superuser: admin@scientice.org / Admin@12345'))
        else:
            admin_user.role = User.Role.ADMIN
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()

        doctor_user, created = User.objects.get_or_create(
            email='doctor@scientice.org',
            defaults={
                'full_name': 'Dr. Ananya Sharma, MD',
                'role': User.Role.DOCTOR,
                'specialty': 'Cardiology',
                'license_number': 'MCI-884920',
                'city': 'Hyderabad',
                'state': 'Telangana',
                'is_verified': True,
            }
        )
        if created:
            doctor_user.set_password('Doctor@12345')
            doctor_user.save()
            self.stdout.write(self.style.SUCCESS('Created demo doctor: doctor@scientice.org / Doctor@12345'))

        # 3. Seed Therapy Areas
        therapy_areas_data = [
            ("Cardiology", "Heart", 1),
            ("Diabetology", "Activity", 2),
            ("Dermatology", "Sparkles", 3),
            ("Respiratory / Pulmonology", "Wind", 4),
            ("Gastroenterology", "Stethoscope", 5),
            ("Neurology", "Brain", 6),
            ("Psychiatry", "Smile", 7),
            ("Oncology", "ShieldAlert", 8),
            ("Rheumatology", "Bone", 9),
            ("Orthopedics", "Syringe", 10),
            ("Nephrology", "Droplets", 11),
            ("Urology", "CheckCircle", 12),
            ("Obstetrics & Gynaecology", "UserCheck", 13),
            ("Pediatrics", "Baby", 14),
            ("Ophthalmology", "Eye", 15),
            ("Allergy & Immunology", "ShieldCheck", 16),
            ("Infectious Diseases", "Microscope", 17),
        ]

        ta_map = {}
        for name, icon, order in therapy_areas_data:
            ta, _ = TherapyArea.objects.get_or_create(
                name=name,
                defaults={
                    'icon': icon,
                    'order': order,
                    'description': f'Clinical updates, evidence-based research, and therapeutics in {name}.'
                }
            )
            ta_map[name] = ta
        self.stdout.write(self.style.SUCCESS(f'Seeded {len(ta_map)} Therapy Areas.'))

        # 4. Seed Headline Highlights & News Articles
        articles_data = [
            {
                'title': 'PCOS Linked to Cognitive Decline and Early Brain Aging: Study Uncovers Memory and Thinking Challenges in Women Over 40',
                'category_override': 'Neurology & Endocrinology',
                'category_name': 'Neurology',
                'headline_tag': 'HEADLINE',
                'is_headline': True,
                'summary': 'A recent study by UCSF Health suggests that Polycystic Ovary Syndrome (PCOS) may be associated with lower memory and thinking skills, as well as signs of early brain aging, in women during midlife. Researchers found that women with PCOS symptoms displayed changes in brain white matter and scored lower on cognitive tests.',
                'body': '<p>A groundbreaking longitudinal cohort evaluation led by researchers at UCSF Health reveals unprecedented links between chronic Polycystic Ovary Syndrome (PCOS) manifestations and accelerated midlife cognitive attenuation.</p><p>Using high-resolution fractional anisotropy diffusion tensor MRI alongside standardized neurocognitive battery assessments across a 30-year observation period, investigators detected measurable compromises in white matter microstructural integrity.</p><h3>Key Clinical Takeaways:</h3><ul><li>Statistically significant reductions in psychomotor speed, executive function, and verbal memory retention.</li><li>Microstructural alterations concentrated in the corpus callosum and anterior thalamic radiation.</li><li>Endocrinologists and primary care physicians are urged to institute routine baseline cognitive screening and early insulin-sensitizing interventions.</li></ul>',
                'reference_name': 'Neurology Journal / UCSF Health',
                'reference_url': 'https://www.webmd.com/women/news/20240201/researchers-find-link-pcos-midlife-cognitive-decline',
                'image_url': 'https://images.unsplash.com/photo-1559757175-5700dde675bc?auto=format&fit=crop&q=80&w=800',
                'read_time_minutes': 4,
                'published_at': timezone.now() - timedelta(days=2),
            },
            {
                'title': 'Breakthrough in Heart Failure: Novel Dual-Inhibitor Regimen Demonstrates 28% Reduction in Hospital Readmissions',
                'category_override': 'Cardiology & Therapeutics',
                'category_name': 'Cardiology',
                'headline_tag': 'BREAKTHROUGH',
                'is_headline': True,
                'summary': 'Landmark clinical trial results reveal significant improvements in cardiovascular outcomes among patients with reduced ejection fraction. The dual-pathway approach significantly improves ventricular elasticity, stabilizes systolic load, and prevents recurrent acute decompensation events across all monitored age cohorts.',
                'body': '<p>In a phase III international multicenter randomized controlled trial involving 4,800 patients diagnosed with HFrEF, combination therapy with novel SGLT2i and ARNI regimens yielded extraordinary reductions in primary composite cardiovascular mortality and recurrent hospitalizations.</p><p>Echocardiographic parameters documented substantial left ventricular reverse remodeling, with mean ejection fraction recovery of +8.4% over 12 months of sustained protocol titration.</p>',
                'reference_name': 'New England Journal of Medicine (NEJM)',
                'reference_url': 'https://www.nejm.org/doi/full/10.1056/NEJMoa2308191',
                'image_url': 'https://images.unsplash.com/photo-1628348068343-c6a848d2b6dd?auto=format&fit=crop&q=80&w=800',
                'read_time_minutes': 5,
                'published_at': timezone.now() - timedelta(days=4),
            },
            {
                'title': 'Next-Generation CAR-T Cell Therapy Demonstrates Unprecedented Remission Rates in Advanced Solid Tumors',
                'category_override': 'Oncology & Precision Medicine',
                'category_name': 'Oncology',
                'headline_tag': 'ONCOLOGY',
                'is_headline': True,
                'summary': 'Pioneering multicenter trials reveal synthetic biology engineered T-cells capable of penetrating immunosuppressive microenvironments in solid malignancies. Phase II clinical data confirms durable complete response in 72% of participating cohorts with significantly reduced toxicity profiles.',
                'body': '<p>Engineered autologous T-cells equipped with dual-antigen chimeric receptors and armored with switchable cytokine secreting cassettes overcome prior solid tumor microenvironment barriers.</p><p>In patients with refractory metastatic gastrointestinal and pancreatic adenocarcinomas, radiographic objective response rates reached 84%, providing a transformative therapeutic horizon.</p>',
                'reference_name': 'Nature Medicine / International Oncology Forum',
                'reference_url': 'https://www.nature.com/articles/s41591-024-02845-x',
                'image_url': 'https://images.unsplash.com/photo-1579684385127-1ef15d508118?auto=format&fit=crop&q=80&w=800',
                'read_time_minutes': 6,
                'published_at': timezone.now() - timedelta(days=6),
            },
            {
                'title': 'Targeted IL-23 Inhibitors Establish New Benchmark for Long-Term Psoriasis Clearance and Remission',
                'category_override': 'Dermatology & Immunology',
                'category_name': 'Dermatology',
                'headline_tag': 'DERMATOLOGY',
                'is_headline': True,
                'summary': 'A comprehensive 5-year real-world registry study demonstrates sustained PASI 90/100 skin clearance with quarterly biologic maintenance dosing. Patients report significant enhancements in psychosocial indices with no evidence of cumulative systemic immunosuppression.',
                'body': '<p>Real-world evidence tracking over 3,200 moderate-to-severe plaque psoriasis patients confirms high-affinity interleukin-23 p19 subunit inhibition provides unmatched clinical durability.</p><p>Over 82% of patients maintained complete skin clearance (PASI 100) at Year 5, with negligible rates of antidrug antibody neutralization.</p>',
                'reference_name': 'The Lancet Dermatology',
                'reference_url': 'https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(24)00341-2',
                'image_url': 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&q=80&w=800',
                'read_time_minutes': 3,
                'published_at': timezone.now() - timedelta(days=8),
            },
            {
                'title': 'Breakthrough in Cardiology: New study shows promising results in heart failure treatment.',
                'category_override': '',
                'category_name': 'Cardiology',
                'headline_tag': 'NEWS',
                'is_headline': False,
                'summary': 'Cardiology clinical updates on mineralocorticoid receptor antagonists in preservation of renal and systolic performance.',
                'body': 'Recent clinical trials demonstrate protective outcomes with non-steroidal MRAs in heart failure patients.',
                'reference_name': 'European Heart Journal',
                'reference_url': 'https://academic.oup.com/eurheartj',
                'image_url': 'https://images.unsplash.com/photo-1628348068343-c6a848d2b6dd?auto=format&fit=crop&q=80&w=400',
                'read_time_minutes': 4,
                'published_at': timezone.now() - timedelta(days=1),
            },
            {
                'title': 'Dermatology Update: Latest advances in psoriasis management.',
                'category_override': '',
                'category_name': 'Dermatology',
                'headline_tag': 'NEWS',
                'is_headline': False,
                'summary': 'Topical phosphodiesterase-4 inhibitors present non-steroidal long-term options for intertriginous and sensitive facial psoriasis.',
                'body': 'Novel non-steroidal topical formulations deliver efficacy without skin atrophy risks.',
                'reference_name': 'Journal of Investigative Dermatology',
                'reference_url': 'https://www.jidonline.org',
                'image_url': 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&q=80&w=400',
                'read_time_minutes': 3,
                'published_at': timezone.now() - timedelta(days=3),
            },
            {
                'title': 'Oncology News: Immunotherapy shows improved survival rates.',
                'category_override': '',
                'category_name': 'Oncology',
                'headline_tag': 'NEWS',
                'is_headline': False,
                'summary': 'Neoadjuvant checkpoint inhibitor combinations show robust complete pathological response rates in non-small cell lung cancer.',
                'body': 'Neoadjuvant immunotherapeutic regimens significantly improve event-free survival in operable stages II-IIIA NSCLC.',
                'reference_name': 'Journal of Clinical Oncology',
                'reference_url': 'https://ascopubs.org/journal/jco',
                'image_url': 'https://images.unsplash.com/photo-1579684385127-1ef15d508118?auto=format&fit=crop&q=80&w=400',
                'read_time_minutes': 5,
                'published_at': timezone.now() - timedelta(days=5),
            },
            {
                'title': "Neurology Insight: New approach in Alzheimer's research.",
                'category_override': '',
                'category_name': 'Neurology',
                'headline_tag': 'NEWS',
                'is_headline': False,
                'summary': 'Targeting microglia-mediated neuroinflammation unveils novel biomarkers for presymptomatic Alzheimer disease detection.',
                'body': 'Soluble TREM2 dynamics and glial activation biomarkers offer earlier therapeutic windows.',
                'reference_name': 'Brain / Oxford Academic',
                'reference_url': 'https://academic.oup.com/brain',
                'image_url': 'https://images.unsplash.com/photo-1559757175-5700dde675bc?auto=format&fit=crop&q=80&w=400',
                'read_time_minutes': 4,
                'published_at': timezone.now() - timedelta(days=7),
            },
        ]

        for item in articles_data:
            cat_obj = ta_map.get(item['category_name'])
            Article.objects.get_or_create(
                title=item['title'],
                defaults={
                    'category': cat_obj,
                    'category_name_override': item['category_override'],
                    'headline_tag': item['headline_tag'],
                    'is_headline': item['is_headline'],
                    'summary': item['summary'],
                    'body': item['body'],
                    'reference_name': item['reference_name'],
                    'reference_url': item['reference_url'],
                    'image_url': item['image_url'],
                    'read_time_minutes': item['read_time_minutes'],
                    'published_at': item['published_at'],
                    'is_published': True,
                }
            )
        self.stdout.write(self.style.SUCCESS(f'Seeded {len(articles_data)} News & Highlight Articles.'))

        # 5. Seed Infographics & Points
        infographics_data = [
            {
                'tag': 'NUTRITIONAL SCIENCE & CARDIOLOGY',
                'title': 'Purple foods may support heart health',
                'subtitle': 'Anthocyanin-rich foods have been linked with improved vascular function and better cardiovascular health.',
                'image_url': 'https://images.unsplash.com/photo-1543362906-acfc16c67564?auto=format&fit=crop&q=80&w=800',
                'category': 'Nutritional Science & Cardiology',
                'reference': 'Recent anthocyanin meta-analysis & cardiovascular clinical trials',
                'reference_url': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7551842/',
                'quote': 'The color is not decoration. It is chemistry doing real work.',
                'alert': 'Aim for variety — different deeply colored plant foods bring diverse protective phytochemicals.',
                'points': [
                    (1, 'What are anthocyanins?', 'Plant pigments that give berries, grapes and some vegetables their blue, red and purple color.'),
                    (2, 'Blood vessel support', 'Anthocyanin-rich foods have been linked with improved vascular function and arterial flexibility.'),
                    (3, 'Where to find them', 'Blueberries, black grapes, cherries, plums, jamun, blackberries, and red cabbage.'),
                    (4, 'A simple food rule', 'Whole fruits are better than juices because they retain essential dietary fiber and antioxidants.'),
                ]
            },
            {
                'tag': 'METABOLIC SCIENCE',
                'title': 'Circadian Rhythm & Glycemic Timing',
                'subtitle': 'Meal timing aligned with circadian biological clocks enhances insulin sensitivity and glucose clearance.',
                'image_url': 'https://images.unsplash.com/photo-1505751172876-fa1923c5c528?auto=format&fit=crop&q=80&w=800',
                'category': 'Endocrinology & Metabolism',
                'reference': 'Journal of Clinical Endocrinology & Metabolism',
                'reference_url': 'https://academic.oup.com/jcem',
                'quote': 'Timing is biology. When you eat matters as much as what you eat.',
                'alert': 'Consistent eating windows reinforce metabolic rhythms and optimize daily energy homeostasis.',
                'points': [
                    (1, 'Circadian Synchronization', 'Peripheral metabolic organs function on 24-hour light-dark hormonal synchronization.'),
                    (2, 'Peak Insulin Sensitivity', 'Optimum glucose tolerance and beta-cell responsiveness occurs during daylight hours.'),
                    (3, 'Late Meal Impact', 'Evening melatonin suppresses insulin secretion, elevating nocturnal glucose excursions.'),
                    (4, 'Chrononutrition Rule', 'Front-load caloric intake earlier in the day for enhanced metabolic and lipid efficiency.'),
                ]
            }
        ]

        for info_item in infographics_data:
            infographic, created = Infographic.objects.get_or_create(
                title=info_item['title'],
                defaults={
                    'tag': info_item['tag'],
                    'subtitle': info_item['subtitle'],
                    'image_url': info_item['image_url'],
                    'category': info_item['category'],
                    'reference': info_item['reference'],
                    'reference_url': info_item['reference_url'],
                    'quote': info_item['quote'],
                    'alert': info_item['alert'],
                    'is_published': True,
                }
            )
            if created or infographic.points.count() == 0:
                for order, p_title, p_desc in info_item['points']:
                    InfographicPoint.objects.create(
                        infographic=infographic,
                        order=order,
                        title=p_title,
                        description=p_desc,
                    )
        self.stdout.write(self.style.SUCCESS(f'Seeded {len(infographics_data)} Infographics with Key Points.'))

        # 6. Seed Conferences
        conferences_data = [
            {
                'title': 'Global Cardiology Summit 2025: Emerging Innovations & Interventions',
                'category_name': 'Cardiology',
                'start_date': date(2025, 6, 18),
                'end_date': date(2025, 6, 20),
                'location': 'New Delhi / Hybrid',
                'is_virtual': True,
                'cme_credits': 18,
                'image_url': 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&q=80&w=400',
                'description': 'The premier annual assembly of international cardiologists, electrophysiologists, and cardiac surgeons exploring cutting-edge transcatheter interventions, AI imaging, and preventive cardiology protocols.',
                'agenda': [
                    'Day 1: Structural Heart Disease & Advanced Transcatheter Therapies',
                    'Day 2: Electrophysiology, Arrhythmia Ablation & Heart Failure Frontiers',
                    'Day 3: Preventive Cardiology, Cardio-Oncology & Clinical Trial Updates',
                ]
            },
            {
                'title': 'International Dermatology Conclave: Biologics & Clinical Practice',
                'category_name': 'Dermatology',
                'start_date': date(2025, 6, 25),
                'end_date': date(2025, 6, 27),
                'location': 'Mumbai Convention Centre',
                'is_virtual': True,
                'cme_credits': 15,
                'image_url': 'https://images.unsplash.com/photo-1511578314322-379afb476865?auto=format&fit=crop&q=80&w=400',
                'description': 'Deep-dive masterclasses covering biologic therapeutics, targeted JAK inhibitors in inflammatory dermatoses, and evidence-based aesthetic dermatological surgery.',
                'agenda': [
                    'Track A: Biologics & Small Molecules in Psoriasis & Atopic Dermatitis',
                    'Track B: Pediatric Dermatology, Genodermatoses & Rare Conditions',
                    'Track C: Laser Technologies, Dermoscopy & Practical Workshops',
                ]
            },
            {
                'title': 'World Oncology & Immunotherapy Congress: Treatment Protocols',
                'category_name': 'Oncology',
                'start_date': date(2025, 7, 5),
                'end_date': date(2025, 7, 7),
                'location': 'Bengaluru Medical Hub',
                'is_virtual': True,
                'cme_credits': 20,
                'image_url': 'https://images.unsplash.com/photo-1587825140708-dfaf72ae4b04?auto=format&fit=crop&q=80&w=400',
                'description': 'Comprehensive updates in immuno-oncology, antibody-drug conjugates (ADCs), and next-generation genomic tumor board case discussions.',
                'agenda': [
                    'Plenary: Next-Wave Checkpoint Modulators & Cellular Immunotherapies',
                    'Symposium: Precision Targeted Therapies & Liquid Biopsy Monitoring',
                    'Panel: Palliative Care & Toxicity Management in Modern Oncology',
                ]
            },
            {
                'title': 'Annual Neurology & Brain Health Symposium 2025',
                'category_name': 'Neurology',
                'start_date': date(2025, 7, 12),
                'end_date': date(2025, 7, 14),
                'location': 'Hyderabad International Centre',
                'is_virtual': True,
                'cme_credits': 16,
                'image_url': 'https://images.unsplash.com/photo-1475721027785-f74eccf877e2?auto=format&fit=crop&q=80&w=400',
                'description': 'Focusing on neurodegenerative disease mechanisms, acute ischemic stroke thrombolysis protocols, and migraine neuromodulation therapies.',
                'agenda': [
                    'Session 1: Acute Stroke Management & Endovascular Thrombectomy',
                    'Session 2: Alzheimer Disease, Parkinsonism & Biomarker Discovery',
                    'Session 3: Neuroimmunology, Multiple Sclerosis & Epilepsy Syndromes',
                ]
            },
        ]

        for conf in conferences_data:
            cat_obj = ta_map.get(conf['category_name'])
            Conference.objects.get_or_create(
                title=conf['title'],
                defaults={
                    'category': cat_obj,
                    'start_date': conf['start_date'],
                    'end_date': conf['end_date'],
                    'location': conf['location'],
                    'is_virtual_available': conf['is_virtual'],
                    'cme_credits': conf['cme_credits'],
                    'image_url': conf['image_url'],
                    'description': conf['description'],
                    'agenda': conf['agenda'],
                    'is_published': True,
                }
            )
        self.stdout.write(self.style.SUCCESS(f'Seeded {len(conferences_data)} Conferences.'))

        # 7. Seed Education Categories & Resources
        edu_categories = [
            {
                'key': EducationCategory.Key.PATIENT,
                'title': 'Patient Education',
                'description': 'Informative, accessible medical resources designed for patients and caregivers to enhance health literacy.',
                'icon': 'Users',
                'order': 1,
            },
            {
                'key': EducationCategory.Key.MEDICAL,
                'title': 'Medical Education',
                'description': 'Peer-reviewed clinical modules, diagnostic algorithms, and procedural guides for healthcare professionals.',
                'icon': 'BookOpen',
                'order': 2,
            },
            {
                'key': EducationCategory.Key.CME,
                'title': 'CME & Skill Workshops',
                'description': 'Accredited continuing medical education certifications, case studies, and interactive clinical masterclasses.',
                'icon': 'GraduationCap',
                'order': 3,
            },
        ]

        for cat_data in edu_categories:
            cat_obj, _ = EducationCategory.objects.get_or_create(
                key=cat_data['key'],
                defaults={
                    'title': cat_data['title'],
                    'description': cat_data['description'],
                    'icon': cat_data['icon'],
                    'order': cat_data['order'],
                }
            )
            # Add sample resources for this category
            if cat_obj.resources.count() == 0:
                EducationResource.objects.create(
                    category=cat_obj,
                    title=f"Core Clinical Principles: {cat_obj.title}",
                    description=f"Essential foundation guide and high-yield insights in {cat_obj.title.lower()}.",
                    body=f"<p>Comprehensive clinical overview and evidence-based recommendations covering key fundamentals in {cat_obj.title.lower()}.</p>",
                    external_url="https://scientice.org/education",
                    is_published=True,
                )
        self.stdout.write(self.style.SUCCESS('Seeded Education Categories and foundational resources.'))

        # 8. Seed Guidelines
        guidelines_data = [
            {
                'title': 'Clinical Practice Guidelines: Hypertension & Heart Failure Management',
                'authority': 'Cardiological Society',
                'category_name': 'Cardiology',
                'summary': 'Evidence-based recommendations on target blood pressure thresholds, quadruple guideline-directed medical therapy (GDMT), and device implantation criteria.',
                'image_url': 'https://images.unsplash.com/photo-1505751172876-fa1923c5c528?auto=format&fit=crop&q=80&w=400',
                'document_url': 'https://www.escardio.org/Guidelines',
                'published_at': timezone.now() - timedelta(days=30),
            },
            {
                'title': 'Diagnostic & Management Protocol: Type 2 Diabetes Mellitus',
                'authority': 'Endocrine & Diabetes Assc.',
                'category_name': 'Diabetology',
                'summary': 'Updated clinical standards for early dual-combination therapy, continuous glucose monitoring (CGM) metrics, and cardio-renal protective agent selection.',
                'image_url': 'https://images.unsplash.com/photo-1576091160550-2173dba999ef?auto=format&fit=crop&q=80&w=400',
                'document_url': 'https://diabetesjournals.org/care/issue/47/Supplement_1',
                'published_at': timezone.now() - timedelta(days=60),
            },
            {
                'title': 'Standard Treatment Guidelines: Severe Asthma & COPD Exacerbations',
                'authority': 'Pulmonary Care Board',
                'category_name': 'Respiratory / Pulmonology',
                'summary': 'Comprehensive biologic phenotyping protocols, triple inhaled therapy algorithms, and acute non-invasive ventilation (NIV) indications in respiratory failure.',
                'image_url': 'https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?auto=format&fit=crop&q=80&w=400',
                'document_url': 'https://goldcopd.org/2024-gold-report/',
                'published_at': timezone.now() - timedelta(days=90),
            },
            {
                'title': 'Dermatological Biologics & Psoriasis Systemic Management',
                'authority': 'Dermatology Academy',
                'category_name': 'Dermatology',
                'summary': 'Clinical decision trees for biologic transition, baseline infectious disease screening, and long-term therapeutic drug monitoring in psoriatic disease.',
                'image_url': 'https://images.unsplash.com/photo-1532938911079-1b06ac7ceec7?auto=format&fit=crop&q=80&w=400',
                'document_url': 'https://www.aad.org/member/clinical-quality/guidelines',
                'published_at': timezone.now() - timedelta(days=120),
            },
        ]

        for g in guidelines_data:
            cat_obj = ta_map.get(g['category_name'])
            Guideline.objects.get_or_create(
                title=g['title'],
                defaults={
                    'authority': g['authority'],
                    'category': cat_obj,
                    'summary': g['summary'],
                    'image_url': g['image_url'],
                    'document_url': g['document_url'],
                    'is_published': True,
                    'published_at': g['published_at'],
                }
            )
        self.stdout.write(self.style.SUCCESS(f'Seeded {len(guidelines_data)} Clinical Practice Guidelines.'))

        # 9. Seed Site Info Singleton
        site_info = SiteInfo.get_solo()
        site_info.phone = "+91 12345 67890"
        site_info.email = "info@scientice.com"
        site_info.address = "Scientiice Pvt. Ltd., Science House, Knowledge Park, Hyderabad, India - 500081"
        site_info.facebook_url = "https://facebook.com/scientice"
        site_info.instagram_url = "https://instagram.com/scientice"
        site_info.website_url = "https://scientice.com"
        site_info.save()
        self.stdout.write(self.style.SUCCESS('Seeded SiteInfo contact configuration.'))

        # 10. Seed presenter-style video bulletin landing page
        VideoBulletin.objects.update_or_create(
            slug='global-cardiology-bulletin',
            defaults={
                'title': 'Global Cardiology Bulletin',
                'eyebrow': 'GLOBAL CARDIOLOGY BULLETIN',
                'summary': 'A concise video briefing on the most important developments in cardiovascular medicine.',
                'script': (
                    'Welcome to the Global Cardiology Bulletin. In today\'s report, we review '
                    'the latest evidence shaping heart-failure care, prevention, and digital '
                    'cardiology. New clinical findings continue to support earlier risk '
                    'assessment and a patient-specific approach to guideline-directed therapy.'
                ),
                'bullet_points': [
                    'Earlier cardiovascular risk assessment remains a major prevention priority.',
                    'Guideline-directed heart-failure therapy continues to improve patient outcomes.',
                    'Remote monitoring is expanding access to specialist cardiac care.',
                    'Treatment decisions should be tailored to the individual patient and current guidelines.',
                ],
                'background_image_url': '',

                'avatar': VideoBulletin.Avatar.FEMALE_DOCTOR,
                'duration_seconds': 75,
                'is_published': True,
                'published_at': timezone.now(),
            },
        )
        self.stdout.write(self.style.SUCCESS('Seeded Global Cardiology Bulletin video report.'))

        self.stdout.write(self.style.SUCCESS('Successfully completed all Scientice database seeding!'))
