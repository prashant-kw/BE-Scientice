from django.contrib import admin
from .models import EducationCategory, EducationResource

@admin.register(EducationCategory)
class EducationCategoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'title', 'key', 'is_active', 'icon')
    list_display_links = ('title',)
    list_editable = ('order', 'is_active')
    list_filter = ('is_active', 'key')
    search_fields = ('title', 'description', 'key')

@admin.register(EducationResource)
class EducationResourceAdmin(admin.ModelAdmin):
    list_display = ('image_thumbnail', 'title', 'category', 'is_published', 'published_at')
    list_display_links = ('image_thumbnail', 'title')
    list_filter = ('category', 'is_published', 'published_at')
    search_fields = ('title', 'description', 'body')
    list_editable = ('is_published',)
    ordering = ('-published_at',)
    readonly_fields = ('created_at', 'updated_at', 'image_preview_detail')

    fieldsets = (
        (None, {'fields': ('title', 'category', 'icon')}),
        ('Publication Status', {'fields': ('is_published', 'published_at')}),
        ('Content', {'fields': ('description', 'body')}),
        ('Media & Documents', {'fields': ('image', 'image_url', 'image_preview_detail', 'file', 'external_url')}),
        ('Audit Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    @admin.display(description='Thumbnail')
    def image_thumbnail(self, obj):
        from django.utils.html import format_html
        url = obj.image_display_url
        if url:
            return format_html('<img src="{}" style="width: 50px; height: 35px; object-fit: cover; border-radius: 4px;" />', url)
        return format_html('<span style="color: #999;">No image</span>')

    @admin.display(description='Image Preview')
    def image_preview_detail(self, obj):
        from django.utils.html import format_html
        url = obj.image_display_url
        if url:
            return format_html('<img src="{}" style="max-width: 320px; max-height: 200px; border-radius: 8px; border: 1px solid #ddd;" />', url)
        return 'No image specified'
