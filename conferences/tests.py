from datetime import date, timedelta
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from therapyareas.models import TherapyArea
from .models import Conference

class ConferencesAPITests(APITestCase):
    def setUp(self):
        self.ta = TherapyArea.objects.create(name='Cardiology', icon='Heart')
        self.conf = Conference.objects.create(
            title='Global Cardiology Summit',
            category=self.ta,
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=12),
            location='Boston, MA & Online',
            is_virtual_available=True,
            cme_credits=12,
            is_published=True
        )

    def test_list_upcoming_conferences(self):
        url = reverse('conference-upcoming')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        titles = [item['title'] for item in results]
        self.assertIn('Global Cardiology Summit', titles)

    def test_register_for_conference(self):
        url = reverse('conference-register', kwargs={'pk': self.conf.pk})
        payload = {
            'fullName': 'Dr. Robert Smith',
            'email': 'drsmith@hospital.org',
            'attendanceMode': 'in_person',
            'organization': 'Boston General Hospital',
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.conf.registrations.count(), 1)
        registration = self.conf.registrations.first()
        self.assertEqual(registration.full_name, 'Dr. Robert Smith')
        self.assertEqual(registration.attendance_mode, 'in_person')

    def test_conference_image_absolute_url(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        test_image = SimpleUploadedFile('conf_banner.jpg', b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b', content_type='image/jpeg')
        self.conf.image = test_image
        self.conf.save()

        url = reverse('conference-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        item = next(x for x in results if x['id'] == self.conf.id)
        self.assertTrue(item['image'].startswith('http://testserver/media/conferences/'))

