from django.contrib import admin
from .models import Page, VideoBulletin, VideoBulletinLead, VideoGenerationJob

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'updated_at')
    list_filter = ('is_published',)
    search_fields = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(VideoBulletin)
class VideoBulletinAdmin(admin.ModelAdmin):
    list_display = ('title', 'avatar', 'is_published', 'published_at', 'updated_at')
    list_filter = ('avatar', 'is_published')
    search_fields = ('title', 'summary', 'script')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(VideoBulletinLead)
class VideoBulletinLeadAdmin(admin.ModelAdmin):
    list_display = ('mobile', 'name', 'email', 'profession', 'bulletin', 'created_at')
    list_filter = ('profession', 'bulletin', 'created_at')
    search_fields = ('mobile', 'name', 'email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(VideoGenerationJob)
class VideoGenerationJobAdmin(admin.ModelAdmin):
    list_display = ('bulletin', 'status', 'progress', 'started_at', 'completed_at')
    list_filter = ('status', 'created_at')
    readonly_fields = ('task_id', 'error', 'output_file', 'started_at', 'completed_at', 'created_at', 'updated_at')
