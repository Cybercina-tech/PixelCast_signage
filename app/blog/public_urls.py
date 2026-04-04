from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PublicBlogPostViewSet

router = DefaultRouter()
router.register(r'posts', PublicBlogPostViewSet, basename='public-blog-post')

urlpatterns = [
    path('', include(router.urls)),
]
