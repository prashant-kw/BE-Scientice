from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import TherapyArea

class TherapyAreaAPITests(APITestCase):
    def setUp(self):
        self.cardio = TherapyArea.objects.create(
            name='Cardiology',
            icon='Heart',
            description='Cardiovascular medicine'
        )
        self.derm = TherapyArea.objects.create(
            name='Dermatology',
            icon='Sparkles',
            description='Skin health and clinical dermatology'
        )

    def test_list_therapy_areas(self):
        url = reverse('therapy-area-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify unpaginated list returns array of items with name, icon, slug
        names = [item['name'] for item in response.data]
        self.assertIn('Cardiology', names)
        self.assertIn('Dermatology', names)

    def test_retrieve_therapy_area_detail_by_slug_or_id(self):
        url = reverse('therapy-area-detail', kwargs={'slug': self.cardio.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Cardiology')
        self.assertEqual(response.data['icon'], 'Heart')


