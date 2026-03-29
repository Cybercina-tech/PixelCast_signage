# PixelCast Signage - Digital Signage Management System

## 1. Project Overview

**What this system is:**
PixelCast Signage is a centralized web-based platform for managing multiple digital signage displays. It consists of a Django REST API backend and a Vue.js frontend dashboard. Screens connect via a web player (HTML/JavaScript) that renders templates in fullscreen mode.

**What problem it solves:**
- Centralized management of multiple digital signage displays
- Remote content deployment and scheduling
- Real-time monitoring of screen status and health
- Web-based content player for TVs and displays
- Template-based content creation and management

**High-level explanation:**
The system uses a Django REST API backend to manage screens, templates, content, and users. A Vue.js frontend provides the administration dashboard. Screens connect via a web player that renders templates in fullscreen mode. Communication happens via HTTP REST API and WebSocket connections (Django Channels) for real-time updates.

## 2. Current Features

### Authentication & Users
- ✅ JWT-based authentication with access/refresh tokens (60-minute access, 7-day refresh)
- ✅ Role-based access control (SuperAdmin, Admin, Operator, Manager, Viewer)
- ✅ User CRUD operations with permissions
- ✅ Account lockout after 5 failed login attempts (15-minute lockout duration)
- ✅ Password security (PBKDF2 hashing, strength validation, 8+ characters, similarity checks)
- ✅ User enumeration prevention
- ✅ Profile management (view/edit profile, change password, active sessions)
- ✅ Dynamic sidebar based on user permissions
- ✅ Audit logging for critical actions
- ✅ Multi-tenant organization support (organization_name field)
- ⚠️ Session management exists but may need testing for edge cases
- ⚠️ Email verification system exists but may not be fully implemented

### Screens & Pairing
- ✅ Screen CRUD operations
- ✅ Screen pairing via 6-digit code or QR token (expires in 5 minutes)
- ✅ Screen status tracking (is_online, last_heartbeat_at)
- ✅ Health check endpoints and metrics
- ✅ Command queue management per screen
- ✅ Screen authentication via auth_token + secret_key OR screen_id (multiple methods)
- ✅ Device information tracking (app_version, OS version, screen dimensions, brightness, orientation)
- ✅ IP address tracking (last_ip field)
- ✅ Pairing session cleanup management command
- ✅ ScreenConnectionRegistry for WebSocket connection management
- ⚠️ Heartbeat endpoint has documented 401 authentication issues (see Known Issues)
- ⚠️ Pairing works but credentials handling has been refactored (screen_id method added, legacy auth_token/secret_key method still supported)

### Web Player
- ✅ Fullscreen responsive player component
- ✅ Template polling (fetches template every 5 minutes from `/iot/player/template/`)
- ✅ Layer-based rendering with proper z-indexing
- ✅ Widget rendering (supports image widgets currently)
- ✅ Responsive scaling (320px to 8K displays) using CSS transform: scale()
- ✅ Aspect ratio preservation
- ✅ Heartbeat functionality (sends periodic heartbeats to backend every 30-60 seconds)
- ✅ Error handling with retry logic
- ✅ Credential management (localStorage for screen_id or auth_token/secret_key)
- ✅ Unpaired state handling with redirect to pairing page
- ⚠️ Template rendering may show black screens if template has no active layers/widgets/content
- ⚠️ Only image widget type is fully implemented; video, text, webview, chart widgets exist in models but may not render properly
- ⚠️ VideoWidget.vue and TextWidget.vue components exist but may be incomplete

### Content Management
- ✅ Content CRUD operations
- ✅ Content upload for images, videos, webview files
- ✅ Storage management (local filesystem, S3 support configured but not required)
- ✅ User-based directory structure (`users/user_{id}/{type}/`)
- ✅ File validation (type, size limits: 500MB max)
- ✅ Content download status tracking (pending, success, failed)
- ✅ Content sync commands to screens
- ✅ Hash-based integrity checking (SHA-256)
- ✅ Secure URL generation (signed URLs for S3, regular URLs for local)
- ✅ ContentStorageManager with comprehensive validation
- ✅ Content retry mechanism (max 3 retries)
- ⚠️ Upload endpoint has documented 400 error issues (Content-Type header boundary issues fixed, but other issues may persist)
- ⚠️ Preview reliability may be unstable (file_url generation issues documented)
- ⚠️ Media files may not save to expected local paths in some cases

### Templates / Widgets
- ✅ Template CRUD operations
- ✅ Hierarchical structure: Template → Layer → Widget → Content
- ✅ Layer management (position, size, z-index, background, opacity, animations: fade, slide)
- ✅ Widget management (position, size, type: image, video, text, clock, webview, chart)
- ✅ Content assignment to widgets (multiple content items per widget for playlists/slideshows)
- ✅ Template activation on screens (atomic transaction)
- ✅ Template versioning field (version number stored)
- ✅ Template configuration via JSON (config_json, meta_data)
- ✅ Template thumbnail support
- ⚠️ Template preview/visual editor not implemented (only data model)
- ⚠️ Template designer UI not implemented (create/edit via forms only)
- ⚠️ Some widget types (video, text, webview, chart, clock) may not render properly in web player
- ⚠️ Widget animations not implemented in player

### Media Upload & Preview
- ✅ File upload via multipart/form-data
- ✅ File type validation (image: jpeg, png, gif, webp, svg; video: mp4, webm, ogg, quicktime)
- ✅ File size validation (500MB max)
- ✅ Hash-based integrity checking (SHA-256)
- ✅ Storage path generation with user-based organization
- ✅ URL generation for file access
- ✅ Content validation module with security checks
- ⚠️ Upload 400 errors documented (Content-Type boundary issues fixed, other issues may remain)
- ⚠️ Preview not always reliable (file_url may not be accessible)
- ⚠️ Media files may not save correctly to local storage in some cases

### Heartbeat & Screen Status
- ✅ Heartbeat endpoint (`POST /api/screens/heartbeat/` and `/iot/screens/heartbeat/`)
- ✅ Screen status tracking (is_online, last_heartbeat_at)
- ✅ Stale heartbeat detection (5-minute timeout)
- ✅ Screen status logs (ScreenStatusLog model)
- ✅ Optional metrics (latency, CPU usage, memory usage)
- ✅ Management command to mark offline screens (`check_heartbeats`)
- ✅ WebSocket heartbeat support (via ScreenConnectionRegistry)
- ✅ Multiple credential extraction methods (screen_id, auth_token/secret_key, URL params, env vars)
- ⚠️ Heartbeat 401 errors documented - authentication issues with request body parsing
- ⚠️ Heartbeat endpoint has multiple credential extraction methods but may fail in some scenarios

### Schedules
- ✅ Schedule CRUD operations
- ✅ Time-based scheduling (start_time, end_time)
- ✅ Repeat types (none, daily, weekly, monthly)
- ✅ Priority-based conflict resolution
- ✅ Schedule execution on screens
- ✅ Recurrence calculation for repeat schedules (SecureRecurrenceCalculator)
- ✅ Schedule status tracking (is_active, is_currently_running)
- ✅ Schedule conflict detection
- ⚠️ Schedule execution may not work correctly for all repeat types
- ⚠️ Timezone support not fully implemented (uses UTC)

### Commands
- ✅ Command queue system
- ✅ Command types (restart, refresh, change_template, display_message, sync_content, custom)
- ✅ Command priority and expiration
- ✅ Command execution status tracking (pending, executing, done, failed)
- ✅ Command execution logs (CommandExecutionLog)
- ✅ Command pull endpoint for screens (`/iot/commands/pending/`)
- ✅ Command response endpoint for screens (`/iot/commands/{id}/status/`)
- ✅ WebSocket command delivery (with HTTP fallback)
- ✅ Command security (HMAC signing via ScreenSecurity, nonce protection, timestamp validation)
- ✅ ScreenConnectionRegistry for WebSocket management
- ⚠️ Command execution via WebSocket may not be fully reliable (HTTP fallback exists)
- ⚠️ Command retry logic exists but may need improvement

### Analytics & Logging
- ✅ Analytics dashboard endpoints
- ✅ Screen status logs (ScreenStatusLog)
- ✅ Content download logs (ContentDownloadLog)
- ✅ Command execution logs (CommandExecutionLog)
- ✅ Error logging (Super Admin only, ErrorDashboard component)
- ✅ Audit logs for critical actions (AuditLog model)
- ✅ Log filtering and export
- ✅ Centralized logging middleware (ErrorLoggingMiddleware)
- ⚠️ Analytics may not have comprehensive reporting features

### Core Infrastructure
- ✅ Backup system (database and media backups) - SystemBackup model
- ✅ Rate limiting (configurable per role, per endpoint)
- ✅ Caching (Redis/LocMem cache)
- ✅ Error logging middleware
- ✅ Content validation module
- ✅ Bulk operations support
- ✅ Celery configuration for async tasks
- ✅ Notification system (encrypted notifications, async delivery)
- ✅ Installation wizard with environment configuration
- ✅ Docker containerization with auto-migration entrypoint
- ✅ GitHub webhook deployment automation
- ⚠️ Automated backup scheduling configured but may need Celery workers running
- ⚠️ Redis cache requires USE_REDIS_CACHE=True in production

## 3. Current Architecture

### Backend Stack
- **Framework**: Django 5.2+ with Django REST Framework
- **Database**: SQLite (default, USE_SQLITE=True) or PostgreSQL (production)
- **Authentication**: JWT (djangorestframework-simplejwt)
- **WebSocket**: Django Channels (in-memory channel layer in dev, Redis for production)
- **Storage**: Local filesystem (default) or Amazon S3 (USE_S3_STORAGE=True)
- **Caching**: Redis (production, USE_REDIS_CACHE=True) or LocMemCache (development)
- **Task Queue**: Celery (configured, but may need workers running)
- **API Documentation**: drf-spectacular (Swagger/OpenAPI)
- **Deployment**: Docker with docker-compose, auto-deployment via GitHub webhooks

### Frontend Stack
- **Framework**: Vue.js 3.4+ with Composition API
- **Build Tool**: Vite 5.1+
- **Router**: Vue Router 4.3+
- **State Management**: Pinia 2.1+
- **HTTP Client**: Axios
- **Styling**: Tailwind CSS 3.4+
- **Charts**: Chart.js with vue-chartjs
- **Icons**: Heroicons
- **Theme**: Aether (Light) and Cosmic (Dark) themes with CSS variables

### Media Storage Approach
- **Local Storage**: Files stored in `BackEnd/media/users/user_{user_id}/{type}/`
- **S3 Storage**: Configured but requires `USE_S3_STORAGE=True` and AWS credentials
- **File Organization**: User-based directory structure
- **File Naming**: `{type}_{uuid}.{ext}` format
- **URL Generation**: `/media/users/user_{id}/{type}/...` for local, signed URLs for S3
- **Hash Verification**: SHA-256 hashes stored for integrity checking
- **Storage Manager**: ContentStorageManager handles all storage operations

### Screen ↔ User Connection Flow

1. **Pairing Flow**:
   - User generates pairing session via `POST /api/pairing/generate/` (returns 6-digit code + pairing_token)
   - Screen displays pairing code and QR code (contains pairing_token)
   - User enters pairing code or scans QR code in dashboard
   - Dashboard calls `POST /api/pairing/bind/` with pairing_code/token
   - Backend creates Screen record and links to user (atomic transaction with select_for_update)
   - Screen polls `GET /api/pairing/status/` until status becomes "paired"
   - Screen receives auth_token and secret_key (or screen_id for new method)

2. **Authentication**:
   - Screen authenticates using auth_token + secret_key OR screen_id
   - Credentials stored in localStorage on screen
   - Heartbeat endpoint accepts both methods (multiple extraction strategies: request body, query params, env vars)

3. **Communication**:
   - HTTP REST API for commands and template fetching
   - WebSocket for real-time updates (if available via ScreenConnectionRegistry)
   - Polling fallback (template polling every 5 minutes, heartbeat every 30-60 seconds)
   - Command pull endpoint for screens (`GET /iot/commands/pending/?screen_id=...`)

### Web Player Lifecycle

1. **Initialization**:
   - Load credentials from localStorage, URL params, or env vars
   - Fetch template from `GET /api/player/template/` or `GET /iot/player/template/?screen_id=...` endpoint
   - Initialize responsive scaling (useResponsiveScaling composable)

2. **Rendering**:
   - Render template container with proper dimensions
   - Render layers in z-index order (LayerRenderer component)
   - Render widgets within layers (WidgetRenderer component)
   - Render content within widgets (currently ImageWidget.vue, VideoWidget.vue and TextWidget.vue exist but may be incomplete)

3. **Updates**:
   - Poll template every 5 minutes
   - Send heartbeat every 30-60 seconds to `/iot/screens/heartbeat/`
   - Handle window resize events (debounced)

4. **Error Handling**:
   - Retry on network errors
   - Show error messages on screen
   - Fallback to cached template if available
   - Redirect to pairing page if unpaired

### Docker development (hot reload)

- **Command:** `docker compose -f docker-compose.yml -f docker-compose.dev.yml up db redis backend frontend-dev`
- **App (Vite HMR):** http://localhost:5173 — proxies `/api` to the backend container
- **Django (auto-reload):** http://localhost:8000 — `./BackEnd` is bind-mounted to `/app`
- **Environment file:** host `./.env` is mounted at **`/config/.env`** in the backend container (isolated from the code mount); `PIXELCAST_SIGNAGE_ENV_FILE=/config/.env`
- **Skip wizard:** set `PIXELCAST_SIGNAGE_INSTALLED=true` in `.env`, or rely on `installed.lock` after installation

## 4. Known Issues & Limitations

### Upload Issues (400 Errors)
- **Issue**: Content upload endpoint (`POST /api/contents/{id}/upload/`) may return 400 errors
- **Status**: Content-Type header boundary issue has been fixed, but other issues may persist
- **Symptoms**: "File is required" error even when file is sent, validation errors
- **Workaround**: Ensure FormData is sent correctly, check browser Network tab for request format
- **Root Cause**: May be related to MultiPartParser configuration or file validation logic in ContentStorageManager

### Preview Problems
- **Issue**: Content preview may not display correctly after upload
- **Possible Causes**: 
  - `file_url` not generated correctly by ContentStorageManager
  - `MEDIA_URL` not configured properly in settings
  - CORS issues preventing file access
  - File not actually saved to disk (storage backend issue)
- **Status**: Needs investigation
- **Workaround**: Check file_url in content details, verify file exists in media directory

### Heartbeat 401 Issues
- **Issue**: Heartbeat endpoint (`POST /api/screens/heartbeat/` or `/iot/screens/heartbeat/`) may return 401 Unauthorized
- **Status**: Multiple fixes applied (request body parsing, credential extraction from multiple sources: body, query params, env vars)
- **Symptoms**: "Authentication credentials were not provided" even when credentials are sent
- **Workaround**: Ensure credentials are sent in POST body as JSON, check backend logs for parsing issues
- **Root Cause**: Complex credential extraction logic may fail in edge cases (screen_id vs auth_token/secret_key)

### Template Black Screen Problems
- **Issue**: Web player may show black screen when rendering templates
- **Possible Causes**:
  - Template has no active layers
  - Template has no active widgets
  - Template has no active content
  - Invalid template dimensions (width/height = 0)
  - Widget renderer not implemented for widget type
  - Content file_url is invalid or inaccessible
- **Status**: Template validation exists but may not catch all cases
- **Workaround**: Verify template has active layers, widgets, and content before activating

### Media Not Saving Locally
- **Issue**: Uploaded files may not save to expected local paths
- **Possible Causes**:
  - `MEDIA_ROOT` directory doesn't exist
  - Permission issues (directory not writable)
  - Storage path generation errors in ContentStorageManager
  - Storage backend misconfiguration
- **Status**: Needs investigation
- **Workaround**: Verify `BackEnd/media/` directory exists and is writable, check storage logs

### Missing Validations
- Template activation on offline screens (allows activation but content won't sync)
- Content type validation may not catch all invalid files
- Widget type rendering (only image widgets fully implemented)
- Schedule timezone validation (timezone support not fully implemented, uses UTC)

### Missing Permissions
- Some endpoints may not have proper permission checks
- Bulk operations may not check permissions for all affected resources
- Template/widget/content access may not respect organization boundaries in all cases

### Partial Implementations
- **Video Widgets**: Models exist, VideoWidget.vue component exists but rendering may not be fully implemented
- **Text Widgets**: Models exist, TextWidget.vue component exists but rendering may not be fully implemented
- **Webview Widgets**: Models exist but rendering not implemented
- **Chart Widgets**: Models exist but rendering not implemented
- **Clock Widgets**: Models exist but rendering not implemented
- **Template Preview**: No visual preview in dashboard (only data editing)
- **Template Designer**: No drag-and-drop designer UI
- **Schedule Execution**: May not work correctly for all repeat types

### Performance Considerations
- Template polling every 5 minutes may be too frequent for many screens
- Heartbeat frequency may need adjustment (currently 30-60 seconds)
- Large file uploads may timeout (500MB max)
- No CDN integration for media files (S3 can be used but not required)
- Database queries may not be optimized for large datasets (select_related/prefetch_related not used everywhere)

### Database
- SQLite used by default (not suitable for production with multiple concurrent users)
- PostgreSQL recommended for production (configured in docker-compose.yml)
- Database migrations run automatically on container startup via entrypoint.sh

### Deployment
- Docker containerization fully implemented
- Auto-migration on container startup
- GitHub webhook deployment automation available
- Environment variables documented in env.example
- Celery workers need to be started separately for async tasks
- Redis required for production WebSocket and caching

### Upgrading from legacy ScreenGram-branded installs
- Default PostgreSQL database and user names are now `pixelcast_signage_db` / `pixelcast_signage_user` (see `env.example`). Point `DB_NAME` / `DB_USER` at your existing database if you are not creating a fresh instance.
- Docker Compose **named volumes** were renamed (e.g. `pixelcast-signage_postgres_data`). To keep existing data, either copy data into the new volumes or temporarily map volume `name:` values in `docker-compose.yml` back to your previous volume names.
- Legacy environment variables `SCREENGRAM_ENV_FILE` and `SCREENGRAM_INSTALLED` are still honored alongside `PIXELCAST_SIGNAGE_ENV_FILE` and `PIXELCAST_SIGNAGE_INSTALLED`.

---

**Last Updated**: 2024  
**Status**: Active Development - See FuturePlans.md for roadmap
