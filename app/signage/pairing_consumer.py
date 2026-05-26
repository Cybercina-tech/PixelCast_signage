"""
WebSocket consumer for TV / web-player pairing wait screen.

Authenticates with the temporary pairing_token query parameter (not JWT or
device credentials). Stays connected until the dashboard binds the session.
"""
import json
import logging
from urllib.parse import parse_qs, unquote

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone

from signage.models import PairingSession
from signage.pairing_broadcast import pairing_group_name

logger = logging.getLogger('channels')


class PairingConsumer(AsyncWebsocketConsumer):
    """Hold a pairing session open on the TV until bind completes."""

    async def connect(self):
        self.client_ip = self.scope.get('client', [None, None])[0]
        self.pairing_session = None
        self.group_name = None

        token = self._parse_pairing_token()
        if not token:
            logger.warning(
                'WebSocket connection rejected: Missing or invalid temporary pairing token.'
            )
            await self.close(code=4001)
            return

        session, reject_reason, already_paired = await self._load_valid_session(token)
        if not session:
            logger.warning(
                'WebSocket connection rejected: %s from IP %s',
                reject_reason or 'Missing or invalid temporary pairing token.',
                self.client_ip,
            )
            await self.close(code=4001)
            return

        self.pairing_session = session
        self.group_name = pairing_group_name(session.id)

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        if already_paired:
            await self.send(text_data=json.dumps({
                'event': 'paired',
                'screen_id': str(session.screen_id),
                'screen_name': session.screen.name if session.screen else '',
                'paired_at': session.paired_at.isoformat() if session.paired_at else timezone.now().isoformat(),
            }))
            return

        await self.send(text_data=json.dumps({
            'event': 'connected',
            'status': 'pending',
            'expires_at': session.expires_at.isoformat() if session.expires_at else None,
        }))
        logger.info(
            'Pairing WebSocket connected for session %s (code %s) from IP %s',
            session.id,
            session.pairing_code,
            self.client_ip,
        )

    async def disconnect(self, close_code):
        if self.group_name:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        if self.pairing_session:
            logger.info(
                'Pairing WebSocket disconnected for session %s (code %s)',
                self.pairing_session.id,
                close_code,
            )

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return
        try:
            payload = json.loads(text_data)
        except json.JSONDecodeError:
            return
        if payload.get('type') == 'ping':
            await self.send(text_data=json.dumps({'type': 'pong'}))

    async def pairing_complete(self, event):
        """Group message from broadcast_pairing_complete."""
        data = event.get('data') or {}
        await self.send(text_data=json.dumps(data))

    def _parse_pairing_token(self):
        query_string = self.scope.get('query_string', b'').decode()
        if not query_string:
            return None
        params = parse_qs(query_string, keep_blank_values=False)
        values = params.get('pairing_token') or []
        token = unquote(values[0]).strip() if values else ''
        return token or None

    @database_sync_to_async
    def _load_valid_session(self, token):
        try:
            session = PairingSession.objects.select_related('screen').get(pairing_token=token)
        except PairingSession.DoesNotExist:
            return None, 'Missing or invalid temporary pairing token.', False

        if session.status == 'paired' and session.screen_id:
            return session, None, True

        if session.status != 'pending':
            return None, 'Pairing session is no longer pending.', False

        if session.is_expired():
            return None, 'Pairing session has expired.', False

        return session, None, False
