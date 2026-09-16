import os
import django
import csv
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from cms.models import VideoBulletin
from news.models import Article

def export_published_content(site_url='https://scientice.com', filename='published_content.csv'):
    # Ensure site_url ends without a trailing slash for consistent joining
    site_url = site_url.rstrip('/')
    
    # Fetch published videos
    videos = VideoBulletin.objects.filter(is_published=True).order_by('-published_at')
    
    # Optionally, we can also fetch Articles or other content.
    # The user mentioned "published video" but also "published content". 
    # We will focus on videos but can add a type column if mixing.
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow(['Type', 'Title', 'Description', 'URL', 'Published At'])
        
        count = 0
        
        # Export Video Bulletins
        for video in videos:
            title = video.title
            description = video.summary
            url = f"{site_url}/{video.slug}"
            published_at = video.published_at.strftime('%Y-%m-%d %H:%M:%S') if video.published_at else ''
            
            writer.writerow(['Video', title, description, url, published_at])
            count += 1
            
        # If you also want to include News Articles, uncomment the following block:
        """
        articles = Article.objects.filter(is_published=True).order_by('-published_at')
        for article in articles:
            title = article.title
            description = article.summary
            # For articles, verify the correct route, e.g., /news/<slug> or /<slug>
            url = f"{site_url}/{article.slug}"
            published_at = article.published_at.strftime('%Y-%m-%d %H:%M:%S') if article.published_at else ''
            
            writer.writerow(['Article', title, description, url, published_at])
            count += 1
        """
            
    print(f"Successfully exported {count} published items to {filename}")
    print(f"You can open {filename} directly in Microsoft Excel.")

if __name__ == '__main__':
    # You can pass a custom site URL and filename as arguments if needed
    site = sys.argv[1] if len(sys.argv) > 1 else 'https://scientice.com'
    export_published_content(site_url=site)
