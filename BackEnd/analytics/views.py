"""
Analytics Dashboard API views.

Provides REST API endpoints for fetching analytics data with proper
authentication, authorization, and input validation.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.cache import cache
from typing import Optional

from accounts.permissions import RolePermissions
from .services import (
    ScreenAnalyticsService,
    CommandAnalyticsService,
    ContentAnalyticsService,
    TemplateAnalyticsService,
    ActivityAnalyticsService,
)
from .validators import (
    validate_date_range,
    validate_uuid_list,
    validate_pagination,
    validate_period,
)
from .serializers import (
    ScreenStatisticsSerializer,
    ScreenDetailSerializer,
    CommandStatisticsSerializer,
    ContentStatisticsSerializer,
    TemplateStatisticsSerializer,
    ActivityTrendsSerializer,
)


def check_analytics_permission(request):
    """
    Check if user has permission to access analytics.
    
    Only Manager and Admin roles can access analytics.
    
    Raises:
        PermissionDenied: If user doesn't have permission
    """
    if not RolePermissions.can_manage_own(request.user):
        from rest_framework.exceptions import PermissionDenied
        raise PermissionDenied("Manager or Admin role required to access analytics")


def get_rate_limit_key(user_id: int, endpoint: str) -> str:
    """Generate cache key for rate limiting."""
    return f"analytics_rate_limit:{user_id}:{endpoint}"


def check_rate_limit(user_id: int, endpoint: str, max_requests: int = 100, window_seconds: int = 60):
    """
    Check if user has exceeded rate limit for an endpoint.
    
    Args:
        user_id: User ID
        endpoint: Endpoint name
        max_requests: Maximum requests per window
        window_seconds: Time window in seconds
        
    Raises:
        ValidationError: If rate limit exceeded
    """
    cache_key = get_rate_limit_key(user_id, endpoint)
    current_count = cache.get(cache_key, 0)
    
    if current_count >= max_requests:
        raise ValidationError(
            f"Rate limit exceeded. Maximum {max_requests} requests per {window_seconds} seconds."
        )
    
    cache.set(cache_key, current_count + 1, window_seconds)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def screen_statistics(request):
    """
    GET /api/analytics/screens/
    
    Get aggregated screen statistics including online/offline status,
    CPU, memory, and latency averages.
    
    Query Parameters:
        - screen_ids (optional): Comma-separated list of screen UUIDs
        - start_date (optional): Start date (YYYY-MM-DD)
        - end_date (optional): End date (YYYY-MM-DD)
        
    Returns:
        JSON response with screen statistics
    """
    try:
        # Check permissions
        check_analytics_permission(request)
        
        # Rate limiting
        check_rate_limit(request.user.id, 'screen_statistics')
        
        # Parse query parameters
        screen_ids = None
        if 'screen_ids' in request.query_params:
            screen_id_list = request.query_params['screen_ids'].split(',')
            screen_ids = validate_uuid_list([s.strip() for s in screen_id_list], "screen_ids")
        
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        start_date, end_date = validate_date_range(start_date_str, end_date_str)
        
        # Get statistics
        stats = ScreenAnalyticsService.get_screen_statistics(
            screen_ids=screen_ids,
            start_date=start_date,
            end_date=end_date
        )
        
        return Response({
            'status': 'success',
            'data': stats,
            'timestamp': timezone.now().isoformat(),
        }, status=status.HTTP_200_OK)
        
    except ValidationError as e:
        return Response({
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'status': 'error',
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def screen_detail(request, screen_id):
    """
    GET /api/analytics/screens/{screen_id}/
    
    Get detailed analytics for a specific screen.
    
    Returns:
        JSON response with detailed screen analytics
    """
    try:
        # Check permissions
        check_analytics_permission(request)
        
        # Rate limiting
        check_rate_limit(request.user.id, 'screen_detail')
        
        # Validate screen_id
        validate_uuid_list([screen_id], "screen_id")
        
        # Get detailed statistics
        details = ScreenAnalyticsService.get_screen_details(screen_id)
        
        if details is None:
            return Response({
                'status': 'error',
                'error': 'Screen not found',
                'timestamp': timezone.now().isoformat(),
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'status': 'success',
            'data': details,
            'timestamp': timezone.now().isoformat(),
        }, status=status.HTTP_200_OK)
        
    except ValidationError as e:
        return Response({
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'status': 'error',
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def command_statistics(request):
    """
    GET /api/analytics/commands/
    
    Get command statistics including queued, executed, failed commands
    per time period.
    
    Query Parameters:
        - screen_ids (optional): Comma-separated list of screen UUIDs
        - start_date (optional): Start date (YYYY-MM-DD)
        - end_date (optional): End date (YYYY-MM-DD)
        - period (optional): Aggregation period ('day', 'week', 'month')
        
    Returns:
        JSON response with command statistics
    """
    try:
        # Check permissions
        check_analytics_permission(request)
        
        # Rate limiting
        check_rate_limit(request.user.id, 'command_statistics')
        
        # Parse query parameters
        screen_ids = None
        if 'screen_ids' in request.query_params:
            screen_id_list = request.query_params['screen_ids'].split(',')
            screen_ids = validate_uuid_list([s.strip() for s in screen_id_list], "screen_ids")
        
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        start_date, end_date = validate_date_range(start_date_str, end_date_str)
        
        period = validate_period(request.query_params.get('period'))
        
        # Get statistics
        stats = CommandAnalyticsService.get_command_statistics(
            screen_ids=screen_ids,
            start_date=start_date,
            end_date=end_date,
            period=period
        )
        
        return Response({
            'status': 'success',
            'data': stats,
            'timestamp': timezone.now().isoformat(),
        }, status=status.HTTP_200_OK)
        
    except ValidationError as e:
        return Response({
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'status': 'error',
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def content_statistics(request):
    """
    GET /api/analytics/content/
    
    Get content download analytics including progress, error rates,
    and type distribution.
    
    Query Parameters:
        - start_date (optional): Start date (YYYY-MM-DD)
        - end_date (optional): End date (YYYY-MM-DD)
        
    Returns:
        JSON response with content statistics
    """
    try:
        # Check permissions
        check_analytics_permission(request)
        
        # Rate limiting
        check_rate_limit(request.user.id, 'content_statistics')
        
        # Parse query parameters
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        start_date, end_date = validate_date_range(start_date_str, end_date_str)
        
        # Get statistics
        stats = ContentAnalyticsService.get_content_statistics(
            start_date=start_date,
            end_date=end_date
        )
        
        return Response({
            'status': 'success',
            'data': stats,
            'timestamp': timezone.now().isoformat(),
        }, status=status.HTTP_200_OK)
        
    except ValidationError as e:
        return Response({
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'status': 'error',
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def template_statistics(request):
    """
    GET /api/analytics/templates/
    
    Get template usage metrics including active templates per screen
    and frequency of activation.
    
    Query Parameters:
        - start_date (optional): Start date (YYYY-MM-DD)
        - end_date (optional): End date (YYYY-MM-DD)
        
    Returns:
        JSON response with template statistics
    """
    try:
        # Check permissions
        check_analytics_permission(request)
        
        # Rate limiting
        check_rate_limit(request.user.id, 'template_statistics')
        
        # Parse query parameters
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        start_date, end_date = validate_date_range(start_date_str, end_date_str)
        
        # Get statistics
        stats = TemplateAnalyticsService.get_template_statistics(
            start_date=start_date,
            end_date=end_date
        )
        
        return Response({
            'status': 'success',
            'data': stats,
            'timestamp': timezone.now().isoformat(),
        }, status=status.HTTP_200_OK)
        
    except ValidationError as e:
        return Response({
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'status': 'error',
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def activity_trends(request):
    """
    GET /api/analytics/activity/
    
    Get activity trends including daily/weekly/monthly summaries
    of operations.
    
    Query Parameters:
        - period (optional): Aggregation period ('day', 'week', 'month')
        - days (optional): Number of days to look back (default: 30, max: 365)
        
    Returns:
        JSON response with activity trends
    """
    try:
        # Check permissions
        check_analytics_permission(request)
        
        # Rate limiting
        check_rate_limit(request.user.id, 'activity_trends')
        
        # Parse query parameters
        period = validate_period(request.query_params.get('period'))
        
        days = 30
        if 'days' in request.query_params:
            try:
                days = int(request.query_params['days'])
                if days < 1 or days > 365:
                    raise ValidationError("days must be between 1 and 365")
            except ValueError:
                raise ValidationError("days must be a valid integer")
        
        # Get trends
        trends = ActivityAnalyticsService.get_activity_trends(
            period=period,
            days=days
        )
        
        return Response({
            'status': 'success',
            'data': trends,
            'timestamp': timezone.now().isoformat(),
        }, status=status.HTTP_200_OK)
        
    except ValidationError as e:
        return Response({
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'status': 'error',
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
