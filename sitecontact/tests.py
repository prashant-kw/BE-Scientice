from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import SiteInfo, ContactMessage

class SiteContactAPITests(APITestCase):
    def setUp(self):
        self.site_info = SiteInfo.get_solo()
        self.site_info.email = 'contact@scientice.org'
        self.site_info.phone = '+1 (800) 555-0199'
        self.site_info.save()

    def test_get_site_info(self):
        url = reverse('site-info')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'contact@scientice.org')
        self.assertEqual(response.data['phone'], '+1 (800) 555-0199')

    def test_post_contact_message(self):
        url = reverse('contact-submit')
        payload = {
            'name': 'Dr. Lisa Cuddy',
            'email': 'cuddy@ppth.org',
            'subject': 'Editorial Board Inquiry',
            'message': 'I would like to submit a clinical commentary on renal biomarkers.',
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ContactMessage.objects.count(), 1)
        msg = ContactMessage.objects.first()
        self.assertEqual(msg.name, 'Dr. Lisa Cuddy')
        self.assertEqual(msg.is_read, False)
