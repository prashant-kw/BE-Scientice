import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from cms.models import Page
import re

print("Updating pages to use Markdown instead of HTML...")

# Remove HTML tags from existing pages to convert them to Markdown
pages = Page.objects.all()
for page in pages:
    content = page.content
    if '<div' in content or '<h3' in content:
        # Convert simple HTML seed data to Markdown
        content = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1\n\n', content)
        content = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', content)
        content = re.sub(r'<[^>]+>', '', content)
        content = content.strip()
        page.content = content
        page.save()
        print(f"Updated {page.slug} to Markdown format.")

print("Done updating pages.")
