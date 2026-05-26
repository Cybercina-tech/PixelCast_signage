"""
Real-time pairing notifications over Django Channels.

When a dashboard user binds a pairing session, we push an event to any TV
WebSocket that is waiting on that session's channel group.
"""
import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

logger = logging.getLogger(__name__)


def pairing_group_name(session_id) -> str:
    return f'pairing_session_{session_id}'


def broadcast_pairing_complete(session, screen) -> None:
    """
    Notify waiting player clients that pairing succeeded.

    The TV should poll GET /api/pairing/status/ once to receive the one-time
    device token; this event only signals that bind completed.
    """
    channel_layer = get_channel_layer()
    if not channel_layer:
        logger.warning('Pairing broadcast skipped: channel layer not configured')
        return

    payload = {
        'event': 'paired',
        'screen_id': str(screen.id),
        'screen_name': screen.name,
        'paired_at': session.paired_at.isoformat() if session.paired_at else timezone.now().isoformat(),
    }
    group = pairing_group_name(session.id)

    try:
        async_to_sync(channel_layer.group_send)(
            group,
            {
                'type': 'pairing_complete',
                'data': payload,
            },
        )
        logger.info('Pairing complete broadcast sent for session %s screen %s', session.id, screen.id)
    except Exception as exc:
        logger.error('Failed to broadcast pairing complete for session %s: %s', session.id, exc, exc_info=True)
