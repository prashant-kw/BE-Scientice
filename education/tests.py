from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import EducationCategory, EducationResource

class EducationAPITests(APITestCase):
    def setUp(self):
        self.cat_patient = EducationCategory.objects.create(
            key=EducationCategory.Key.PATIENT,
            title='Patient Education',
            description='Patient resources',
            icon='Users',
            order=1
        )
        self.cat_med = EducationCategory.objects.create(
            key=EducationCategory.Key.MEDICAL,
            title='Medical Education',
            description='HCP modules',
            icon='BookOpen',
            order=2
        )
        self.res = EducationResource.objects.create(
            category=self.cat_patient,
            title='Understanding Blood Pressure',
            description='A guide for patients',
            is_published=True
        )

    def test_list_education_categories(self):
        url = reverse('education-categories')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        keys = [item['key'] for item in response.data]
        self.assertIn('patient', keys)
        self.assertIn('medical', keys)

    def test_patient_education_list(self):
        url = reverse('education-patient')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        titles = [item['title'] for item in results]
        self.assertIn('Understanding Blood Pressure', titles)

    def test_education_resource_file_absolute_url(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        test_file = SimpleUploadedFile('patient_pamphlet.pdf', b'%PDF-1.4 sample content', content_type='application/pdf')
        self.res.file = test_file
        self.res.save()

        url = reverse('education-patient')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        item = next(x for x in results if x['id'] == self.res.id)
        self.assertTrue(item['fileUrl'].startswith('http://testserver/media/education_docs/'))

