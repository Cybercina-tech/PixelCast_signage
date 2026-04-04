from rest_framework import serializers

from .ai_service import get_blog_ai_settings, mask_api_key
from .models import BlogAISettings, BlogAIGenerationLog


class BlogAIGenerationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogAIGenerationLog
        fields = (
            'id',
            'created_at',
            'trigger',
            'status',
            'message',
            'requested_count',
            'created_count',
            'error_detail',
        )
        read_only_fields = fields


class BlogAISettingsReadSerializer(serializers.ModelSerializer):
    openai_api_key_masked = serializers.SerializerMethodField()

    class Meta:
        model = BlogAISettings
        fields = (
            'enabled',
            'model',
            'api_base_url',
            'system_prompt',
            'keyword_pool',
            'posts_per_run',
            'max_posts_per_day',
            'auto_publish',
            'updated_at',
            'openai_api_key_masked',
        )
        read_only_fields = fields

    def get_openai_api_key_masked(self, obj):
        return mask_api_key(obj.openai_api_key_encrypted or '')


class BlogAISettingsUpdateSerializer(serializers.Serializer):
    enabled = serializers.BooleanField(required=False)
    openai_api_key = serializers.CharField(required=False, allow_blank=True, write_only=True, max_length=512)
    model = serializers.CharField(required=False, allow_blank=False, max_length=128)
    api_base_url = serializers.URLField(required=False, max_length=512)
    system_prompt = serializers.CharField(required=False, allow_blank=True, max_length=16000)
    keyword_pool = serializers.CharField(required=False, allow_blank=True, max_length=32000)
    posts_per_run = serializers.IntegerField(required=False, min_value=1, max_value=20)
    max_posts_per_day = serializers.IntegerField(required=False, min_value=1, max_value=50)
    auto_publish = serializers.BooleanField(required=False)

    def validate_posts_per_run(self, v):
        return int(v)

    def validate_max_posts_per_day(self, v):
        return int(v)


class BlogAIGenerateSerializer(serializers.Serializer):
    count = serializers.IntegerField(required=False, default=1, min_value=1, max_value=10)
