from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from saas_platform.permissions import IsDeveloper

from .constants import BLOG_POST_CORE_SELECT_FIELDS
from .db_compat import blog_post_table_has_ai_columns
from .models import BlogPost
from .serializers import (
    BlogPostPlatformSerializer,
    BlogPostPlatformSerializerNoAi,
    BlogPostPublicListSerializer,
    BlogPostPublicSerializer,
)


class BlogPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


def _published_qs():
    now = timezone.now()
    return (
        BlogPost.objects.filter(
            status=BlogPost.STATUS_PUBLISHED,
            published_at__isnull=False,
            published_at__lte=now,
        )
        .select_related('author')
        .only(*BLOG_POST_CORE_SELECT_FIELDS)
    )


class PublicBlogPostViewSet(viewsets.ReadOnlyModelViewSet):
    """Anonymous read-only access to published posts."""

    # Skip JWT/session auth: the SPA sends Bearer on all axios calls; validating it here adds DB work
    # and can surface 5xx (e.g. DB errors) on a route that must stay public and cache-friendly.
    authentication_classes = []
    permission_classes = [AllowAny]
    # Do not apply global/default filter backends — they can clone the queryset and drop .only().
    filter_backends = []
    pagination_class = BlogPagination
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'

    def get_queryset(self):
        return _published_qs().order_by('-published_at', '-created_at')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BlogPostPublicSerializer
        return BlogPostPublicListSerializer


class PlatformBlogPostViewSet(viewsets.ModelViewSet):
    """Full CRUD for Developer role (not gated by PLATFORM_SAAS_ENABLED)."""

    permission_classes = [IsAuthenticated, IsDeveloper]
    serializer_class = BlogPostPlatformSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']

    def get_serializer_class(self):
        if blog_post_table_has_ai_columns():
            return BlogPostPlatformSerializer
        return BlogPostPlatformSerializerNoAi

    def get_queryset(self):
        if blog_post_table_has_ai_columns():
            base = BlogPost.objects.all().select_related('author')
        else:
            base = BlogPost.objects.all().select_related('author').only(*BLOG_POST_CORE_SELECT_FIELDS)
        qs = base.order_by('-created_at')
        st = self.request.query_params.get('status')
        if st in (BlogPost.STATUS_DRAFT, BlogPost.STATUS_PUBLISHED):
            qs = qs.filter(status=st)
        q = self.request.query_params.get('search', '').strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(slug__icontains=q) | Q(excerpt__icontains=q))
        return qs

    @action(detail=True, methods=['post'], url_path='publish')
    def publish(self, request, pk=None):
        post = self.get_object()
        post.status = BlogPost.STATUS_PUBLISHED
        if not post.published_at:
            post.published_at = timezone.now()
        post.save()
        return Response(self.get_serializer(post).data)
