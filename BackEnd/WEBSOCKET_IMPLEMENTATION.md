# WebSocket Real-Time Implementation

## Overview

This document describes the comprehensive real-time WebSocket implementation for Screengram, providing instant updates for commands, content synchronization, and screen status.

## Architecture

### Components

1. **ScreenConsumer** (`commands/consumers.py`)
   - Handles WebSocket connections from screens
   - Enhanced security with HMAC validation, rate limiting, and nonce protection
   - Supports real-time command delivery and status updates

2. **AdminDashboardConsumer** (`commands/dashboard_consumer.py`)
   - Handles WebSocket connections from dashboard users
   - JWT authentication with RBAC
   - Organization-based data filtering

3. **Real-time Broadcasting** (`commands/realtime_broadcast.py`)
   - Utility functions for broadcasting events
   - Command creation and status updates
   - Content sync progress events

4. **Signal Handlers** (`commands/signals.py`)
   - Automatically broadcast events when commands are created/updated
   - Integrated with Django signals

## WebSocket Endpoints

### Screen Connection
```
ws://server/ws/screen/?auth_token=<AUTH_TOKEN>&secret_key=<SECRET_KEY>
```

**Authentication:**
- Uses screen `auth_token` and `secret_key` from query parameters
- Validates credentials during handshake
- Rejects invalid connections

**Security Features:**
- HMAC signature validation on all messages
- Timestamp freshness check (5-minute window)
- Nonce replay protection
- Connection rate limiting (10 connections/minute per IP)
- Max concurrent connections per screen (3)
- Message rate limiting (100 messages/minute)
- Suspicious behavior detection and auto-disconnect

### Dashboard Connection
```
ws://server/ws/dashboard/?token=<JWT_ACCESS_TOKEN>
```

**Authentication:**
- Uses JWT access token from query parameters
- Validates token and user permissions
- Rejects expired tokens and inactive users

**RBAC:**
- **SuperAdmin/Admin**: Full access to all screens and commands
- **Operator**: Can see commands and screens in their organization
- **Manager/Viewer**: Read-only access to their organization's data

## Event Types

### Screen → Server Events

1. **command_ack**
   - Acknowledgment of command receipt
   - Required fields: `command_id`, `signature`, `timestamp`, `nonce`

2. **command_status**
   - Final status update (done/failed)
   - Required fields: `command_id`, `status`, `signature`, `timestamp`, `nonce`

3. **command_status_update**
   - Real-time status update (executing, progress)
   - Required fields: `command_id`, `status`, `signature`, `timestamp`, `nonce`
   - Optional: `progress` (0-100), `message`

4. **content_sync_progress**
   - Content download progress
   - Required fields: `screen_id`, `template_id`, `progress`, `signature`, `timestamp`, `nonce`
   - Optional: `content_id`, `status`, `error_message`

5. **screen_health_update**
   - Screen health metrics
   - Required fields: `screen_id`, `signature`, `timestamp`, `nonce`
   - Optional: `cpu_usage`, `memory_usage`, `disk_usage`, `uptime`

6. **heartbeat**
   - Periodic heartbeat
   - Optional: `latency`, `cpu_usage`, `memory_usage`

### Server → Screen Events

1. **command**
   - Command delivery
   - Contains: `command_id`, `command_type`, `payload`, `signature`, `timestamp`, `nonce`

2. **command_status_update**
   - Status update broadcast (for confirmation)

3. **content_sync_progress**
   - Content sync progress broadcast

4. **screen_health_update**
   - Health update broadcast

5. **error**
   - Error messages

### Server → Dashboard Events

1. **connection_confirmed**
   - Sent on successful connection
   - Contains: `user_id`, `role`, `organization`, `timestamp`

2. **command_status_update**
   - Command status changes
   - Filtered by user permissions

3. **content_sync_progress**
   - Content sync progress
   - Filtered by user permissions

4. **screen_status_update**
   - Screen online/offline status
   - Filtered by user permissions

5. **screen_health_update**
   - Screen health metrics
   - Filtered by user permissions

6. **pong**
   - Response to ping

7. **error**
   - Error messages

## Security Implementation

### Screen WebSocket Security

1. **HMAC Validation**
   - All messages must include valid HMAC-SHA256 signature
   - Signature includes: `timestamp|nonce|json_payload`
   - Validated using screen's `secret_key`

2. **Timestamp Validation**
   - Messages must be within 5-minute window
   - Prevents replay of old messages

3. **Nonce Replay Protection**
   - Each message must include unique nonce
   - Nonces cached for 1 hour
   - Reused nonces trigger security error

4. **Rate Limiting**
   - Connection rate: 10 connections/minute per IP
   - Message rate: 100 messages/minute per connection
   - Max connections: 3 concurrent per screen

5. **Suspicious Behavior Detection**
   - Tracks invalid messages
   - Auto-disconnects after 10 suspicious messages
   - Logs all security violations

### Dashboard WebSocket Security

1. **JWT Authentication**
   - Validates JWT token on handshake
   - Checks token expiration
   - Verifies user is active

2. **RBAC Enforcement**
   - Filters all events by user role
   - Organization-based data isolation
   - Prevents unauthorized data access

3. **Origin Checking**
   - Validates WebSocket origin (if configured)
   - Prevents CSRF attacks

## Real-Time Command Flow

1. **Command Creation**
   - Command created via API
   - Signal handler broadcasts `command_created` event
   - Dashboard users receive update instantly

2. **Command Delivery**
   - If screen is online via WebSocket:
     - Command sent via WebSocket group
     - Screen receives command immediately
   - If screen is offline:
     - Command queued for HTTP delivery
     - Delivered when screen comes online

3. **Command Execution**
   - Screen sends `command_ack` on receipt
   - Screen sends `command_status_update` during execution
   - Screen sends `command_status` on completion
   - All updates broadcast to dashboard users

## Real-Time Content Sync Flow

1. **Sync Initiated**
   - Content sync command sent to screen
   - `content_sync_started` event broadcast

2. **Progress Updates**
   - Screen sends `content_sync_progress` events
   - Progress percentage (0-100)
   - Broadcast to dashboard users

3. **Completion**
   - `content_sync_completed` or `content_sync_failed` event
   - Final status broadcast to dashboard

## Frontend Integration

### WebSocket Composable

```javascript
import { useWebSocket } from '@/composables/useWebSocket'

const ws = useWebSocket()

// Connect
ws.connect(accessToken)

// Listen to events
ws.on('command_status_update', (data) => {
  console.log('Command update:', data)
})

ws.on('screen_status_update', (data) => {
  console.log('Screen status:', data)
})

ws.on('content_sync_progress', (data) => {
  console.log('Content sync:', data.progress + '%')
})

// Disconnect
ws.disconnect()
```

### Auto-Reconnect

- Automatic reconnection with exponential backoff
- Max delay: 30 seconds
- Ping/pong for connection health

## Scalability

### Redis Channel Layer

For production, configure Redis:

```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

### Stateless Design

- All state stored in Redis/cache
- No in-memory state assumptions
- Supports horizontal scaling
- Handles worker restarts safely

## Logging & Monitoring

All WebSocket events are logged with:
- Screen ID or User ID
- IP address
- Timestamp
- Event type
- Success/failure status

Log levels:
- **INFO**: Connections, disconnections, successful operations
- **WARNING**: Invalid credentials, rate limit exceeded
- **ERROR**: Security violations, unexpected errors

## Backward Compatibility

- All existing REST APIs remain functional
- HTTP fallback for command delivery
- WebSocket is primary, HTTP is fallback
- No breaking changes to existing code

## Testing

### Screen Connection Test

```bash
# Using wscat
wscat -c "ws://localhost:8000/ws/screen/?auth_token=xxx&secret_key=yyy"
```

### Dashboard Connection Test

```bash
# Using wscat
wscat -c "ws://localhost:8000/ws/dashboard/?token=<JWT_TOKEN>"
```

## Production Checklist

- [ ] Configure Redis channel layer
- [ ] Set up proper CORS/Origin checking
- [ ] Configure rate limiting thresholds
- [ ] Set up monitoring and alerting
- [ ] Test horizontal scaling
- [ ] Load test WebSocket connections
- [ ] Review security logs regularly
- [ ] Set up connection metrics dashboard
