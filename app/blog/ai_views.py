from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from saas_platform.permissions import IsDeveloper

from .ai_serializers import (
    BlogAIGenerateSerializer,
    BlogAIGenerationLogSerializer,
    BlogAISettingsReadSerializer,
    BlogAISettingsUpdateSerializer,
)
from .ai_service import apply_api_key_if_provided, get_blog_ai_settings, run_generation
from .models import BlogAIGenerationLog


class BlogAISettingsView(APIView):
    permission_classes = [IsAuthenticated, IsDeveloper]

    def get(self, request):
        obj = get_blog_ai_settings()
        return Response(BlogAISettingsReadSerializer(obj).data)

    def patch(self, request):
        obj = get_blog_ai_settings()
        ser = BlogAISettingsUpdateSerializer(data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        if 'enabled' in data:
            obj.enabled = data['enabled']
        if 'model' in data:
            obj.model = data['model'].strip()[:128]
        if 'api_base_url' in data:
            obj.api_base_url = data['api_base_url'].strip()[:512]
        if 'system_prompt' in data:
            obj.system_prompt = data['system_prompt'][:16000]
        if 'keyword_pool' in data:
            obj.keyword_pool = data['keyword_pool'][:32000]
        if 'posts_per_run' in data:
            obj.posts_per_run = data['posts_per_run']
        if 'max_posts_per_day' in data:
            obj.max_posts_per_day = data['max_posts_per_day']
        if 'auto_publish' in data:
            obj.auto_publish = data['auto_publish']

        apply_api_key_if_provided(obj, data.get('openai_api_key'))

        obj.save()
        return Response(BlogAISettingsReadSerializer(get_blog_ai_settings()).data)


class BlogAIGenerateView(APIView):
    permission_classes = [IsAuthenticated, IsDeveloper]

    def post(self, request):
        ser = BlogAIGenerateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        count = ser.validated_data['count']
        log, posts = run_generation(
            requested_count=count,
            trigger=BlogAIGenerationLog.TRIGGER_MANUAL,
            user=request.user,
        )
        return Response(
            {
                'log': BlogAIGenerationLogSerializer(log).data,
                'post_ids': [str(p.id) for p in posts],
            },
            status=status.HTTP_200_OK,
        )


class BlogAILogsView(APIView):
    permission_classes = [IsAuthenticated, IsDeveloper]

    def get(self, request):
        limit = int(request.query_params.get('limit', 30))
        limit = max(1, min(limit, 100))
        qs = BlogAIGenerationLog.objects.all().order_by('-created_at')[:limit]
        return Response(BlogAIGenerationLogSerializer(qs, many=True).data)
