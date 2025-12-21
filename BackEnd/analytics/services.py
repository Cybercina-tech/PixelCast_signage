"""
Analytics services for aggregating and calculating metrics.

Provides services for screens, commands, content, templates, and activity analytics.
"""
from django.db.models import (
    Q, Count, Avg, Max, Min, Sum, F, Case, When, IntegerField,
    FloatField, DateTimeField, Value, CharField
)
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta, datetime
from typing import Dict, List, Optional, Any
from decimal import Decimal

from signage.models import Screen
from commands.models import Command
from templates.models import Content, Template, Schedule
from log.models import (
    ScreenStatusLog, CommandExecutionLog, ContentDownloadLog
)
from accounts.models import User


class ScreenAnalyticsService:
    """Service for screen health and status analytics."""
    
    CACHE_TIMEOUT = 300  # 5 minutes
    
    @staticmethod
    def get_screen_statistics(
        screen_ids: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get aggregated screen statistics.
        
        Args:
            screen_ids: Optional list of screen IDs to filter by
            start_date: Optional start date for time range
            end_date: Optional end date for time range
            
        Returns:
            Dictionary with screen statistics
        """
        # Base queryset
        screens = Screen.objects.all()
        
        if screen_ids:
            screens = screens.filter(id__in=screen_ids)
        
        # Get online/offline counts
        total_screens = screens.count()
        online_count = screens.filter(is_online=True).count()
        offline_count = total_screens - online_count
        
        # Get recent status logs for metrics
        status_logs = ScreenStatusLog.objects.all()
        if screen_ids:
            status_logs = status_logs.filter(screen_id__in=screen_ids)
        if start_date:
            status_logs = status_logs.filter(recorded_at__gte=start_date)
        if end_date:
            status_logs = status_logs.filter(recorded_at__lte=end_date)
        
        # Get most recent status for each screen
        recent_logs = status_logs.order_by('screen_id', '-recorded_at').distinct('screen_id')
        
        # Aggregate metrics from recent logs
        if recent_logs.exists():
            metrics = recent_logs.aggregate(
                avg_cpu=Avg('cpu_usage'),
                avg_memory=Avg('memory_usage'),
                avg_latency=Avg('heartbeat_latency'),
                max_cpu=Max('cpu_usage'),
                max_memory=Max('memory_usage'),
                max_latency=Max('heartbeat_latency'),
                min_latency=Min('heartbeat_latency'),
            )
        else:
            metrics = {
                'avg_cpu': None,
                'avg_memory': None,
                'avg_latency': None,
                'max_cpu': None,
                'max_memory': None,
                'max_latency': None,
                'min_latency': None,
            }
        
        # Get screens by status breakdown
        status_breakdown = {
            'online': online_count,
            'offline': offline_count,
            'total': total_screens
        }
        
        # Calculate health score (percentage of online screens)
        health_score = (online_count / total_screens * 100) if total_screens > 0 else 0
        
        return {
            'total_screens': total_screens,
            'status_breakdown': status_breakdown,
            'health_metrics': {
                'avg_cpu_usage': round(float(metrics['avg_cpu']), 2) if metrics['avg_cpu'] else None,
                'avg_memory_usage': round(float(metrics['avg_memory']), 2) if metrics['avg_memory'] else None,
                'avg_latency_ms': round(float(metrics['avg_latency']), 2) if metrics['avg_latency'] else None,
                'max_cpu_usage': round(float(metrics['max_cpu']), 2) if metrics['max_cpu'] else None,
                'max_memory_usage': round(float(metrics['max_memory']), 2) if metrics['max_memory'] else None,
                'max_latency_ms': round(float(metrics['max_latency']), 2) if metrics['max_latency'] else None,
                'min_latency_ms': round(float(metrics['min_latency']), 2) if metrics['min_latency'] else None,
            },
            'health_score': round(health_score, 2),
            'period': {
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None,
            }
        }
    
    @staticmethod
    def get_screen_details(screen_id: str) -> Dict[str, Any]:
        """
        Get detailed analytics for a specific screen.
        
        Args:
            screen_id: UUID of the screen
            
        Returns:
            Dictionary with detailed screen analytics
        """
        try:
            screen = Screen.objects.get(id=screen_id)
        except Screen.DoesNotExist:
            return None
        
        # Get recent status logs (last 100)
        recent_logs = ScreenStatusLog.objects.filter(
            screen=screen
        ).order_by('-recorded_at')[:100]
        
        # Calculate averages from recent logs
        if recent_logs.exists():
            recent_metrics = recent_logs.aggregate(
                avg_cpu=Avg('cpu_usage'),
                avg_memory=Avg('memory_usage'),
                avg_latency=Avg('heartbeat_latency'),
            )
        else:
            recent_metrics = {
                'avg_cpu': None,
                'avg_memory': None,
                'avg_latency': None,
            }
        
        # Get command statistics
        commands = Command.objects.filter(screen=screen)
        command_stats = commands.aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(status='pending')),
            executing=Count('id', filter=Q(status='executing')),
            done=Count('id', filter=Q(status='done')),
            failed=Count('id', filter=Q(status='failed')),
        )
        
        # Get last heartbeat age
        last_heartbeat_age = None
        if screen.last_heartbeat_at:
            delta = timezone.now() - screen.last_heartbeat_at
            last_heartbeat_age = int(delta.total_seconds())
        
        return {
            'screen_id': str(screen.id),
            'screen_name': screen.name,
            'device_id': screen.device_id,
            'is_online': screen.is_online,
            'current_metrics': {
                'cpu_usage': screen.status_logs.first().cpu_usage if screen.status_logs.exists() else None,
                'memory_usage': screen.status_logs.first().memory_usage if screen.status_logs.exists() else None,
                'latency_ms': screen.status_logs.first().heartbeat_latency if screen.status_logs.exists() else None,
            },
            'recent_averages': {
                'avg_cpu_usage': round(float(recent_metrics['avg_cpu']), 2) if recent_metrics['avg_cpu'] else None,
                'avg_memory_usage': round(float(recent_metrics['avg_memory']), 2) if recent_metrics['avg_memory'] else None,
                'avg_latency_ms': round(float(recent_metrics['avg_latency']), 2) if recent_metrics['avg_latency'] else None,
            },
            'status': {
                'last_heartbeat_at': screen.last_heartbeat_at.isoformat() if screen.last_heartbeat_at else None,
                'last_heartbeat_age_seconds': last_heartbeat_age,
                'is_busy': screen.is_busy,
                'app_version': screen.app_version,
                'os_version': screen.os_version,
            },
            'command_statistics': {
                'total': command_stats['total'],
                'pending': command_stats['pending'],
                'executing': command_stats['executing'],
                'done': command_stats['done'],
                'failed': command_stats['failed'],
            },
            'active_template': {
                'template_id': str(screen.active_template.id) if screen.active_template else None,
                'template_name': screen.active_template.name if screen.active_template else None,
            } if screen.active_template else None,
        }


class CommandAnalyticsService:
    """Service for command statistics analytics."""
    
    @staticmethod
    def get_command_statistics(
        screen_ids: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        period: str = 'day'
    ) -> Dict[str, Any]:
        """
        Get aggregated command statistics.
        
        Args:
            screen_ids: Optional list of screen IDs to filter by
            start_date: Optional start date for time range
            end_date: Optional end date for time range
            period: Aggregation period ('day', 'week', 'month')
            
        Returns:
            Dictionary with command statistics
        """
        commands = Command.objects.all()
        
        if screen_ids:
            commands = commands.filter(screen_id__in=screen_ids)
        if start_date:
            commands = commands.filter(created_at__gte=start_date)
        if end_date:
            commands = commands.filter(created_at__lte=end_date)
        
        # Overall statistics
        overall_stats = commands.aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(status='pending')),
            executing=Count('id', filter=Q(status='executing')),
            done=Count('id', filter=Q(status='done')),
            failed=Count('id', filter=Q(status='failed')),
        )
        
        # Statistics by command type
        type_stats = commands.values('type').annotate(
            count=Count('id'),
            pending=Count('id', filter=Q(status='pending')),
            done=Count('id', filter=Q(status='done')),
            failed=Count('id', filter=Q(status='failed')),
        ).order_by('-count')
        
        # Statistics by status
        status_stats = commands.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Time series aggregation
        trunc_func = TruncDate('created_at')
        if period == 'week':
            trunc_func = TruncWeek('created_at')
        elif period == 'month':
            trunc_func = TruncMonth('created_at')
        
        time_series = commands.annotate(
            period=trunc_func
        ).values('period').annotate(
            total=Count('id'),
            done=Count('id', filter=Q(status='done')),
            failed=Count('id', filter=Q(status='failed')),
        ).order_by('period')
        
        # Calculate success rate
        success_rate = 0
        if overall_stats['total'] > 0:
            success_rate = (overall_stats['done'] / overall_stats['total']) * 100
        
        return {
            'overall': {
                'total': overall_stats['total'],
                'pending': overall_stats['pending'],
                'executing': overall_stats['executing'],
                'done': overall_stats['done'],
                'failed': overall_stats['failed'],
                'success_rate': round(success_rate, 2),
            },
            'by_type': [
                {
                    'type': item['type'],
                    'total': item['count'],
                    'pending': item['pending'],
                    'done': item['done'],
                    'failed': item['failed'],
                }
                for item in type_stats
            ],
            'by_status': [
                {
                    'status': item['status'],
                    'count': item['count'],
                }
                for item in status_stats
            ],
            'time_series': [
                {
                    'period': item['period'].isoformat() if item['period'] else None,
                    'total': item['total'],
                    'done': item['done'],
                    'failed': item['failed'],
                }
                for item in time_series
            ],
            'period': period,
        }


class ContentAnalyticsService:
    """Service for content download and usage analytics."""
    
    @staticmethod
    def get_content_statistics(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get content download and usage statistics.
        
        Args:
            start_date: Optional start date for time range
            end_date: Optional end date for time range
            
        Returns:
            Dictionary with content statistics
        """
        # Content download logs
        download_logs = ContentDownloadLog.objects.all()
        if start_date:
            download_logs = download_logs.filter(created_at__gte=start_date)
        if end_date:
            download_logs = download_logs.filter(created_at__lte=end_date)
        
        # Overall download statistics
        download_stats = download_logs.aggregate(
            total_downloads=Count('id'),
            successful=Count('id', filter=Q(status='success')),
            failed=Count('id', filter=Q(status='failed')),
            in_progress=Count('id', filter=Q(status='in_progress')),
        )
        
        # Statistics by content type
        content_types = Content.objects.values('type').annotate(
            count=Count('id'),
        ).order_by('-count')
        
        # Download statistics by content type
        type_download_stats = []
        if download_logs.exists():
            type_download_stats = download_logs.values(
                'content__type'
            ).annotate(
                total=Count('id'),
                successful=Count('id', filter=Q(status='success')),
                failed=Count('id', filter=Q(status='failed')),
            ).order_by('-total')
        
        # Calculate error rate
        error_rate = 0
        if download_stats['total_downloads'] > 0:
            error_rate = (download_stats['failed'] / download_stats['total_downloads']) * 100
        
        # Content type distribution
        total_content = Content.objects.count()
        type_distribution = [
            {
                'type': item['type'],
                'count': item['count'],
                'percentage': round((item['count'] / total_content * 100), 2) if total_content > 0 else 0,
            }
            for item in content_types
        ]
        
        return {
            'download_statistics': {
                'total_downloads': download_stats['total_downloads'],
                'successful': download_stats['successful'],
                'failed': download_stats['failed'],
                'in_progress': download_stats['in_progress'],
                'error_rate': round(error_rate, 2),
            },
            'type_distribution': type_distribution,
            'downloads_by_type': [
                {
                    'type': item['content__type'],
                    'total': item['total'],
                    'successful': item['successful'],
                    'failed': item['failed'],
                }
                for item in type_download_stats
            ],
            'total_content_items': total_content,
        }


class TemplateAnalyticsService:
    """Service for template usage analytics."""
    
    @staticmethod
    def get_template_statistics(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get template usage statistics.
        
        Args:
            start_date: Optional start date for time range
            end_date: Optional end date for time range
            
        Returns:
            Dictionary with template statistics
        """
        templates = Template.objects.all()
        
        # Template usage statistics
        template_stats = templates.annotate(
            active_screen_count=Count('active_screens', distinct=True),
            total_activation_count=Count('id'),  # This would need schedule/log tracking
        ).order_by('-active_screen_count')
        
        # Most active templates (currently on screens)
        most_active = template_stats[:10]
        
        # Total templates and active screens
        total_templates = templates.count()
        total_active_screens = Screen.objects.filter(active_template__isnull=False).count()
        
        # Templates by orientation
        orientation_stats = templates.values('orientation').annotate(
            count=Count('id')
        )
        
        return {
            'total_templates': total_templates,
            'total_active_screens': total_active_screens,
            'most_active_templates': [
                {
                    'template_id': str(template.id),
                    'template_name': template.name,
                    'active_screen_count': template.active_screen_count,
                }
                for template in most_active
            ],
            'by_orientation': [
                {
                    'orientation': item['orientation'],
                    'count': item['count'],
                }
                for item in orientation_stats
            ],
        }


class ActivityAnalyticsService:
    """Service for activity trends analytics."""
    
    @staticmethod
    def get_activity_trends(
        period: str = 'day',
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get activity trends over time.
        
        Args:
            period: Aggregation period ('day', 'week', 'month')
            days: Number of days to look back
            
        Returns:
            Dictionary with activity trends
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        trunc_func = TruncDate('created_at')
        if period == 'week':
            trunc_func = TruncWeek('created_at')
        elif period == 'month':
            trunc_func = TruncMonth('created_at')
        
        # Screen registrations
        screen_registrations = Screen.objects.filter(
            registration_date__gte=start_date,
            registration_date__lte=end_date
        ).annotate(
            period=trunc_func
        ).values('period').annotate(
            count=Count('id')
        ).order_by('period')
        
        # Commands created
        commands_created = Command.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).annotate(
            period=trunc_func
        ).values('period').annotate(
            count=Count('id')
        ).order_by('period')
        
        # Templates created
        templates_created = Template.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).annotate(
            period=trunc_func
        ).values('period').annotate(
            count=Count('id')
        ).order_by('period')
        
        # Content uploads (from Content model)
        content_uploads = Content.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).annotate(
            period=trunc_func
        ).values('period').annotate(
            count=Count('id')
        ).order_by('period')
        
        return {
            'period': period,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'screen_registrations': [
                {
                    'period': item['period'].isoformat() if item['period'] else None,
                    'count': item['count'],
                }
                for item in screen_registrations
            ],
            'commands_created': [
                {
                    'period': item['period'].isoformat() if item['period'] else None,
                    'count': item['count'],
                }
                for item in commands_created
            ],
            'templates_created': [
                {
                    'period': item['period'].isoformat() if item['period'] else None,
                    'count': item['count'],
                }
                for item in templates_created
            ],
            'content_uploads': [
                {
                    'period': item['period'].isoformat() if item['period'] else None,
                    'count': item['count'],
                }
                for item in content_uploads
            ],
        }
