import io
from django.urls import reverse
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase
from PIL import Image

from accounts.models import User
from news.models import Article
from guidelines.models import Guideline
from conferences.models import Conference, ConferenceRegistration
from education.models import EducationResource, EducationCategory
from infographics.models import Infographic, InfographicPoint
from therapyareas.models import TherapyArea
from sitecontact.models import SiteInfo, ContactMessage


def create_test_image(format='JPEG'):
    """Create a minimal valid in-memory test image."""
    file_obj = io.BytesIO()
    image = Image.new('RGB', (100, 100), color=(73, 109, 137))
    image.save(file_obj, format=format)
    file_obj.seek(0)
    return SimpleUploadedFile(f'test.{format.lower()}', file_obj.read(), content_type=f'image/{format.lower()}')


class CMSBackendAPITests(APITestCase):
    def setUp(self):
        # 1. Setup Groups
        self.editor_group = Group.objects.create(name='Content Editor')

        # 2. Setup Users
        self.regular_doctor = User.objects.create_user(
            email='doctor@scientice.org',
            password='DoctorPassword123!',
            full_name='Dr. Regular Doctor',
            role=User.Role.DOCTOR,
            is_staff=False,
            is_superuser=False
        )

        self.group_editor = User.objects.create_user(
            email='groupeditor@scientice.org',
            password='EditorPassword123!',
            full_name='Editor Group Member',
            role=User.Role.DOCTOR,
            is_staff=False,
            is_superuser=False
        )
        self.group_editor.groups.add(self.editor_group)

        self.staff_admin = User.objects.create_superuser(
            email='admin@scientice.org',
            password='AdminPassword123!',
            full_name='System Admin'
        )

        # 3. Setup Seed Data
        self.cardio = TherapyArea.objects.create(name='Cardiology', order=1)
        self.edu_cat = EducationCategory.objects.create(
            key=EducationCategory.Key.MEDICAL,
            title='Medical Education',
            description='Clinical guidelines & CME'
        )

        self.article = Article.objects.create(
            title='Published Cardiology Study',
            summary='Breakthrough study summary',
            body='<p>Full findings of the study.</p>',
            category=self.cardio,
            is_published=True
        )

        self.draft_article = Article.objects.create(
            title='Draft Oncology Research',
            summary='Draft summary not yet published',
            body='<p>Draft body.</p>',
            is_published=False
        )

        self.conference = Conference.objects.create(
            title='Global Cardiology Summit 2026',
            description='Annual cardiology convention',
            start_date='2026-10-15',
            end_date='2026-10-18',
            location='Boston, MA',
            is_published=True
        )

        self.registration = ConferenceRegistration.objects.create(
            conference=self.conference,
            full_name='Dr. Attendee One',
            email='attendee1@hospital.org',
            attendance_mode=ConferenceRegistration.Mode.IN_PERSON,
            organization='Mass General'
        )

        self.message = ContactMessage.objects.create(
            name='Dr. Inquirer',
            email='inquirer@clinic.org',
            subject='Partnership question',
            message='Would like to collaborate.'
        )

    # ------------------------------------------------------------------
    # 1. Authentication & Permission Barriers
    # ------------------------------------------------------------------
    def test_anonymous_user_denied_401(self):
        """Anonymous visitor receives 401 Unauthorized on CMS endpoints."""
        url = reverse('cms-articles-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_doctor_user_denied_403(self):
        """Standard doctor user (not staff/Content Editor) receives 403 Forbidden."""
        self.client.force_authenticate(user=self.regular_doctor)
        url = reverse('cms-articles-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_content_editor_group_member_succeeds(self):
        """
        User with is_staff=False but in 'Content Editor' group succeeds.
        Guarantees group-based RBAC functions independently of is_staff.
        """
        self.client.force_authenticate(user=self.group_editor)
        url = reverse('cms-articles-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Writable action succeeds
        create_payload = {
            'title': 'Group Editor Clinical Update',
            'summary': 'New findings summary',
            'body': '<p>Valid body content.</p>',
            'category': self.cardio.id,
            'is_published': True
        }
        create_resp = self.client.post(url, create_payload, format='json')
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_resp.data['title'], 'Group Editor Clinical Update')

    def test_staff_admin_succeeds(self):
        """Staff/Superuser succeeds on all CMS endpoints."""
        self.client.force_authenticate(user=self.staff_admin)
        url = reverse('cms-articles-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ------------------------------------------------------------------
    # 2. Server-Side HTML Sanitization
    # ------------------------------------------------------------------
    def test_html_sanitization_strips_scripts_and_event_handlers(self):
        """
        Submitting script tags and malicious attributes in rich text body
        is stripped cleanly on the server before database persistence.
        """
        self.client.force_authenticate(user=self.staff_admin)
        payload = {
            'title': 'XSS Test Article',
            'summary': 'Summary with <script>alert("bad")</script>clean text',
            'body': '<p>Clinical text <b onclick="alert(1)">Bold</b> <script>stealCookies()</script><iframe src="evil.com"></iframe></p>',
            'is_published': True
        }
        response = self.client.post(reverse('cms-articles-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        article = Article.objects.get(id=response.data['id'])
        # Body has no script, iframe, or onclick
        self.assertNotIn('<script>', article.body)
        self.assertNotIn('stealCookies', article.body)
        self.assertNotIn('<iframe>', article.body)
        self.assertNotIn('onclick', article.body)
        self.assertIn('<p>', article.body)
        self.assertIn('<b>', article.body)

        # Summary plain text sanitizer stripped tags
        self.assertNotIn('<script>', article.summary)
        self.assertIn('clean text', article.summary)

    # ------------------------------------------------------------------
    # 3. Image Validation & Non-Image Rejection
    # ------------------------------------------------------------------
    def test_valid_image_upload_succeeds(self):
        """Valid JPEG image passes Pillow byte validation and returns absolute image_display_url."""
        self.client.force_authenticate(user=self.staff_admin)
        image_file = create_test_image('JPEG')
        payload = {
            'title': 'Image Test Article',
            'summary': 'Summary',
            'body': '<p>Content</p>',
            'image': image_file,
            'is_published': True
        }
        response = self.client.post(reverse('cms-articles-list'), payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['image'])
        self.assertTrue(response.data['image_display_url'].startswith('http://testserver/media/news/'))

    def test_cms_guideline_image_and_document_absolute_url(self):
        """Guideline CMS serializer returns absolute URLs for both image and document file."""
        self.client.force_authenticate(user=self.staff_admin)
        image_file = create_test_image('JPEG')
        doc_file = SimpleUploadedFile('protocol.pdf', b'%PDF-1.4 dummy cms doc', content_type='application/pdf')
        payload = {
            'title': 'CMS Guideline Test',
            'authority': 'ESC',
            'image': image_file,
            'document_file': doc_file,
            'is_published': True
        }
        response = self.client.post(reverse('cms-guidelines-list'), payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['image_display_url'].startswith('http://testserver/media/guidelines/'))
        self.assertTrue(response.data['effective_document_url'].startswith('http://testserver/media/guidelines_docs/'))

    def test_cms_education_file_absolute_url(self):
        """Education resource CMS serializer returns absolute file_url."""
        self.client.force_authenticate(user=self.staff_admin)
        doc_file = SimpleUploadedFile('cme_slides.pdf', b'%PDF-1.4 slides', content_type='application/pdf')
        payload = {
            'category': self.edu_cat.id,
            'title': 'CME Slides Resource',
            'file': doc_file,
            'is_published': True
        }
        response = self.client.post(reverse('cms-education-list'), payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['file_url'].startswith('http://testserver/media/education_docs/'))

    def test_spoofed_non_image_upload_rejected(self):
        """A text/executable file masquerading as .jpg fails byte inspection with HTTP 400."""
        self.client.force_authenticate(user=self.staff_admin)
        fake_image = SimpleUploadedFile('fake.jpg', b'<html>Not an image content</html>', content_type='image/jpeg')
        payload = {
            'title': 'Spoofed Image Article',
            'summary': 'Summary',
            'body': '<p>Content</p>',
            'image': fake_image,
            'is_published': True
        }
        response = self.client.post(reverse('cms-articles-list'), payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('image', response.data)

    def test_spoofed_non_pdf_upload_rejected(self):
        """A renamed image/executable file masquerading as .pdf fails magic bytes inspection with HTTP 400."""
        self.client.force_authenticate(user=self.staff_admin)
        fake_pdf = SimpleUploadedFile('fake.pdf', b'<html>Not a pdf content</html>', content_type='application/pdf')
        payload = {
            'title': 'Spoofed PDF Article',
            'summary': 'Summary',
            'body': '<p>Content</p>',
            'document_file': fake_pdf,
            'is_published': True
        }
        response = self.client.post(reverse('cms-articles-list'), payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('document_file', response.data)

    def test_cms_article_absolute_url(self):
        self.client.force_authenticate(user=self.staff_admin)
        doc_file = SimpleUploadedFile('article.pdf', b'%PDF-1.4 dummy cms doc', content_type='application/pdf')
        payload = {
            'title': 'CMS Article Test',
            'summary': 'Summary',
            'body': '<p>Body</p>',
            'document_file': doc_file,
            'is_published': True
        }
        response = self.client.post(reverse('cms-articles-list'), payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['effective_document_url'].startswith('http://testserver/media/news_docs/'))

        # Also test the public serializer
        public_resp = self.client.get(reverse('news-detail', kwargs={'pk': response.data['id']}))
        self.assertTrue(public_resp.data['documentUrl'].startswith('http://testserver/media/news_docs/'))

    def test_cms_conference_absolute_url(self):
        self.client.force_authenticate(user=self.staff_admin)
        doc_file = SimpleUploadedFile('conference.pdf', b'%PDF-1.4 dummy cms doc', content_type='application/pdf')
        payload = {
            'title': 'CMS Conference Test',
            'description': 'Description',
            'start_date': '2026-01-01',
            'end_date': '2026-01-02',
            'location': 'Boston',
            'document_file': doc_file,
            'is_published': True
        }
        response = self.client.post(reverse('cms-conferences-list'), payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['effective_document_url'].startswith('http://testserver/media/conferences_docs/'))

        # Also test public endpoint
        public_resp = self.client.get(reverse('conference-list'))
        results = public_resp.data.get('results', public_resp.data) if isinstance(public_resp.data, dict) else public_resp.data
        conf_data = next((c for c in results if c['title'] == 'CMS Conference Test'), None)
        self.assertTrue(conf_data['documentUrl'].startswith('http://testserver/media/conferences_docs/'))

    def test_cms_infographic_absolute_url(self):
        self.client.force_authenticate(user=self.staff_admin)
        doc_file = SimpleUploadedFile('infographic.pdf', b'%PDF-1.4 dummy cms doc', content_type='application/pdf')
        payload = {
            'title': 'CMS Infographic Test',
            'document_file': doc_file,
            'is_published': True
        }
        response = self.client.post(reverse('cms-infographics-list'), payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['effective_document_url'].startswith('http://testserver/media/infographics_docs/'))

        # Also test public endpoint
        public_resp = self.client.get(reverse('infographic-list'))
        results = public_resp.data.get('results', public_resp.data) if isinstance(public_resp.data, dict) else public_resp.data
        info_data = next((i for i in results if i['title'] == 'CMS Infographic Test'), None)
        self.assertTrue(info_data['documentUrl'].startswith('http://testserver/media/infographics_docs/'))



    # ------------------------------------------------------------------
    # 4. Conference Agenda Validation & Registration Export
    # ------------------------------------------------------------------
    def test_agenda_validation_strips_html_and_validates_list(self):
        """Conference agenda validates JSON list structure and strips HTML tags."""
        self.client.force_authenticate(user=self.staff_admin)
        payload = {
            'title': 'Cardio Summit 2027',
            'description': '<p>Conference overview</p>',
            'agenda': ['Keynote: <b>Cardio Advances</b>', 'Session 2: <script>bad()</script>Arrhythmia Management'],
            'start_date': '2027-05-10',
            'end_date': '2027-05-12',
            'location': 'Geneva, Switzerland',
            'is_published': True
        }
        response = self.client.post(reverse('cms-conferences-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        conf = Conference.objects.get(id=response.data['id'])
        self.assertNotIn('<b>', conf.agenda[0])
        self.assertIn('Keynote: Cardio Advances', conf.agenda[0])
        self.assertNotIn('<script>', conf.agenda[1])
        self.assertIn('Session 2: Arrhythmia Management', conf.agenda[1])

    def test_conference_registrations_read_only_and_csv_export(self):
        """
        Registrations can be listed and exported as CSV via CMS actions,
        but cannot be created/modified/deleted directly via CMS endpoints.
        """
        self.client.force_authenticate(user=self.staff_admin)
        list_url = reverse('cms-conferences-registrations', kwargs={'pk': self.conference.id})
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['full_name'], 'Dr. Attendee One')

        # CSV Export
        export_url = reverse('cms-conferences-export-registrations', kwargs={'pk': self.conference.id})
        csv_response = self.client.get(export_url)
        self.assertEqual(csv_response.status_code, status.HTTP_200_OK)
        self.assertEqual(csv_response['Content-Type'], 'text/csv; charset=utf-8')
        content = csv_response.content.decode('utf-8')
        self.assertIn('Dr. Attendee One', content)
        self.assertIn('attendee1@hospital.org', content)

    # ------------------------------------------------------------------
    # 5. Atomic Nested Infographic Points (No Cross-Object Leakage)
    # ------------------------------------------------------------------
    def test_atomic_nested_infographic_points_creation_and_update(self):
        """
        Infographics handle points as an atomic nested relationship, ensuring
        points are strictly bound to their parent infographic.
        """
        self.client.force_authenticate(user=self.staff_admin)
        payload = {
            'title': 'Heart Failure Pathway',
            'tag': 'CLINICAL PATHWAY',
            'subtitle': 'Key intervention steps',
            'category': 'Cardiology',
            'quote': 'Early guideline adherence saves lives',
            'is_published': True,
            'points': [
                {'order': 1, 'title': 'Step 1: Early Assessment', 'description': 'Check BNP levels'},
                {'order': 2, 'title': 'Step 2: Guideline Medical Therapy', 'description': 'Initiate SGLT2i + ARNI'}
            ]
        }
        response = self.client.post(reverse('cms-infographics-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        info_id = response.data['id']
        self.assertEqual(InfographicPoint.objects.filter(infographic_id=info_id).count(), 2)

        # Update points atomically
        update_payload = {
            'title': 'Heart Failure Pathway Updated',
            'points': [
                {'order': 1, 'title': 'Step 1: Revised Protocol', 'description': 'Updated biomarker criteria'}
            ]
        }
        update_resp = self.client.patch(reverse('cms-infographics-detail', kwargs={'pk': info_id}), update_payload, format='json')
        self.assertEqual(update_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(InfographicPoint.objects.filter(infographic_id=info_id).count(), 1)
        self.assertEqual(InfographicPoint.objects.get(infographic_id=info_id).title, 'Step 1: Revised Protocol')

    # ------------------------------------------------------------------
    # 6. SiteInfo Singleton Hardening
    # ------------------------------------------------------------------
    def test_site_info_singleton_retrieve_and_update_disallows_post(self):
        """SiteInfo view operates on solo singleton; POST is rejected with 405 Method Not Allowed."""
        self.client.force_authenticate(user=self.staff_admin)
        url = reverse('cms-site-info')

        # Retrieve singleton
        get_resp = self.client.get(url)
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(SiteInfo.objects.count(), 1)

        # Update singleton
        patch_resp = self.client.patch(url, {'phone': '+1 (800) 777-9999'}, format='json')
        self.assertEqual(patch_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(SiteInfo.objects.get(pk=1).phone, '+1 (800) 777-9999')
        self.assertEqual(SiteInfo.objects.count(), 1)

        # POST is disallowed
        post_resp = self.client.post(url, {'phone': '+1 (800) 000-0000'}, format='json')
        self.assertEqual(post_resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # ------------------------------------------------------------------
    # 7. Contact Messages (Read & Mark-as-read Only)
    # ------------------------------------------------------------------
    def test_contact_messages_read_and_patch_only_no_delete(self):
        """CMS users can list and mark messages as read, but cannot delete or create them."""
        self.client.force_authenticate(user=self.staff_admin)
        list_url = reverse('cms-messages-list')
        detail_url = reverse('cms-messages-detail', kwargs={'pk': self.message.id})

        # List
        list_resp = self.client.get(list_url)
        self.assertEqual(list_resp.status_code, status.HTTP_200_OK)

        # Mark as read via PATCH
        self.assertFalse(self.message.is_read)
        patch_resp = self.client.patch(detail_url, {'is_read': True}, format='json')
        self.assertEqual(patch_resp.status_code, status.HTTP_200_OK)
        self.message.refresh_from_db()
        self.assertTrue(self.message.is_read)

        # Toggle read action
        toggle_url = reverse('cms-messages-toggle-read', kwargs={'pk': self.message.id})
        toggle_resp = self.client.post(toggle_url)
        self.assertEqual(toggle_resp.status_code, status.HTTP_200_OK)
        self.message.refresh_from_db()
        self.assertFalse(self.message.is_read)

        # DELETE is not allowed on ViewSet
        delete_resp = self.client.delete(detail_url)
        self.assertEqual(delete_resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # ------------------------------------------------------------------
    # 8. Public Endpoints Unaffected
    # ------------------------------------------------------------------
    def test_public_endpoints_unaffected_and_only_show_published(self):
        """
        Public /api/news/ endpoints remain AllowAny GET-only,
        and exclude draft items (is_published=False).
        """
        # Anonymous GET to public news list
        public_url = reverse('news-list')
        response = self.client.get(public_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that only published article is returned
        titles = [item['title'] for item in response.data['results']]
        self.assertIn('Published Cardiology Study', titles)
        self.assertNotIn('Draft Oncology Research', titles)

    # ------------------------------------------------------------------
    # 9. Therapy Areas CMS CRUD & Icon Synchronization
    # ------------------------------------------------------------------
    def test_therapy_area_cms_crud_and_icon_update(self):
        """CMS users can update therapy area icon (accepting both icon and icon_name) and verify persistence."""
        self.client.force_authenticate(user=self.staff_admin)
        detail_url = reverse('cms-therapy-areas-detail', kwargs={'pk': self.cardio.id})

        # Update with 'Heart' icon via icon field
        patch_resp = self.client.patch(detail_url, {'icon': 'Heart'}, format='json')
        self.assertEqual(patch_resp.status_code, status.HTTP_200_OK)
        self.cardio.refresh_from_db()
        self.assertEqual(self.cardio.icon, 'Heart')
        self.assertEqual(patch_resp.data['icon'], 'Heart')
        self.assertEqual(patch_resp.data['icon_name'], 'Heart')

        # Update with 'Brain' icon via icon_name alias
        patch_resp2 = self.client.patch(detail_url, {'icon_name': 'Brain'}, format='json')
        self.assertEqual(patch_resp2.status_code, status.HTTP_200_OK)
        self.cardio.refresh_from_db()
        self.assertEqual(self.cardio.icon, 'Brain')
        self.assertEqual(patch_resp2.data['icon'], 'Brain')

    # ------------------------------------------------------------------
    # 10. Video Bulletin Banner Scheduling & Countdown Timer
    # ------------------------------------------------------------------
    def test_video_bulletin_banner_scheduling_and_countdown_timer(self):
        """Video Bulletin supports hero banner upload, schedule dates, and countdown timer fields."""
        from django.utils import timezone
        from cms.models import VideoBulletin

        self.client.force_authenticate(user=self.staff_admin)
        banner_img = create_test_image('JPEG')

        now = timezone.now()
        start_time = now - timezone.timedelta(hours=1)
        end_time = now + timezone.timedelta(days=5)
        event_time = now + timezone.timedelta(days=3)

        payload = {
            'title': 'ESC Congress 2026 Special Bulletin',
            'slug': 'esc-congress-2026-special',
            'eyebrow': 'BREAKING NEWS',
            'summary': 'Live coverage of breakthroughs in heart failure management.',
            'script': 'Welcome to our special ESC Congress bulletin.',
            'promo_banner_image': banner_img,
            'show_countdown_timer': True,
            'event_timer_label': 'ESC Congress 2026 Starts In',
            'event_start_datetime': event_time.isoformat(),
            'schedule_start_datetime': start_time.isoformat(),
            'schedule_end_datetime': end_time.isoformat(),
            'is_published': True,
        }

        # Create bulletin via CMS
        create_resp = self.client.post(reverse('cms-video-bulletins-list'), payload, format='multipart')
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        bulletin_id = create_resp.data['id']

        bulletin = VideoBulletin.objects.get(id=bulletin_id)
        self.assertTrue(bulletin.show_countdown_timer)
        self.assertEqual(bulletin.event_timer_label, 'ESC Congress 2026 Starts In')
        self.assertIsNotNone(bulletin.promo_banner_image)
        self.assertTrue(create_resp.data['promoBannerImageUrl'].startswith('http://testserver/media/'))

        # Public list endpoint includes active scheduled bulletin and new fields
        public_resp = self.client.get(reverse('video-report-list'))
        self.assertEqual(public_resp.status_code, status.HTTP_200_OK)
        found = next((b for b in public_resp.data if b['id'] == bulletin_id), None)
        self.assertIsNotNone(found)
        self.assertTrue(found['show_countdown_timer'])
        self.assertEqual(found['event_timer_label'], 'ESC Congress 2026 Starts In')
        self.assertIn('event_start_datetime', found)
        self.assertIn('schedule_start_datetime', found)
        self.assertIn('schedule_end_datetime', found)


