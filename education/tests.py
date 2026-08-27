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
            order=1,
            is_active=True,
        )
        self.cat_med = EducationCategory.objects.create(
            key=EducationCategory.Key.MEDICAL,
            title='Medical Education',
            description='HCP modules',
            icon='BookOpen',
            order=2,
            is_active=True,
        )
        self.cat_cme = EducationCategory.objects.create(
            key=EducationCategory.Key.CME,
            title='CME & Guidelines',
            description='CME courses',
            icon='GraduationCap',
            order=3,
            is_active=False,
        )
        self.res_patient = EducationResource.objects.create(
            category=self.cat_patient,
            title='Patient Awareness Handbook',
            description='A guide for patients',
            is_published=True,
        )
        self.res_med = EducationResource.objects.create(
            category=self.cat_med,
            title='Clinical Specialist Module',
            description='A guide for clinicians',
            is_published=True,
        )
        self.res_cme = EducationResource.objects.create(
            category=self.cat_cme,
            title='CME Clinical Review',
            description='Continuing medical education',
            is_published=True,
        )

    def test_list_active_education_categories(self):
        """Active categories are returned; disabled CME is excluded."""
        url = reverse('education-categories')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        keys = [item['key'] for item in response.data]
        self.assertIn('patient', keys)
        self.assertIn('medical', keys)
        self.assertNotIn('cme', keys)

    def test_reenabling_cme_makes_it_available(self):
        """When CME category is enabled by admin, it is included in categories list."""
        self.cat_cme.is_active = True
        self.cat_cme.save()

        url = reverse('education-categories')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        keys = [item['key'] for item in response.data]
        self.assertIn('cme', keys)

    def test_patient_education_list_active(self):
        """Patient education list returns active published resources."""
        url = reverse('education-patient')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        titles = [item['title'] for item in results]
        self.assertIn('Patient Awareness Handbook', titles)

    def test_medical_education_list_active(self):
        """Medical education list returns active published resources."""
        url = reverse('education-medical')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        titles = [item['title'] for item in results]
        self.assertIn('Clinical Specialist Module', titles)

    def test_disabled_category_resources_hidden(self):
        """Resources under a disabled category are not returned."""
        url = reverse('education-guidelines-cme')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 0)

        # Deactivating Medical hides its resources
        self.cat_med.is_active = False
        self.cat_med.save()
        med_res = self.client.get(reverse('education-medical'))
        med_results = med_res.data.get('results', med_res.data)
        self.assertEqual(len(med_results), 0)

    def test_disabling_category_does_not_delete_resources(self):
        """Disabling a category preserves its resources in database."""
        self.cat_cme.is_active = False
        self.cat_cme.save()
        self.assertTrue(EducationResource.objects.filter(id=self.res_cme.id).exists())

        # Re-enabling exposes the resource again
        self.cat_cme.is_active = True
        self.cat_cme.save()
        cme_res = self.client.get(reverse('education-guidelines-cme'))
        cme_results = cme_res.data.get('results', cme_res.data)
        titles = [item['title'] for item in cme_results]
        self.assertIn('CME Clinical Review', titles)

    def test_api_requests_do_not_recreate_deleted_resources(self):
        """Deleting a resource from CMS does not get auto-recreated on API requests."""
        self.res_patient.delete()
        self.assertEqual(EducationResource.objects.filter(category=self.cat_patient).count(), 0)

        # Requesting API does not recreate it
        url = reverse('education-patient')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(EducationResource.objects.filter(category=self.cat_patient).count(), 0)

    def test_education_resource_file_absolute_url(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        test_file = SimpleUploadedFile('patient_pamphlet.pdf', b'%PDF-1.4 sample content', content_type='application/pdf')
        self.res_patient.file = test_file
        self.res_patient.save()

        url = reverse('education-patient')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        item = next(x for x in results if x['id'] == self.res_patient.id)
        self.assertTrue(item['fileUrl'].startswith('http://testserver/media/education_docs/'))

