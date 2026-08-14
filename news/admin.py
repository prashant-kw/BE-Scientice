from django.contrib import admin
from django.utils.html import format_html
from .models import Article

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        'image_thumbnail',
        'title',
        'category_display_admin',
        'is_headline',
        'is_published',
        'read_time_minutes',
        'published_at',
    )
    list_display_links = ('image_thumbnail', 'title')
    list_filter = ('is_headline', 'is_published', 'category', 'published_at')
    search_fields = ('title', 'summary', 'body', 'category_name_override', 'reference_name')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_headline', 'is_published')
    ordering = ('-published_at',)
    readonly_fields = ('created_at', 'updated_at', 'image_preview_detail')

    fieldsets = (
        (None, {'fields': ('title', 'slug', 'category', 'category_name_override', 'headline_tag')}),
        ('Publication Status', {'fields': ('is_headline', 'is_published', 'published_at', 'read_time_minutes')}),
        ('Article Content', {'fields': ('summary', 'body')}),
        ('Media & Image', {'fields': ('image', 'image_url', 'image_preview_detail')}),
        ('Citations & References', {'fields': ('reference_name', 'reference_url')}),
        ('Audit Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    @admin.display(description='Thumbnail')
    def image_thumbnail(self, obj):
        url = obj.image_display_url
        if url:
            return format_html('<img src="{}" style="width: 50px; height: 35px; object-fit: cover; border-radius: 4px;" />', url)
        return format_html('<span style="color: #999;">No image</span>')

    @admin.display(description='Image Preview')
    def image_preview_detail(self, obj):
        url = obj.image_display_url
        if url:
            return format_html('<img src="{}" style="max-width: 320px; max-height: 200px; border-radius: 8px; border: 1px solid #ddd;" />', url)
        return 'No image specified'

    @admin.display(description='Category')
    def category_display_admin(self, obj):
        return obj.category_display
