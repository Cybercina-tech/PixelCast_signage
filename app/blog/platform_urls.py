from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .ai_views import BlogAIGenerateView, BlogAILogsView, BlogAISettingsView
from .views import PlatformBlogPostViewSet

router = DefaultRouter()
router.register(r'posts', PlatformBlogPostViewSet, basename='platform-blog-post')

urlpatterns = [
    path('ai/settings/', BlogAISettingsView.as_view(), name='platform-blog-ai-settings'),
    path('ai/generate/', BlogAIGenerateView.as_view(), name='platform-blog-ai-generate'),
    path('ai/logs/', BlogAILogsView.as_view(), name='platform-blog-ai-logs'),
    path('', include(router.urls)),
]
