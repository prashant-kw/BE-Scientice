from django.contrib import admin
from .models import Page, VideoBulletin, VideoBulletinLead, VideoGenerationJob, KeyHighlightItem

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'updated_at')
    list_filter = ('is_published',)
    search_fields = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(VideoBulletin)
class VideoBulletinAdmin(admin.ModelAdmin):
    list_display = ('title', 'avatar', 'event_title', 'parent_event', 'loop_start_clip', 'is_published', 'published_at', 'updated_at')
    list_filter = ('avatar', 'is_published')
    search_fields = ('title', 'summary', 'script', 'event_title')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(VideoBulletinLead)
class VideoBulletinLeadAdmin(admin.ModelAdmin):
    list_display = ('mobile', 'name', 'email', 'profession', 'bulletin', 'created_at')
    list_filter = ('profession', 'bulletin', 'created_at')
    search_fields = ('mobile', 'name', 'email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(VideoGenerationJob)
class VideoGenerationJobAdmin(admin.ModelAdmin):
    list_display = ('bulletin', 'task_id', 'status', 'progress', 'started_at', 'completed_at')
    list_filter = ('status', 'created_at')
    readonly_fields = ('task_id', 'error', 'output_file', 'started_at', 'completed_at', 'created_at', 'updated_at')


@admin.register(KeyHighlightItem)
class KeyHighlightItemAdmin(admin.ModelAdmin):
    list_display = ('number', 'category', 'title', 'is_published', 'order', 'created_at')
    list_filter = ('category', 'is_published')
    search_fields = ('title', 'summary')
