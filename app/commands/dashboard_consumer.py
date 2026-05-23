"""
WebSocket consumer for admin dashboard.

Handles real-time updates for authenticated dashboard users with JWT authentication
and role-based access control (RBAC).
"""
import json
import logging
import re
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from jwt import decode as jwt_decode
from django.conf import settings
from urllib.parse import parse_qs, unquote

from accounts.models import User
from signage.models import Screen
from commands.models import Command
from commands.realtime_metrics import increment_metric

logger = logging.getLogger(__name__)


class AdminDashboardConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for admin dashboard connections.
    
    Handles:
    - JWT authentication during handshake
    - Role-based access control (RBAC)
    - Real-time updates for commands, screens, and content
    - Organization-based filtering
    """
    
    MAX_CONNECTIONS_PER_MINUTE_PER_IP = 30
    MAX_CONNECTIONS_PER_MINUTE_PER_USER = 20
    ACL_CACHE_TTL_SECONDS = 30

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ws_security = getattr(settings, 'DASHBOARD_WS_SECURITY', {})
        self.MAX_CONNECTIONS_PER_MINUTE_PER_IP = ws_security.get(
            'MAX_CONNECTIONS_PER_MINUTE_PER_IP',
            self.MAX_CONNECTIONS_PER_MINUTE_PER_IP
        )
        self.MAX_CONNECTIONS_PER_MINUTE_PER_USER = ws_security.get(
            'MAX_CONNECTIONS_PER_MINUTE_PER_USER',
            self.MAX_CONNECTIONS_PER_MINUTE_PER_USER
        )
        self.ACL_CACHE_TTL_SECONDS = ws_security.get(
            'ACL_CACHE_TTL_SECONDS',
            self.ACL_CACHE_TTL_SECONDS
        )
        self.user = None
        self.user_id = None
        self.organization_name = None
        self.user_role = None
        self.client_ip = None
        self.dashboard_groups = []
    
    async def connect(self):
        """
        Handle WebSocket connection.
        
        Authenticates user using JWT token from query params.
        Rejects connection if authentication fails or user lacks permissions.
        """
        # Get client IP for logging
        self.client_ip = self.scope.get('client', [None, None])[0]
        
        # Parse query string
        query_string = self.scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string, keep_blank_values=False)
        
        # Get JWT token from query string
        token_values = query_params.get('token') or []
        token = unquote(token_values[0]) if token_values else None
        
        if not token:
            increment_metric("dashboard_ws_connect_rejected_total")
            increment_metric("dashboard_ws_auth_rejected_total")
            logger.warning(f"Dashboard WebSocket connection rejected: missing token from IP {self.client_ip}")
            await self.close(code=4001)  # Unauthorized
            return
        
        # Authenticate user with JWT
        try:
            self.user, auth_reason = await self.authenticate_user(token)
            if not self.user:
                increment_metric("dashboard_ws_connect_rejected_total")
                increment_metric("dashboard_ws_auth_rejected_total")
                logger.warning(
                    f"Dashboard WebSocket connection rejected: {auth_reason} from IP {self.client_ip}"
                )
                await self.close(code=4001)  # Unauthorized
                return
            
            # Check if user is active
            if not self.user.is_active:
                increment_metric("dashboard_ws_connect_rejected_total")
                increment_metric("dashboard_ws_auth_rejected_total")
                logger.warning(f"Dashboard WebSocket connection rejected: inactive user {self.user.id}")
                await self.close(code=4001)  # Unauthorized
                return
            
            self.user_id = str(self.user.id)
            self.organization_name = self.user.organization_name
            self.user_role = self.user.role

            if not self.check_connection_rate_limit():
                increment_metric("dashboard_ws_connect_rejected_total")
                increment_metric("dashboard_ws_rate_limited_total")
                logger.warning(
                    f"Dashboard WebSocket connection rejected: rate limit exceeded for user {self.user_id} from IP {self.client_ip}"
                )
                await self.close(code=4003)
                return
            
            # Check permissions (all authenticated users can connect, but data is filtered)
            # Viewer role has read-only access
            # Operator, Manager, Admin, SuperAdmin have full access
            
            # Add to scoped dashboard groups to reduce global fan-out.
            self.dashboard_groups = self.resolve_dashboard_groups()
            for group in self.dashboard_groups:
                await self.channel_layer.group_add(group, self.channel_name)
            
            await self.accept()
            increment_metric("dashboard_ws_connect_success_total")
            increment_metric("dashboard_ws_active_connections")
            
            # Update user's last_seen
            await self.update_user_last_seen()
            
            logger.info(f"Dashboard user {self.user_id} ({self.user_role}) connected via WebSocket from IP {self.client_ip}")
            
            # Send initial connection confirmation
            await self.send(text_data=json.dumps({
                'type': 'connection_confirmed',
                'user_id': self.user_id,
                'role': self.user_role,
                'organization': self.organization_name,
                'timestamp': timezone.now().isoformat()
            }))
            
        except Exception as e:
            increment_metric("dashboard_ws_connect_rejected_total")
            logger.error(f"Error during dashboard WebSocket connection: {str(e)}", exc_info=True)
            await self.close(code=4002)  # Internal error
    
    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.
        
        Removes user from dashboard group.
        """
        if self.user_id:
            increment_metric("dashboard_ws_active_connections", delta=-1)
            # Remove from group
            for group in self.dashboard_groups:
                await self.channel_layer.group_discard(group, self.channel_name)
            
            logger.info(f"Dashboard user {self.user_id} disconnected (code: {close_code}) from IP {self.client_ip}")
    
    async def receive(self, text_data):
        """
        Handle messages received from dashboard client.
        
        Expected message types:
        - subscribe_screen: Subscribe to updates for specific screen
        - unsubscribe_screen: Unsubscribe from screen updates
        - subscribe_command: Subscribe to updates for specific command
        - ping: Heartbeat/ping message
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'subscribe_screen':
                await self.handle_subscribe_screen(data)
            elif message_type == 'unsubscribe_screen':
                await self.handle_unsubscribe_screen(data)
            elif message_type == 'subscribe_command':
                await self.handle_subscribe_command(data)
            elif message_type == 'ping':
                await self.handle_ping()
            else:
                logger.warning(f"Unknown message type from dashboard user {self.user_id}: {message_type}")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received from dashboard user {self.user_id}")
        except Exception as e:
            logger.error(f"Error processing message from dashboard user {self.user_id}: {str(e)}", exc_info=True)
    
    async def command_status_update(self, event):
        """
        Handle command status update broadcast.
        
        Filters data based on user permissions and organization.
        """
        data = event['data']
        if not self.is_event_visible_for_user(data):
            return
        
        # Check if user has permission to see this command
        if await self.can_access_command(data.get('command_id')):
            await self.send(text_data=json.dumps({
                'type': 'command_status_update',
                'data': data
            }))
    
    async def content_sync_progress(self, event):
        """
        Handle content sync progress broadcast.
        
        Filters data based on user permissions and organization.
        """
        data = event['data']
        if not self.is_event_visible_for_user(data):
            return
        
        # Check if user has permission to see this screen
        if await self.can_access_screen(data.get('screen_id')):
            await self.send(text_data=json.dumps({
                'type': 'content_sync_progress',
                'data': data
            }))
    
    async def screen_status_update(self, event):
        """
        Handle screen status update broadcast (online/offline).
        
        Filters data based on user permissions and organization.
        """
        data = event['data']
        if not self.is_event_visible_for_user(data):
            return
        
        # Check if user has permission to see this screen
        if await self.can_access_screen(data.get('screen_id')):
            await self.send(text_data=json.dumps({
                'type': 'screen_status_update',
                'data': data
            }))
    
    async def screen_health_update(self, event):
        """
        Handle screen health update broadcast.
        
        Filters data based on user permissions and organization.
        """
        data = event['data']
        if not self.is_event_visible_for_user(data):
            return
        
        # Check if user has permission to see this screen
        if await self.can_access_screen(data.get('screen_id')):
            await self.send(text_data=json.dumps({
                'type': 'screen_health_update',
                'data': data
            }))
    
    async def handle_subscribe_screen(self, data):
        """Handle screen subscription request"""
        screen_id = data.get('screen_id')
        if not screen_id:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'screen_id required'
            }))
            return
        
        # Check permissions
        if not await self.can_access_screen(screen_id):
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Permission denied'
            }))
            return
        
        # Add to screen-specific group
        screen_group = f'screen_{screen_id}'
        await self.channel_layer.group_add(
            screen_group,
            self.channel_name
        )
        
        await self.send(text_data=json.dumps({
            'type': 'subscribed',
            'resource_type': 'screen',
            'resource_id': screen_id
        }))
    
    async def handle_unsubscribe_screen(self, data):
        """Handle screen unsubscription request"""
        screen_id = data.get('screen_id')
        if screen_id:
            screen_group = f'screen_{screen_id}'
            await self.channel_layer.group_discard(
                screen_group,
                self.channel_name
            )
    
    async def handle_subscribe_command(self, data):
        """Handle command subscription request"""
        command_id = data.get('command_id')
        if not command_id:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'command_id required'
            }))
            return
        
        # Check permissions
        if not await self.can_access_command(command_id):
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Permission denied'
            }))
            return
        
        # Commands are pushed via scoped dashboard groups, no separate command group needed
    
    async def handle_ping(self):
        """Handle ping message"""
        await self.send(text_data=json.dumps({
            'type': 'pong',
            'timestamp': timezone.now().isoformat()
        }))
    
    async def can_access_screen(self, screen_id):
        """
        Check if user can access a specific screen.
        
        Rules:
        - SuperAdmin/Admin: Can access all screens
        - Others: Can only access screens in their organization
        """
        if not screen_id:
            return False
        
        if self.user.is_developer() or self.user.is_manager():
            return True

        cache_key = f"dashboard_acl:screen:{self.user_id}:{screen_id}"
        cached = cache.get(cache_key)
        if cached is not None:
            return bool(cached)

        try:
            screen = await database_sync_to_async(
                lambda: Screen.objects.select_related('owner').get(id=screen_id)
            )()
            if screen.owner_id == self.user.id:
                return True
            if (
                self.organization_name
                and screen.owner
                and getattr(screen.owner, 'organization_name', None) == self.organization_name
            ):
                cache.set(cache_key, True, self.ACL_CACHE_TTL_SECONDS)
                return True
            cache.set(cache_key, False, self.ACL_CACHE_TTL_SECONDS)
            return False
        except ObjectDoesNotExist:
            cache.set(cache_key, False, self.ACL_CACHE_TTL_SECONDS)
            return False
    
    async def can_access_command(self, command_id):
        """
        Check if user can access a specific command.
        
        Rules:
        - SuperAdmin/Admin: Can access all commands
        - Operator: Can access commands for screens in their organization
        - Manager/Viewer: Can view commands for screens in their organization
        """
        if not command_id:
            return False
        
        if self.user.is_developer() or self.user.is_manager():
            return True

        cache_key = f"dashboard_acl:command:{self.user_id}:{command_id}"
        cached = cache.get(cache_key)
        if cached is not None:
            return bool(cached)

        try:
            command = await database_sync_to_async(
                lambda: Command.objects.select_related('screen', 'screen__owner').get(id=command_id)
            )()
            screen = command.screen
            if screen.owner_id == self.user.id:
                return True
            if (
                self.organization_name
                and screen.owner
                and getattr(screen.owner, 'organization_name', None) == self.organization_name
            ):
                cache.set(cache_key, True, self.ACL_CACHE_TTL_SECONDS)
                return True
            cache.set(cache_key, False, self.ACL_CACHE_TTL_SECONDS)
            return False
        except ObjectDoesNotExist:
            cache.set(cache_key, False, self.ACL_CACHE_TTL_SECONDS)
            return False
    
    @database_sync_to_async
    def authenticate_user(self, token):
        """
        Authenticate user using JWT token.
        
        Args:
            token: JWT access token string
            
        Returns:
            Tuple[User|None, str] as (user, reason)
        """
        try:
            # Validate token structure
            UntypedToken(token)
            
            # Decode token to get user_id
            decoded_data = jwt_decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"]
            )
            user_id = decoded_data.get('user_id')
            
            if not user_id:
                return None, "invalid token (missing user_id claim)"
            
            # Get user
            try:
                user = User.objects.get(id=user_id, is_active=True)
                return user, "ok"
            except ObjectDoesNotExist:
                return None, f"user {user_id} not found or inactive"
                
        except (InvalidToken, TokenError) as e:
            reason = str(e).lower()
            if "expired" in reason:
                logger.warning(f"Invalid JWT token: {str(e)}")
                return None, "expired token"
            logger.warning(f"Invalid JWT token: {str(e)}")
            return None, "invalid token"
        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}", exc_info=True)
            return None, "authentication error"
    
    @database_sync_to_async
    def update_user_last_seen(self):
        """Update user's last_seen timestamp"""
        if self.user:
            self.user.update_last_seen()

    def check_connection_rate_limit(self):
        """Rate limit dashboard websocket connect attempts by IP and user."""
        ip = self.client_ip or "unknown"
        user = self.user_id or "unknown"
        ip_key = f"dashboard_ws_conn_rate:ip:{ip}"
        user_key = f"dashboard_ws_conn_rate:user:{user}"

        ip_count = cache.get(ip_key, 0)
        user_count = cache.get(user_key, 0)

        if ip_count >= self.MAX_CONNECTIONS_PER_MINUTE_PER_IP:
            return False
        if user_count >= self.MAX_CONNECTIONS_PER_MINUTE_PER_USER:
            return False

        cache.set(ip_key, ip_count + 1, 60)
        cache.set(user_key, user_count + 1, 60)
        return True

    def resolve_dashboard_groups(self):
        """Select dashboard groups for this user to avoid global broadcasts for all users."""
        groups = set()
        if self.user and (self.user.is_developer() or self.user.is_manager()):
            groups.add('dashboard_global_updates')
        else:
            org_group = self._org_group_name(self.organization_name)
            if org_group:
                groups.add(org_group)
        if not groups:
            groups.add('dashboard_global_updates')
        return list(groups)

    def is_event_visible_for_user(self, data):
        """Fast path filter using event organization before DB checks."""
        event_org = (data or {}).get('organization_name')
        if not event_org:
            return True
        if self.user and (self.user.is_developer() or self.user.is_manager()):
            return True
        return event_org == self.organization_name

    @staticmethod
    def _org_group_name(organization_name):
        if not organization_name:
            return None
        normalized = re.sub(r'[^a-z0-9_]', '_', str(organization_name).strip().lower())
        normalized = re.sub(r'_+', '_', normalized).strip('_')
        if not normalized:
            return None
        return f"dashboard_org_{normalized}"
