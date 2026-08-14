from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from therapyareas.models import TherapyArea
from .models import Article

class NewsAPITests(APITestCase):
    def setUp(self):
        self.ta = TherapyArea.objects.create(name='Cardiology', icon='Heart')
        self.headline_article = Article.objects.create(
            title='Cardiology Headline Breakthrough',
            category=self.ta,
            summary='Breakthrough cardiology discovery summary.',
            is_headline=True,
            is_published=True
        )
        self.regular_article = Article.objects.create(
            title='Routine Cardiology Update',
            category=self.ta,
            summary='Regular news brief.',
            is_headline=False,
            is_published=True
        )
        self.unpublished_article = Article.objects.create(
            title='Draft Article Not Ready',
            category=self.ta,
            summary='Draft content.',
            is_headline=False,
            is_published=False
        )

    def test_list_published_articles(self):
        url = reverse('news-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that unpublished article is not returned
        results = response.data.get('results', response.data)
        titles = [item['title'] for item in results]
        self.assertIn('Cardiology Headline Breakthrough', titles)
        self.assertIn('Routine Cardiology Update', titles)
        self.assertNotIn('Draft Article Not Ready', titles)

    def test_highlights_endpoint(self):
        url = reverse('news-highlights')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [item['title'] for item in response.data]
        self.assertIn('Cardiology Headline Breakthrough', titles)
        self.assertNotIn('Routine Cardiology Update', titles)

    def test_filter_by_therapy_area(self):
        url = f"{reverse('news-list')}?therapy_area=Cardiology"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        for item in results:
            self.assertEqual(item['category'], 'Cardiology')

    def test_article_image_absolute_url(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b',
            content_type='image/jpeg'
        )
        article = Article.objects.create(
            title='Image Test Article',
            category=self.ta,
            summary='Testing image absolute URL.',
            image=test_image,
            is_published=True
        )
        url = reverse('news-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        item = next(x for x in results if x['id'] == article.id)
        self.assertTrue(item['image'].startswith('http://testserver/media/news/'))

