from django.contrib import admin

from .models import BlogAIGenerationLog, BlogAISettings, BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'status', 'published_at', 'author', 'ai_generated', 'updated_at')
    list_filter = ('status', 'ai_generated')
    search_fields = ('title', 'slug', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('id', 'created_at', 'updated_at', 'ai_log')


@admin.register(BlogAISettings)
class BlogAISettingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'enabled', 'model', 'posts_per_run', 'max_posts_per_day', 'updated_at')
    readonly_fields = ('updated_at',)


@admin.register(BlogAIGenerationLog)
class BlogAIGenerationLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'trigger', 'status', 'created_count', 'requested_count', 'message')
    list_filter = ('status', 'trigger')
    readonly_fields = ('id', 'created_at')
