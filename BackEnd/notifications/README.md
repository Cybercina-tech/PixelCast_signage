# ScreenGram Notification System

## Overview

Production-ready, secure notification system for ScreenGram Digital Signage System. Supports Email, SMS, and Webhook channels with event-driven architecture, full audit trail, and panel-ready configuration.

## Features

- **Multi-Channel Support**: Email (SMTP), SMS (Twilio/Generic), Webhook (HTTP with HMAC)
- **Event-Driven**: Automatic notifications for critical system events
- **Security-First**: Encrypted configs, HMAC signatures, replay protection, rate limiting
- **Panel-Ready**: Full backend support for future admin panel control
- **Async Delivery**: Celery-based async delivery (configurable)
- **Audit Trail**: Complete logging of all notification attempts
- **Idempotent**: Deduplication and cooldown enforcement

## Installation

1. Install dependencies:
```bash
pip install cryptography celery redis twilio
```

2. Run migrations:
```bash
python manage.py migrate notifications
```

3. Initialize default events:
```bash
python manage.py init_notification_events
```

4. Configure Celery (for async delivery):
```bash
# Start Celery worker
celery -A Screengram worker -l info
```

## Configuration

### Settings

Add to `settings.py`:

```python
# Notification System Configuration
NOTIFICATIONS_ASYNC = True  # Use Celery for async delivery
NOTIFICATION_ENCRYPTION_KEY = os.environ.get('NOTIFICATION_ENCRYPTION_KEY')  # Required!

# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
```

### Environment Variables

```bash
NOTIFICATION_ENCRYPTION_KEY=<base64-encoded-key>  # Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## Usage

### Creating Notification Channels

#### Email Channel
```python
from notifications.models import NotificationChannel

channel = NotificationChannel.objects.create(
    type='email',
    name='Admin Email',
    config={
        'smtp_host': 'smtp.example.com',
        'smtp_port': 587,
        'from_email': 'alerts@screengram.com',
        'to_emails': ['admin@example.com'],
        'use_tls': True,
        'username': 'smtp_user',
        'password': 'smtp_password'
    },
    is_enabled=True
)
```

#### SMS Channel (Twilio)
```python
channel = NotificationChannel.objects.create(
    type='sms',
    name='Admin SMS',
    config={
        'provider': 'twilio',
        'account_sid': 'ACxxxxx',
        'auth_token': 'xxxxx',
        'from_number': '+1234567890',
        'to_numbers': ['+1234567890']
    },
    is_enabled=True
)
```

#### Webhook Channel
```python
channel = NotificationChannel.objects.create(
    type='webhook',
    name='Slack Webhook',
    config={
        'url': 'https://hooks.slack.com/services/xxx',
        'secret_key': 'your-secret-key',
        'allowed_domains': ['hooks.slack.com']
    },
    is_enabled=True
)
```

### Creating Notification Rules

```python
from notifications.models import NotificationRule, NotificationEvent

event = NotificationEvent.objects.get(event_key='screen.offline')

rule = NotificationRule.objects.create(
    event=event,
    severity_threshold='warning',
    cooldown_seconds=300,  # 5 minutes
    is_enabled=True
)
rule.channels.add(email_channel, sms_channel)
```

### Manual Notification Dispatch

```python
from notifications.dispatcher import NotificationDispatcher

result = NotificationDispatcher.dispatch(
    event_key='screen.offline',
    payload={
        'screen_id': 'xxx',
        'screen_name': 'Main Display',
        'offline_duration_seconds': 600
    },
    organization=user,
    severity='warning'
)
```

## Event Triggers

Notifications are automatically triggered for:

- **screen.offline**: Screen goes offline for >5 minutes
- **command.failed**: Command execution fails
- **content.sync_failed**: Content sync fails (max retries exceeded)
- **schedule.execution_failed**: Schedule execution fails
- **security.rate_limit_breach**: Rate limit exceeded
- **security.invalid_signature**: Invalid HMAC signature
- **security.replay_attempt**: Replay attack detected
- **security.invalid_timestamp**: Invalid timestamp

## Security Features

- **Encrypted Configs**: Channel configurations encrypted at rest using Fernet
- **HMAC Signatures**: Webhook payloads signed with HMAC-SHA256
- **Replay Protection**: Nonce-based replay attack prevention
- **Rate Limiting**: Per-endpoint rate limiting for webhooks
- **Domain Allowlist**: Webhook domain validation
- **Input Validation**: Strict payload size and format validation
- **PII Masking**: Personal information masked in logs

## Testing

Run tests:
```bash
python manage.py test notifications
```

## Future Admin Panel Integration

The system is designed for future admin panel control:

- Enable/disable channels per organization
- Event → channel mapping via rules
- Severity filtering
- Cooldown configuration
- Test notifications
- Dry-run mode

All backend support is ready - only UI needed.

## Architecture

```
Event Trigger → NotificationDispatcher → Rule Resolution → Channel Adapters → Delivery
                     ↓
              Cooldown Check
              Deduplication
              Severity Filter
                     ↓
              NotificationLog (Audit)
```

## API Endpoints (Future)

Future DRF endpoints for admin panel:
- `/api/notifications/events/` - List events
- `/api/notifications/channels/` - Manage channels
- `/api/notifications/rules/` - Manage rules
- `/api/notifications/logs/` - View logs
- `/api/notifications/test/` - Send test notification

## Troubleshooting

### Notifications not sending

1. Check Celery worker is running (if async enabled)
2. Verify channel configuration is correct
3. Check NotificationLog for error messages
4. Ensure rules are enabled and channels are active

### Encryption errors

1. Ensure `NOTIFICATION_ENCRYPTION_KEY` is set
2. Key must be base64-encoded Fernet key
3. Regenerate key: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`

### Webhook delivery failures

1. Verify URL is HTTPS (required in production)
2. Check domain is in allowlist
3. Verify secret_key matches on both sides
4. Check webhook endpoint logs

