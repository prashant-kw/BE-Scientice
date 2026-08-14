import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from cms.models import Page

pages_to_seed = [
    {
        'title': 'Privacy Policy',
        'slug': 'privacy-policy',
        'content': '### Content Coming Soon\n\nThis privacy policy is currently being updated by our legal team.',
    },
    {
        'title': 'Terms & Conditions',
        'slug': 'terms-and-conditions',
        'content': '### Content Coming Soon\n\nThese terms and conditions are currently being updated.',
    },
    {
        'title': 'Clinical Disclaimer',
        'slug': 'clinical-disclaimer',
        'content': '### Content Coming Soon\n\nThis clinical disclaimer is currently being updated by our editorial board.',
    },
    {
        'title': 'Medical Directory',
        'slug': 'medical-directory',
        'content': '### Medical Directory Coming Soon\n\nOur comprehensive directory of verified healthcare professionals is currently being compiled.',
    }
]

created_count = 0
for data in pages_to_seed:
    page, created = Page.objects.get_or_create(slug=data['slug'], defaults={
        'title': data['title'],
        'content': data['content'],
        'is_published': True
    })
    if created:
        print(f"Created page: {page.slug}")
        created_count += 1
    else:
        print(f"Page already exists: {page.slug}")

print(f"\nSuccessfully seeded {created_count} pages.")
