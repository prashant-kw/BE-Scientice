from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Infographic, InfographicPoint

class InfographicsAPITests(APITestCase):
    def setUp(self):
        self.infographic = Infographic.objects.create(
            tag='NUTRITION',
            title='Mediterranean Diet & Vascular Function',
            subtitle='Dietary polyphenols enhance nitric oxide bioavailability.',
            quote='Food is biochemistry in action.',
            alert='Consult a registered clinical dietitian.',
            is_published=True
        )
        self.point1 = InfographicPoint.objects.create(
            infographic=self.infographic,
            order=1,
            title='Polyphenols',
            description='Bioactive compounds found in olives and greens.'
        )
        self.point2 = InfographicPoint.objects.create(
            infographic=self.infographic,
            order=2,
            title='Endothelial Health',
            description='Improves flow-mediated dilation.'
        )

    def test_list_infographics_with_nested_points(self):
        url = reverse('infographic-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        item = response.data[0]
        self.assertEqual(item['title'], 'Mediterranean Diet & Vascular Function')
        self.assertEqual(len(item['points']), 2)
        self.assertEqual(item['points'][0]['num'], '1')
        self.assertEqual(item['points'][0]['title'], 'Polyphenols')

    def test_infographic_image_absolute_url(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        test_image = SimpleUploadedFile('chart.png', b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82', content_type='image/png')
        self.infographic.image = test_image
        self.infographic.save()

        url = reverse('infographic-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item = response.data[0]
        self.assertTrue(item['image'].startswith('http://testserver/media/infographics/'))

