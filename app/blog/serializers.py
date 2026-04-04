from django.core.exceptions import ObjectDoesNotExist
from django.utils.text import slugify
from rest_framework import serializers

from .models import BlogPost

_PLATFORM_FIELDS_NO_AI = (
    'id',
    'title',
    'slug',
    'excerpt',
    'body',
    'status',
    'published_at',
    'featured_image_url',
    'meta_title',
    'meta_description',
    'author',
    'created_at',
    'updated_at',
)

_PLATFORM_EXTRA_KWARGS = {
    'slug': {'required': False, 'allow_blank': True},
    'excerpt': {'required': False, 'allow_blank': True},
    'body': {'required': False, 'allow_blank': True},
    'featured_image_url': {'required': False, 'allow_blank': True},
    'meta_title': {'required': False, 'allow_blank': True},
    'meta_description': {'required': False, 'allow_blank': True},
    'published_at': {'required': False, 'allow_null': True},
    'author': {'required': False, 'allow_null': True},
}


def _author_display_name(post):
    """Safe author label; broken FK (orphan author_id) must not 500 the API."""
    if not post.author_id:
        return None
    try:
        u = post.author
    except ObjectDoesNotExist:
        return None
    return (u.full_name or u.username or u.email or '').strip() or None


class BlogPostPublicSerializer(serializers.ModelSerializer):
    """Published posts for anonymous API."""

    author_name = serializers.SerializerMethodField()
    reading_time_minutes = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = (
            'id',
            'title',
            'slug',
            'excerpt',
            'body',
            'featured_image_url',
            'published_at',
            'meta_title',
            'meta_description',
            'author_name',
            'reading_time_minutes',
            'updated_at',
        )
        read_only_fields = fields

    def get_author_name(self, obj):
        return _author_display_name(obj)

    def get_reading_time_minutes(self, obj):
        text = f'{obj.title} {obj.excerpt} {obj.body}'
        words = len(text.split())
        return max(1, (words + 199) // 200)


class BlogPostPublicListSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = (
            'id',
            'title',
            'slug',
            'excerpt',
            'featured_image_url',
            'published_at',
            'author_name',
        )
        read_only_fields = fields

    def get_author_name(self, obj):
        return _author_display_name(obj)


class BlogPostPlatformSerializerMixin:
    """Shared slug validation and create; slug check uses .only() so missing AI columns do not break."""

    def validate_slug(self, value):
        value = (value or '').strip()
        if not value:
            return value
        qs = BlogPost.objects.all().only('id', 'slug')
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        candidate = slugify(value)[:280]
        if qs.filter(slug=candidate).exists():
            raise serializers.ValidationError('A post with this slug already exists.')
        return candidate

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated and validated_data.get('author') is None:
            validated_data['author'] = request.user
        return super().create(validated_data)


class BlogPostPlatformSerializerNoAi(BlogPostPlatformSerializerMixin, serializers.ModelSerializer):
    """Platform API when blog.0003 (AI columns) is not applied yet."""

    class Meta:
        model = BlogPost
        fields = _PLATFORM_FIELDS_NO_AI
        read_only_fields = ('id', 'created_at', 'updated_at')
        extra_kwargs = _PLATFORM_EXTRA_KWARGS


class BlogPostPlatformSerializer(BlogPostPlatformSerializerMixin, serializers.ModelSerializer):
    ai_log = serializers.UUIDField(source='ai_log_id', read_only=True, allow_null=True)

    class Meta:
        model = BlogPost
        fields = _PLATFORM_FIELDS_NO_AI + ('ai_generated', 'ai_log')
        read_only_fields = ('id', 'created_at', 'updated_at', 'ai_generated', 'ai_log')
        extra_kwargs = _PLATFORM_EXTRA_KWARGS
