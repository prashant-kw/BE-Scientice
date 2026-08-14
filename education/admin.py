from django.contrib import admin
from .models import EducationCategory, EducationResource

@admin.register(EducationCategory)
class EducationCategoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'title', 'key', 'icon')
    list_display_links = ('title',)
    list_editable = ('order',)
    search_fields = ('title', 'description', 'key')

@admin.register(EducationResource)
class EducationResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_published', 'published_at')
    list_filter = ('category', 'is_published', 'published_at')
    search_fields = ('title', 'description', 'body')
    list_editable = ('is_published',)
    ordering = ('-published_at',)
