# ScreenGram - Digital Signage Management System

## 1. Project Overview

ScreenGram is a digital signage management platform that enables users to remotely manage digital displays (screens), create and schedule content templates, monitor screen health, and execute commands on remote devices.

**Problem it solves:**
- Centralized management of multiple digital signage displays
- Remote content deployment and scheduling
- Real-time monitoring of screen status and health
- Web-based content player for TVs and displays

**High-level explanation:**
The system consists of a Django REST API backend that manages screens, templates, content, and users, and a Vue.js frontend dashboard for administration. Screens connect via a web player (HTML/JavaScript) that renders templates in fullscreen mode. Communication happens via HTTP REST API and WebSocket connections for real-time updates.

## 2. Current Features

### Authentication & Users
- ✅ JWT-based authentication with access/refresh tokens
- ✅ Role-based access control (SuperAdmin, Admin, Operator, Manager, Viewer)
- ✅ User CRUD operations with permissions
- ✅ Account lockout after 5 failed login attempts (15-minute lockout)
- ✅ Password security (PBKDF2 hashing, strength validation, 8+ characters)
- ✅ User enumeration prevention
- ✅ Profile management (view/edit profile, change password, active sessions)
- ✅ Dynamic sidebar based on user permissions
- ✅ Audit logging for critical actions
- ⚠️ Session management exists but may need testing for edge cases

### Screens & Pairing
- ✅ Screen CRUD operations
- ✅ Screen pairing via 6-digit code or QR token (expires in 5 minutes)
- ✅ Screen status tracking (online/offline, last heartbeat)
- ✅ Health check endpoints and metrics
- ✅ Command queue management per screen
- ✅ Screen authentication via auth_token + secret_key
- ⚠️ Heartbeat endpoint exists but has documented 401 authentication issues (see Known Issues)
- ⚠️ Pairing works but credentials handling has been refactored (screen_id method added, legacy auth_token/secret_key method still supported)

### Web Player
- ✅ Fullscreen responsive player component
- ✅ Template polling (fetches template every 5 minutes)
- ✅ Layer-based rendering with proper z-indexing
- ✅ Widget rendering (supports image widgets currently)
- ✅ Responsive scaling (320px to 8K displays)
- ✅ Aspect ratio preservation using CSS transform: scale()
- ✅ Heartbeat functionality (sends periodic heartbeats to backend)
- ✅ Error handling with retry logic
- ✅ Credential management (localStorage for screen_id or auth_token/secret_key)
- ⚠️ Template rendering may show black screens if template has no active layers/widgets/content
- ⚠️ Only image widget type is fully implemented; video, text, webview, chart widgets exist in models but may not render

### Content Management
- ✅ Content CRUD operations
- ✅ Content upload for images, videos, webview files
- ✅ Storage management (local filesystem, S3 support configured)
- ✅ User-based directory structure (`users/user_{id}/{type}/`)
- ✅ File validation (type, size limits: 500MB max)
- ✅ Content download status tracking
- ✅ Content sync commands to screens
- ⚠️ Upload endpoint has documented 400 error issues (Content-Type header problems fixed, but other issues may persist)
- ⚠️ Preview reliability may be unstable (file_url generation issues documented)
- ⚠️ Media files may not save to expected local paths in some cases

### Templates / Widgets
- ✅ Template CRUD operations
- ✅ Hierarchical structure: Template → Layer → Widget → Content
- ✅ Layer management (position, size, z-index, background, opacity, animations)
- ✅ Widget management (position, size, type: image, video, text, clock, webview, chart)
- ✅ Content assignment to widgets (multiple content items per widget for playlists)
- ✅ Template activation on screens
- ✅ Template versioning field (version number stored)
- ⚠️ Template preview/visual editor not implemented (only data model)
- ⚠️ Template designer UI not implemented (create/edit via forms only)
- ⚠️ Some widget types (video, text, webview, chart, clock) may not render properly in web player

### Media Upload & Preview
- ✅ File upload via multipart/form-data
- ✅ File type validation (image: jpeg, png, gif, webp, svg; video: mp4, webm, ogg, quicktime)
- ✅ File size validation (500MB max)
- ✅ Hash-based integrity checking (SHA-256)
- ✅ Storage path generation with user-based organization
- ✅ URL generation for file access
- ⚠️ Upload 400 errors documented (Content-Type boundary issues fixed, other issues may remain)
- ⚠️ Preview not always reliable (file_url may not be accessible)
- ⚠️ Media files may not save correctly to local storage in some cases

### Heartbeat & Screen Status
- ✅ Heartbeat endpoint (`POST /api/screens/heartbeat/`)
- ✅ Screen status tracking (is_online, last_heartbeat_at)
- ✅ Stale heartbeat detection (5-minute timeout)
- ✅ Screen status logs (ScreenStatusLog model)
- ✅ Optional metrics (latency, CPU usage, memory usage)
- ✅ Management command to mark offline screens (`check_heartbeats`)
- ⚠️ Heartbeat 401 errors documented - authentication issues with request body parsing
- ⚠️ Heartbeat endpoint has multiple credential extraction methods but may fail in some scenarios

### Schedules
- ✅ Schedule CRUD operations
- ✅ Time-based scheduling (start_time, end_time)
- ✅ Repeat types (none, daily, weekly, monthly)
- ✅ Priority-based conflict resolution
- ✅ Schedule execution on screens
- ✅ Recurrence calculation for repeat schedules
- ⚠️ Schedule execution may not work correctly for all repeat types

### Commands
- ✅ Command queue system
- ✅ Command types (restart, refresh, change_template, display_message, sync_content, custom)
- ✅ Command priority and expiration
- ✅ Command execution status tracking
- ✅ Command execution logs
- ✅ Command pull endpoint for screens
- ✅ Command response endpoint for screens
- ⚠️ Command execution via WebSocket may not be fully reliable (HTTP fallback exists)

### Analytics & Logging
- ✅ Analytics dashboard endpoints
- ✅ Screen status logs
- ✅ Content download logs
- ✅ Command execution logs
- ✅ Error logging (Super Admin only)
- ✅ Audit logs for critical actions
- ✅ Log filtering and export

### Core Infrastructure
- ✅ Backup system (database and media backups)
- ✅ Rate limiting (configurable per role, per endpoint)
- ✅ Caching (Redis/LocMem cache)
- ✅ Error logging middleware
- ⚠️ Automated backup scheduling configured but may need Celery workers

## 3. Current Architecture

### Backend Stack
- **Framework**: Django 5.2+ with Django REST Framework
- **Database**: SQLite (default) or PostgreSQL (production)
- **Authentication**: JWT (djangorestframework-simplejwt)
- **WebSocket**: Django Channels (in-memory channel layer in dev, Redis for production)
- **Storage**: Local filesystem (default) or Amazon S3
- **Caching**: Redis (production) or LocMemCache (development)
- **Task Queue**: Celery (configured, but may need workers running)
- **API Documentation**: drf-spectacular (Swagger/OpenAPI)

### Frontend Stack
- **Framework**: Vue.js 3.4+ with Composition API
- **Build Tool**: Vite 5.1+
- **Router**: Vue Router 4.3+
- **State Management**: Pinia 2.1+
- **HTTP Client**: Axios
- **Styling**: Tailwind CSS 3.4+
- **Charts**: Chart.js with vue-chartjs
- **Icons**: Heroicons

### Media Storage Approach
- **Local Storage**: Files stored in `BackEnd/media/users/user_{user_id}/{type}/`
- **S3 Storage**: Configured but requires `USE_S3_STORAGE=True` and AWS credentials
- **File Organization**: User-based directory structure
- **File Naming**: `{type}_{uuid}.{ext}` format
- **URL Generation**: `/media/users/user_{id}/{type}/...` for local, signed URLs for S3
- **Hash Verification**: SHA-256 hashes stored for integrity checking

### Screen ↔ User Connection Flow

1. **Pairing Flow**:
   - User generates pairing session via `/api/pairing/generate/` (returns 6-digit code + pairing_token)
   - Screen displays pairing code and QR code (contains pairing_token)
   - User enters pairing code or scans QR code in dashboard
   - Dashboard calls `/api/pairing/bind/` with pairing_code/token
   - Backend creates Screen record and links to user
   - Screen polls `/api/pairing/status/` until status becomes "paired"
   - Screen receives auth_token and secret_key (or screen_id for new method)

2. **Authentication**:
   - Screen authenticates using auth_token + secret_key (or screen_id)
   - Credentials stored in localStorage on screen
   - Heartbeat endpoint accepts both methods

3. **Communication**:
   - HTTP REST API for commands and template fetching
   - WebSocket for real-time updates (if available)
   - Polling fallback (template polling every 5 minutes, heartbeat every 30-60 seconds)

### Web Player Lifecycle

1. **Initialization**:
   - Load credentials from localStorage, URL params, or env vars
   - Fetch template from `/api/player/template/` endpoint
   - Initialize responsive scaling

2. **Rendering**:
   - Render template container with proper dimensions
   - Render layers in z-index order
   - Render widgets within layers
   - Render content within widgets (currently image widgets)

3. **Updates**:
   - Poll template every 5 minutes
   - Send heartbeat every 30-60 seconds
   - Handle window resize events (debounced)

4. **Error Handling**:
   - Retry on network errors
   - Show error messages on screen
   - Fallback to cached template if available

## 4. Known Issues & Limitations

### Upload Issues (400 Errors)
- **Issue**: Content upload endpoint (`POST /api/contents/{id}/upload/`) may return 400 errors
- **Status**: Content-Type header boundary issue has been fixed, but other issues may persist
- **Symptoms**: "File is required" error even when file is sent, validation errors
- **Documentation**: See `CONTENT_UPLOAD_DEBUG_GUIDE.md` (to be removed)
- **Workaround**: Ensure FormData is sent correctly, check browser Network tab for request format

### Preview Problems
- **Issue**: Content preview may not display correctly after upload
- **Possible Causes**: 
  - `file_url` not generated correctly
  - `MEDIA_URL` not configured properly
  - CORS issues preventing file access
  - File not actually saved to disk
- **Status**: Needs investigation

### Heartbeat 401 Issues
- **Issue**: Heartbeat endpoint (`POST /api/screens/heartbeat/`) may return 401 Unauthorized
- **Status**: Multiple fixes applied (request body parsing, credential extraction from multiple sources)
- **Symptoms**: "Authentication credentials were not provided" even when credentials are sent
- **Documentation**: See `HEARTBEAT_401_FIX.md` (to be removed)
- **Workaround**: Ensure credentials are sent in POST body as JSON, check backend logs for parsing issues

### Template Black Screen Problems
- **Issue**: Web player may show black screen when rendering templates
- **Possible Causes**:
  - Template has no active layers
  - Template has no active widgets
  - Template has no active content
  - Invalid template dimensions (width/height = 0)
- **Status**: Template validation exists but may not catch all cases
- **Workaround**: Verify template has active layers, widgets, and content before activating

### Media Not Saving Locally
- **Issue**: Uploaded files may not save to expected local paths
- **Possible Causes**:
  - `MEDIA_ROOT` directory doesn't exist
  - Permission issues (directory not writable)
  - Storage path generation errors
  - Storage backend misconfiguration
- **Status**: Needs investigation
- **Workaround**: Verify `BackEnd/media/` directory exists and is writable

### Missing Validations
- Template activation on offline screens (allows activation but content won't sync)
- Content type validation may not catch all invalid files
- Widget type rendering (only image widgets fully implemented)

### Missing Permissions
- Some endpoints may not have proper permission checks
- Bulk operations may not check permissions for all affected resources
- Template/widget/content access may not respect organization boundaries in all cases

### Partial Implementations
- **Video Widgets**: Models exist but rendering not implemented in web player
- **Text Widgets**: Models exist but rendering not implemented
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

### Database
- SQLite used by default (not suitable for production with multiple concurrent users)
- No database migrations strategy documented
- No database backup/restore procedure documented

### Deployment
- No production deployment guide
- Nginx configuration example exists but may need updates
- Environment variables not fully documented
- No Docker/containerization setup

---

**Last Updated**: 2024  
**Status**: Active Development - See FuturePlans.md for roadmap
