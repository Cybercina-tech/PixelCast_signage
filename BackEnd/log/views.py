from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta, datetime

from .models import ScreenStatusLog, ContentDownloadLog, CommandExecutionLog
from .serializers import (
    ScreenStatusLogSerializer, ContentDownloadLogSerializer,
    CommandExecutionLogSerializer, LogSummarySerializer
)


class LogPagination(PageNumberPagination):
    """Custom pagination for log endpoints - 50 items per page"""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000


def parse_date_param(date_string):
    """
    Helper function to parse date parameters.
    Supports ISO format and YYYY-MM-DD format.
    
    Args:
        date_string: Date string to parse
        
    Returns:
        datetime: Parsed datetime object or None
    """
    if not date_string:
        return None
    
    try:
        # Try ISO format first
        if 'T' in date_string or 'Z' in date_string:
            date_string = date_string.replace('Z', '+00:00')
            return timezone.datetime.fromisoformat(date_string)
        else:
            # Try YYYY-MM-DD format
            parsed = timezone.datetime.strptime(date_string, '%Y-%m-%d')
            return timezone.make_aware(parsed)
    except (ValueError, AttributeError):
        return None


class ScreenStatusLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for ScreenStatusLog model.
    Provides read-only access with role-based permissions, filtering, and summary statistics.
    
    Endpoints:
    - GET /api/logs/screen-status/ - List all screen status logs
    - GET /api/logs/screen-status/{id}/ - Retrieve specific log
    - GET /api/logs/screen-status/summary/ - Get summary statistics
    
    Query Parameters:
    - screen_id: Filter by screen UUID
    - status: Filter by status (online/offline)
    - start_date: Filter from date (ISO or YYYY-MM-DD)
    - end_date: Filter to date (ISO or YYYY-MM-DD)
    - page: Page number for pagination
    - page_size: Items per page (max 1000)
    """
    queryset = ScreenStatusLog.objects.select_related('screen').all()
    serializer_class = ScreenStatusLogSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LogPagination
    lookup_field = 'id'
    
    def get_queryset(self):
        """
        Filter queryset based on user permissions and query parameters.
        Ensures no duplicates and optimizes queries.
        """
        queryset = super().get_queryset()
        user = self.request.user
        
        # Only Admin and SuperAdmin can access logs
        if not user.has_full_access():
            raise PermissionDenied("You do not have permission to view logs. Admin or SuperAdmin role required.")
        
        # Filter by screen if provided
        screen_id = self.request.query_params.get('screen_id')
        if screen_id:
            try:
                queryset = queryset.filter(screen_id=screen_id)
            except ValueError:
                # Invalid UUID format
                queryset = queryset.none()
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            valid_statuses = [choice[0] for choice in ScreenStatusLog.STATUS_CHOICES]
            if status_filter in valid_statuses:
                queryset = queryset.filter(status=status_filter)
        
        # Filter by date range if provided
        start_date = parse_date_param(self.request.query_params.get('start_date'))
        end_date = parse_date_param(self.request.query_params.get('end_date'))
        
        if start_date:
            queryset = queryset.filter(recorded_at__gte=start_date)
        if end_date:
            # Include entire end date
            end_date = end_date + timedelta(days=1)
            queryset = queryset.filter(recorded_at__lt=end_date)
        
        # Ensure no duplicates and order by recorded_at descending
        queryset = queryset.distinct().order_by('-recorded_at', '-id')
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        GET /api/logs/screen-status/summary/
        Get summary statistics for screen status logs.
        
        Query Parameters:
        - screen_id: Filter by screen UUID
        - start_date: Filter from date (ISO or YYYY-MM-DD)
        - end_date: Filter to date (ISO or YYYY-MM-DD)
        """
        if not request.user.has_full_access():
            raise PermissionDenied("You do not have permission to view log summaries. Admin or SuperAdmin role required.")
        
        screen_id = request.query_params.get('screen_id')
        start_date = parse_date_param(request.query_params.get('start_date'))
        end_date = parse_date_param(request.query_params.get('end_date'))
        
        # Handle end_date to include entire day
        if end_date:
            end_date = end_date + timedelta(days=1)
        
        screen = None
        if screen_id:
            from signage.models import Screen
            try:
                screen = Screen.objects.get(id=screen_id)
            except Screen.DoesNotExist:
                return Response(
                    {'error': 'Screen not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        stats = ScreenStatusLog.get_summary_stats(
            screen=screen,
            start_date=start_date,
            end_date=end_date
        )
        
        serializer = LogSummarySerializer(stats)
        return Response({
            'status': 'success',
            'summary': serializer.data
        }, status=status.HTTP_200_OK)


class ContentDownloadLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for ContentDownloadLog model.
    Provides read-only access with role-based permissions, filtering, and summary statistics.
    
    Endpoints:
    - GET /api/logs/content-download/ - List all content download logs
    - GET /api/logs/content-download/{id}/ - Retrieve specific log
    - GET /api/logs/content-download/summary/ - Get summary statistics
    
    Query Parameters:
    - content_id: Filter by content UUID
    - screen_id: Filter by screen UUID
    - status: Filter by status (pending/success/failed)
    - start_date: Filter from date (ISO or YYYY-MM-DD) - filters by created_at
    - end_date: Filter to date (ISO or YYYY-MM-DD) - filters by created_at
    - downloaded_from: Filter downloads from date - filters by downloaded_at
    - downloaded_to: Filter downloads to date - filters by downloaded_at
    - page: Page number for pagination
    - page_size: Items per page (max 1000)
    """
    queryset = ContentDownloadLog.objects.select_related('content', 'screen').all()
    serializer_class = ContentDownloadLogSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LogPagination
    lookup_field = 'id'
    
    def get_queryset(self):
        """
        Filter queryset based on user permissions and query parameters.
        Ensures no duplicates and optimizes queries.
        """
        queryset = super().get_queryset()
        user = self.request.user
        
        # Only Admin and SuperAdmin can access logs
        if not user.has_full_access():
            raise PermissionDenied("You do not have permission to view logs. Admin or SuperAdmin role required.")
        
        # Filter by content if provided
        content_id = self.request.query_params.get('content_id')
        if content_id:
            try:
                queryset = queryset.filter(content_id=content_id)
            except ValueError:
                queryset = queryset.none()
        
        # Filter by screen if provided
        screen_id = self.request.query_params.get('screen_id')
        if screen_id:
            try:
                queryset = queryset.filter(screen_id=screen_id)
            except ValueError:
                queryset = queryset.none()
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            valid_statuses = [choice[0] for choice in ContentDownloadLog.STATUS_CHOICES]
            if status_filter in valid_statuses:
                queryset = queryset.filter(status=status_filter)
        
        # Filter by created_at date range if provided
        start_date = parse_date_param(self.request.query_params.get('start_date'))
        end_date = parse_date_param(self.request.query_params.get('end_date'))
        
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            end_date = end_date + timedelta(days=1)
            queryset = queryset.filter(created_at__lt=end_date)
        
        # Filter by downloaded_at date range if provided
        downloaded_from = parse_date_param(self.request.query_params.get('downloaded_from'))
        downloaded_to = parse_date_param(self.request.query_params.get('downloaded_to'))
        
        if downloaded_from:
            queryset = queryset.filter(downloaded_at__gte=downloaded_from)
        if downloaded_to:
            downloaded_to = downloaded_to + timedelta(days=1)
            queryset = queryset.filter(downloaded_at__lt=downloaded_to)
        
        # Ensure no duplicates and order by created_at descending
        queryset = queryset.distinct().order_by('-created_at', '-id')
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        GET /api/logs/content-download/summary/
        Get summary statistics for content download logs.
        
        Query Parameters:
        - content_id: Filter by content UUID
        - screen_id: Filter by screen UUID
        - start_date: Filter from date (ISO or YYYY-MM-DD)
        - end_date: Filter to date (ISO or YYYY-MM-DD)
        """
        if not request.user.has_full_access():
            raise PermissionDenied("You do not have permission to view log summaries. Admin or SuperAdmin role required.")
        
        content_id = request.query_params.get('content_id')
        screen_id = request.query_params.get('screen_id')
        start_date = parse_date_param(request.query_params.get('start_date'))
        end_date = parse_date_param(request.query_params.get('end_date'))
        
        # Handle end_date to include entire day
        if end_date:
            end_date = end_date + timedelta(days=1)
        
        content = None
        if content_id:
            from templates.models import Content
            try:
                content = Content.objects.get(id=content_id)
            except Content.DoesNotExist:
                return Response(
                    {'error': 'Content not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        screen = None
        if screen_id:
            from signage.models import Screen
            try:
                screen = Screen.objects.get(id=screen_id)
            except Screen.DoesNotExist:
                return Response(
                    {'error': 'Screen not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        stats = ContentDownloadLog.get_summary_stats(
            content=content,
            screen=screen,
            start_date=start_date,
            end_date=end_date
        )
        
        serializer = LogSummarySerializer(stats)
        return Response({
            'status': 'success',
            'summary': serializer.data
        }, status=status.HTTP_200_OK)


class CommandExecutionLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for CommandExecutionLog model.
    Provides read-only access with role-based permissions, filtering, and summary statistics.
    
    Endpoints:
    - GET /api/logs/command-execution/ - List all command execution logs
    - GET /api/logs/command-execution/{id}/ - Retrieve specific log
    - GET /api/logs/command-execution/summary/ - Get summary statistics
    
    Query Parameters:
    - command_id: Filter by command UUID
    - screen_id: Filter by screen UUID
    - status: Filter by status (pending/running/done/failed)
    - start_date: Filter from date (ISO or YYYY-MM-DD) - filters by created_at
    - end_date: Filter to date (ISO or YYYY-MM-DD) - filters by created_at
    - started_from: Filter executions started from date - filters by started_at
    - started_to: Filter executions started to date - filters by started_at
    - finished_from: Filter executions finished from date - filters by finished_at
    - finished_to: Filter executions finished to date - filters by finished_at
    - page: Page number for pagination
    - page_size: Items per page (max 1000)
    """
    queryset = CommandExecutionLog.objects.select_related('command', 'screen').all()
    serializer_class = CommandExecutionLogSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LogPagination
    lookup_field = 'id'
    
    def get_queryset(self):
        """
        Filter queryset based on user permissions and query parameters.
        Ensures no duplicates and optimizes queries.
        """
        queryset = super().get_queryset()
        user = self.request.user
        
        # Only Admin and SuperAdmin can access logs
        if not user.has_full_access():
            raise PermissionDenied("You do not have permission to view logs. Admin or SuperAdmin role required.")
        
        # Filter by command if provided
        command_id = self.request.query_params.get('command_id')
        if command_id:
            try:
                queryset = queryset.filter(command_id=command_id)
            except ValueError:
                queryset = queryset.none()
        
        # Filter by screen if provided
        screen_id = self.request.query_params.get('screen_id')
        if screen_id:
            try:
                queryset = queryset.filter(screen_id=screen_id)
            except ValueError:
                queryset = queryset.none()
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            valid_statuses = [choice[0] for choice in CommandExecutionLog.STATUS_CHOICES]
            if status_filter in valid_statuses:
                queryset = queryset.filter(status=status_filter)
        
        # Filter by created_at date range if provided
        start_date = parse_date_param(self.request.query_params.get('start_date'))
        end_date = parse_date_param(self.request.query_params.get('end_date'))
        
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            end_date = end_date + timedelta(days=1)
            queryset = queryset.filter(created_at__lt=end_date)
        
        # Filter by started_at date range if provided
        started_from = parse_date_param(self.request.query_params.get('started_from'))
        started_to = parse_date_param(self.request.query_params.get('started_to'))
        
        if started_from:
            queryset = queryset.filter(started_at__gte=started_from)
        if started_to:
            started_to = started_to + timedelta(days=1)
            queryset = queryset.filter(started_at__lt=started_to)
        
        # Filter by finished_at date range if provided
        finished_from = parse_date_param(self.request.query_params.get('finished_from'))
        finished_to = parse_date_param(self.request.query_params.get('finished_to'))
        
        if finished_from:
            queryset = queryset.filter(finished_at__gte=finished_from)
        if finished_to:
            finished_to = finished_to + timedelta(days=1)
            queryset = queryset.filter(finished_at__lt=finished_to)
        
        # Ensure no duplicates and order by created_at descending
        queryset = queryset.distinct().order_by('-created_at', '-id')
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        GET /api/logs/command-execution/summary/
        Get summary statistics for command execution logs.
        
        Query Parameters:
        - command_id: Filter by command UUID
        - screen_id: Filter by screen UUID
        - start_date: Filter from date (ISO or YYYY-MM-DD)
        - end_date: Filter to date (ISO or YYYY-MM-DD)
        """
        if not request.user.has_full_access():
            raise PermissionDenied("You do not have permission to view log summaries. Admin or SuperAdmin role required.")
        
        command_id = request.query_params.get('command_id')
        screen_id = request.query_params.get('screen_id')
        start_date = parse_date_param(request.query_params.get('start_date'))
        end_date = parse_date_param(request.query_params.get('end_date'))
        
        # Handle end_date to include entire day
        if end_date:
            end_date = end_date + timedelta(days=1)
        
        command = None
        if command_id:
            from commands.models import Command
            try:
                command = Command.objects.get(id=command_id)
            except Command.DoesNotExist:
                return Response(
                    {'error': 'Command not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        screen = None
        if screen_id:
            from signage.models import Screen
            try:
                screen = Screen.objects.get(id=screen_id)
            except Screen.DoesNotExist:
                return Response(
                    {'error': 'Screen not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        stats = CommandExecutionLog.get_summary_stats(
            command=command,
            screen=screen,
            start_date=start_date,
            end_date=end_date
        )
        
        serializer = LogSummarySerializer(stats)
        return Response({
            'status': 'success',
            'summary': serializer.data
        }, status=status.HTTP_200_OK)
