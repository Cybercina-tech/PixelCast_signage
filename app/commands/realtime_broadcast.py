"""
Real-time broadcasting utilities for WebSocket events.

Provides functions to broadcast command and content sync events
to connected dashboard users and screens.
"""
import logging
import re
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone

logger = logging.getLogger(__name__)


def _org_group_name(organization_name):
    if not organization_name:
        return None
    normalized = re.sub(r'[^a-z0-9_]', '_', str(organization_name).strip().lower())
    normalized = re.sub(r'_+', '_', normalized).strip('_')
    if not normalized:
        return None
    return f'dashboard_org_{normalized}'


def _dashboard_target_groups(organization_name=None):
    groups = {'dashboard_global_updates'}
    org_group = _org_group_name(organization_name)
    if org_group:
        groups.add(org_group)
    return list(groups)


def dashboard_target_groups(organization_name=None):
    """Public helper for async publishers that need raw group list."""
    return _dashboard_target_groups(organization_name)


def _broadcast_dashboard_event(event_type, data, organization_name=None):
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    for group in _dashboard_target_groups(organization_name):
        async_to_sync(channel_layer.group_send)(
            group,
            {
                'type': event_type,
                'data': data
            }
        )


def broadcast_dashboard_event(event_type, data, organization_name=None):
    """Public wrapper used by async/sync publishers across commands package."""
    _broadcast_dashboard_event(event_type, data, organization_name)


def broadcast_command_created(command):
    """
    Broadcast command creation event to dashboard users.
    
    Args:
        command: Command instance
    """
    try:
        payload = {
            'command_id': str(command.id),
            'screen_id': str(command.screen.id),
            'screen_name': command.screen.name,
            'command_type': command.type,
            'command_name': command.name,
            'status': command.status,
            'priority': command.priority,
            'created_at': command.created_at.isoformat() if command.created_at else None,
            'created_by': str(command.created_by.id) if command.created_by else None,
            'organization_name': getattr(command.screen.owner, 'organization_name', None),
            'timestamp': timezone.now().isoformat(),
            'event_type': 'command_created'
        }
        _broadcast_dashboard_event(
            'command_status_update',
            payload,
            payload.get('organization_name')
        )
        logger.debug(f"Broadcasted command_created event for command {command.id}")
    except Exception as e:
        logger.error(f"Error broadcasting command_created: {str(e)}", exc_info=True)


def broadcast_command_status_update(command, status, progress=None, message=None):
    """
    Broadcast command status update to dashboard users.
    
    Args:
        command: Command instance
        status: New status ('pending', 'executing', 'done', 'failed')
        progress: Optional progress percentage (0-100)
        message: Optional status message
    """
    try:
        payload = {
            'command_id': str(command.id),
            'screen_id': str(command.screen.id),
            'screen_name': command.screen.name,
            'command_type': command.type,
            'status': status,
            'progress': progress,
            'message': message,
            'error_message': command.error_message if status == 'failed' else None,
            'completed_at': command.completed_at.isoformat() if command.completed_at else None,
            'organization_name': getattr(command.screen.owner, 'organization_name', None),
            'timestamp': timezone.now().isoformat(),
            'event_type': 'command_status_update'
        }
        _broadcast_dashboard_event(
            'command_status_update',
            payload,
            payload.get('organization_name')
        )
        logger.debug(f"Broadcasted command_status_update for command {command.id}: {status}")
    except Exception as e:
        logger.error(f"Error broadcasting command_status_update: {str(e)}", exc_info=True)


def broadcast_content_sync_started(screen_id, template_id, content_id=None, organization_name=None):
    """
    Broadcast content sync started event.
    
    Args:
        screen_id: Screen UUID string
        template_id: Template UUID string
        content_id: Optional content UUID string
    """
    try:
        payload = {
            'screen_id': str(screen_id),
            'template_id': str(template_id),
            'content_id': str(content_id) if content_id else None,
            'organization_name': organization_name,
            'status': 'started',
            'progress': 0,
            'timestamp': timezone.now().isoformat(),
            'event_type': 'content_sync_started'
        }
        _broadcast_dashboard_event(
            'content_sync_progress',
            payload,
            payload.get('organization_name')
        )
        logger.debug(f"Broadcasted content_sync_started for screen {screen_id}")
    except Exception as e:
        logger.error(f"Error broadcasting content_sync_started: {str(e)}", exc_info=True)


def broadcast_content_sync_progress(screen_id, template_id, content_id, progress, status='downloading', organization_name=None):
    """
    Broadcast content sync progress update.
    
    Args:
        screen_id: Screen UUID string
        template_id: Template UUID string
        content_id: Content UUID string
        progress: Progress percentage (0-100)
        status: Status ('downloading', 'completed', 'failed')
    """
    try:
        payload = {
            'screen_id': str(screen_id),
            'template_id': str(template_id),
            'content_id': str(content_id),
            'organization_name': organization_name,
            'status': status,
            'progress': progress,
            'timestamp': timezone.now().isoformat(),
            'event_type': 'content_download_progress'
        }
        _broadcast_dashboard_event(
            'content_sync_progress',
            payload,
            payload.get('organization_name')
        )
        logger.debug(f"Broadcasted content_sync_progress for screen {screen_id}: {progress}%")
    except Exception as e:
        logger.error(f"Error broadcasting content_sync_progress: {str(e)}", exc_info=True)


def broadcast_content_sync_completed(screen_id, template_id, content_id=None, organization_name=None):
    """
    Broadcast content sync completed event.
    
    Args:
        screen_id: Screen UUID string
        template_id: Template UUID string
        content_id: Optional content UUID string
    """
    try:
        payload = {
            'screen_id': str(screen_id),
            'template_id': str(template_id),
            'content_id': str(content_id) if content_id else None,
            'organization_name': organization_name,
            'status': 'completed',
            'progress': 100,
            'timestamp': timezone.now().isoformat(),
            'event_type': 'content_download_completed'
        }
        _broadcast_dashboard_event(
            'content_sync_progress',
            payload,
            payload.get('organization_name')
        )
        logger.debug(f"Broadcasted content_sync_completed for screen {screen_id}")
    except Exception as e:
        logger.error(f"Error broadcasting content_sync_completed: {str(e)}", exc_info=True)


def broadcast_content_sync_failed(screen_id, template_id, content_id, error_message, organization_name=None):
    """
    Broadcast content sync failed event.
    
    Args:
        screen_id: Screen UUID string
        template_id: Template UUID string
        content_id: Content UUID string
        error_message: Error message
    """
    try:
        payload = {
            'screen_id': str(screen_id),
            'template_id': str(template_id),
            'content_id': str(content_id),
            'organization_name': organization_name,
            'status': 'failed',
            'progress': 0,
            'error_message': error_message,
            'timestamp': timezone.now().isoformat(),
            'event_type': 'content_download_failed'
        }
        _broadcast_dashboard_event(
            'content_sync_progress',
            payload,
            payload.get('organization_name')
        )
        logger.debug(f"Broadcasted content_sync_failed for screen {screen_id}")
    except Exception as e:
        logger.error(f"Error broadcasting content_sync_failed: {str(e)}", exc_info=True)
