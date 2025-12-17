# Real-Time Secure Communication Implementation

## Technical Summary

### Overview
This document describes the implementation of real-time, secure communication between the ScreenGram backend and physical Screens, replacing the placeholder `_send_to_screen()` method with a production-ready solution.

---

## Architecture

### Communication Flow

```
Backend (Django)                    Physical Screen
     |                                    |
     | 1. WebSocket Connection           |
     |    (ws://server/ws/screen/)       |
     |    + auth_token + secret_key      |
     |---------------------------------->|
     |                                    |
     | 2. Authentication                  |
     |    (validates credentials)        |
     |<---------------------------------->|
     |                                    |
     | 3. Command Delivery                |
     |    (signed payload)               |
     |---------------------------------->|
     |                                    |
     | 4. Command Acknowledgment          |
     |<----------------------------------|
     |                                    |
     | 5. Execution Status                |
     |<----------------------------------|
```

---

## How Screens Connect

### WebSocket Connection (Primary)

1. **Connection URL**: `ws://server/ws/screen/?auth_token=<token>&secret_key=<key>`
2. **Authentication**: Happens during WebSocket handshake
   - Screen sends `auth_token` and `secret_key` as query parameters
   - Backend validates credentials using `Screen.authenticate()`
   - Connection rejected if invalid (close code 4001)
3. **Connection Registry**: 
   - Screen ID → Channel Name mapping stored in Django cache
   - Auto-cleanup on disconnect
   - One connection per screen (new connection replaces old)

### HTTP Fallback (Secondary)

- **Endpoint**: `POST /api/commands/screens/command-receive/`
- **Authentication**: Via headers (`X-Auth-Token`, `X-Secret-Key`) or payload
- **Used when**: WebSocket is unavailable or connection lost
- **Same security**: HMAC signature, timestamp, nonce validation

---

## How Commands Flow

### Command Execution Lifecycle

1. **Command Creation**: User/admin creates command via API
2. **Command Queuing**: Command stored with status='pending'
3. **Command Delivery**:
   - `Command.execute()` → `_execute_by_type_for_screen()` → `_send_to_screen()`
   - `_send_to_screen()` tries WebSocket first, falls back to HTTP
4. **Screen Receives**:
   - WebSocket: Receives via `command_message` event
   - HTTP: Receives via POST endpoint
5. **Screen Acknowledges**:
   - Sends `command_ack` message (WebSocket) or HTTP response
   - Backend updates `CommandExecutionLog` with status='running'
6. **Screen Executes**: Screen processes command locally
7. **Status Update**:
   - Screen sends `command_status` message (done/failed)
   - Backend updates command and execution log

### Status Transitions

```
pending → executing → done
                   ↘ failed
```

---

## Security Design

### Multi-Layer Security

1. **Authentication Layer**
   - `auth_token` + `secret_key` validation
   - Rejects connection if invalid
   - No session-based auth (stateless)

2. **HMAC Signature Validation**
   - Every command payload is signed with HMAC-SHA256
   - Signature: `HMAC(secret_key, timestamp|nonce|json_payload)`
   - Prevents tampering

3. **Timestamp Validation**
   - Messages older than 5 minutes are rejected
   - Prevents replay of old commands
   - Configurable via `TIMESTAMP_TOLERANCE`

4. **Nonce-Based Replay Protection**
   - Each command includes unique nonce (UUID)
   - Nonces cached for 1 hour
   - Reject if nonce already used

5. **IP Consistency Check**
   - Compares connection IP with `Screen.last_ip`
   - Logs mismatch (doesn't reject - NAT can change IPs)
   - Helps detect unauthorized access

6. **Rate Limiting**
   - Max 60 commands per minute per screen
   - Prevents command flooding
   - Configurable via `RATE_LIMIT_COMMANDS_PER_MINUTE`

### Security Flow

```
Command Creation
    ↓
Sign Payload (HMAC-SHA256)
    ↓
Add Timestamp + Nonce
    ↓
Send to Screen
    ↓
Screen Validates:
  - HMAC Signature ✓
  - Timestamp (not expired) ✓
  - Nonce (not used before) ✓
  - Rate Limit ✓
    ↓
Execute Command
```

---

## What Happens if Screen is Compromised

### Attack Scenarios & Mitigations

1. **Stolen auth_token + secret_key**
   - **Impact**: Attacker can connect as screen
   - **Mitigation**: 
     - IP consistency check logs suspicious connections
     - Rate limiting prevents command flooding
     - Nonce prevents replay attacks
     - Timestamp prevents old command replay
   - **Response**: Admin can regenerate `auth_token` and `secret_key` for screen

2. **Man-in-the-Middle Attack**
   - **Impact**: Intercept and modify commands
   - **Mitigation**: 
     - HMAC signature validation prevents tampering
     - Modified payloads fail signature check
     - Connection rejected

3. **Replay Attack**
   - **Impact**: Re-send old commands
   - **Mitigation**: 
     - Nonce tracking prevents duplicate commands
     - Timestamp validation rejects old messages
     - Each command has unique nonce

4. **Command Flooding**
   - **Impact**: Overwhelm screen with commands
   - **Mitigation**: 
     - Rate limiting (60 commands/minute)
     - Commands queued, not lost
     - Screen can throttle processing

5. **Unauthorized Command Execution**
   - **Impact**: Attacker sends malicious commands
   - **Mitigation**: 
     - All commands logged in `CommandExecutionLog`
     - Audit trail for investigation
     - Commands tied to specific screen (can't execute on wrong screen)

### Compromise Detection

- **Logging**: All security failures logged
  - Invalid signatures
  - Expired timestamps
  - Replay attempts
  - Rate limit violations
  - IP mismatches

- **Monitoring**: Admin can monitor:
  - Connection patterns
  - Command execution rates
  - Failed authentication attempts
  - Security validation failures

---

## Implementation Details

### Files Created/Modified

1. **`BackEnd/commands/security.py`**
   - HMAC signature generation/validation
   - Timestamp validation
   - Nonce tracking
   - Rate limiting

2. **`BackEnd/commands/connection_registry.py`**
   - Screen connection tracking
   - Channel name mapping
   - WebSocket command delivery

3. **`BackEnd/commands/consumers.py`**
   - WebSocket consumer for screens
   - Authentication during handshake
   - Command delivery and status handling

4. **`BackEnd/commands/models.py`** (Modified)
   - `_send_to_screen()`: Real implementation
   - WebSocket-first, HTTP fallback

5. **`BackEnd/commands/views.py`** (Modified)
   - `command_receive_endpoint()`: HTTP fallback
   - `send_command_via_http()`: HTTP delivery helper

6. **`BackEnd/Screengram/settings.py`** (Modified)
   - Django Channels configuration
   - Channel layers setup
   - Security settings

7. **`BackEnd/Screengram/routing.py`** (Created)
   - WebSocket URL routing

8. **`BackEnd/Screengram/asgi.py`** (Modified)
   - ASGI application with WebSocket support

9. **`requirements.txt`** (Modified)
   - Added `channels` and `channels-redis`

---

## Configuration

### Development (In-Memory Channel Layer)
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}
```

### Production (Redis Channel Layer)
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

---

## Usage Examples

### Screen WebSocket Connection
```javascript
// Screen-side JavaScript example
const ws = new WebSocket(
    'ws://server/ws/screen/?auth_token=xxx&secret_key=yyy'
);

ws.onopen = () => {
    console.log('Connected to backend');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'command') {
        // Execute command
        executeCommand(data.command);
        
        // Acknowledge
        ws.send(JSON.stringify({
            type: 'command_ack',
            command_id: data.command.payload.command_id
        }));
        
        // Send status update when done
        ws.send(JSON.stringify({
            type: 'command_status',
            command_id: data.command.payload.command_id,
            status: 'done',
            response_payload: {}
        }));
    }
};
```

### Backend Command Execution
```python
# Create and execute command
command = Command.queue_command(
    command_type='restart',
    screen=screen,
    priority=10
)

# Command automatically sent via WebSocket or HTTP
success = command.execute()
```

---

## Testing

### Manual Testing Steps

1. **Start Django with ASGI**:
   ```bash
   daphne -b 0.0.0.0 -p 8000 Screengram.asgi:application
   ```

2. **Connect Screen via WebSocket**:
   ```bash
   wscat -c "ws://localhost:8000/ws/screen/?auth_token=<token>&secret_key=<key>"
   ```

3. **Send Command via API**:
   ```bash
   POST /api/commands/
   {
     "screen": "<screen_id>",
     "type": "restart",
     "priority": 10
   }
   ```

4. **Verify Command Delivery**:
   - Check WebSocket message received
   - Check `CommandExecutionLog` created
   - Check command status updated

---

## Production Deployment Notes

1. **Use Redis** for channel layers in production
2. **Enable HTTPS/WSS** for secure WebSocket connections
3. **Configure ALLOWED_HOSTS** properly
4. **Monitor connection registry** for memory usage
5. **Set up logging** for security events
6. **Regularly rotate** screen auth tokens
7. **Monitor rate limits** and adjust if needed

---

## Extension Points

### MQTT Support (Future)

The architecture allows easy addition of MQTT:

1. Create `commands/mqtt_client.py`
2. Implement `send_command_via_mqtt()`
3. Add to `_send_to_screen()` fallback chain:
   - WebSocket → HTTP → MQTT

### Additional Security

- TLS/SSL encryption for WebSocket (WSS)
- Certificate pinning
- Command encryption (AES)
- Two-factor authentication for critical commands

---

## Summary

✅ **WebSocket Primary**: Real-time bidirectional communication
✅ **HTTP Fallback**: Reliable delivery when WebSocket unavailable
✅ **Multi-Layer Security**: HMAC, timestamp, nonce, rate limiting
✅ **Connection Registry**: Efficient command routing
✅ **Full Lifecycle**: Command creation → delivery → execution → logging
✅ **Production Ready**: Error handling, logging, monitoring

The implementation provides secure, reliable, real-time communication between backend and screens while maintaining backward compatibility and extensibility.

