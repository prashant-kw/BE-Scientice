from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from therapyareas.models import TherapyArea
from .models import Guideline

class GuidelinesAPITests(APITestCase):
    def setUp(self):
        self.ta = TherapyArea.objects.create(name='Cardiology', icon='Heart')
        self.guideline = Guideline.objects.create(
            title='Clinical Practice Guideline on Lipid Lowering',
            authority='ESC/EAS',
            category=self.ta,
            summary='Targets for LDL-C reduction.',
            is_published=True
        )

    def test_list_guidelines(self):
        url = reverse('guideline-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        titles = [item['title'] for item in results]
        self.assertIn('Clinical Practice Guideline on Lipid Lowering', titles)

    def test_search_guidelines_by_authority(self):
        url = f"{reverse('guideline-list')}?search=ESC"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['authority'], 'ESC/EAS')

    def test_guideline_image_and_document_absolute_url(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        test_image = SimpleUploadedFile('guide_cover.jpg', b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b', content_type='image/jpeg')
        test_doc = SimpleUploadedFile('guide.pdf', b'%PDF-1.4 dummy pdf content', content_type='application/pdf')
        
        guideline = Guideline.objects.create(
            title='Guideline With Uploads',
            authority='AHA',
            category=self.ta,
            image=test_image,
            document_file=test_doc,
            is_published=True
        )
        url = reverse('guideline-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        item = next(x for x in results if x['id'] == guideline.id)
        self.assertTrue(item['image'].startswith('http://testserver/media/guidelines/'))
        self.assertTrue(item['documentUrl'].startswith('http://testserver/media/guidelines_docs/'))

