# PixelCast Signage - Future Plans & Roadmap

This document outlines planned improvements, fixes, and enhancements for the PixelCast Signage Digital Signage Management System.

## 1. Short-Term Fixes (Critical)

### Upload System Stabilization
**Priority**: 🔴 High  
**Status**: Partially fixed

- ✅ Fixed Content-Type header boundary issue
- ❌ Investigate remaining 400 errors
- ❌ Improve error messages and logging
- ❌ Add comprehensive file validation
- ❌ Fix file path generation edge cases
- ❌ Test with various file types and sizes
- ❌ Add retry logic for failed uploads
- ❌ Verify ContentStorageManager handles all edge cases
- ❌ Add file upload progress indicators in frontend

**Impact**: Users cannot reliably upload content, blocking core functionality.

### Media Storage Refactor
**Priority**: 🔴 High  
**Status**: Partially implemented

- ✅ ContentStorageManager exists with validation
- ✅ User-based directory structure implemented
- ❌ Standardize storage path generation across all code paths
- ❌ Add storage backend abstraction layer improvements
- ❌ Implement per-user quota management
- ❌ Add storage cleanup for orphaned files
- ❌ Improve S3 integration and testing
- ❌ Add storage migration tools
- ❌ Document storage configuration thoroughly
- ❌ Verify MEDIA_ROOT directory creation on startup

**Impact**: Prevents storage issues and makes S3 integration reliable.

### Preview Reliability
**Priority**: 🔴 High  
**Status**: Not started

- ❌ Fix file_url generation in ContentStorageManager
- ❌ Ensure MEDIA_URL is properly configured
- ❌ Add file existence verification before serving
- ❌ Implement proper CORS for media files
- ❌ Add preview caching
- ❌ Support for video previews
- ❌ Add preview error handling with user-friendly messages
- ❌ Verify file accessibility after upload

**Impact**: Users cannot verify uploaded content before activating on screens.

### Auth & Heartbeat Fixes
**Priority**: 🔴 High  
**Status**: Partially fixed

- ✅ Added multiple credential extraction methods (body, query params, env vars)
- ✅ Added request body parsing fallbacks
- ✅ ScreenConnectionRegistry for WebSocket management
- ✅ IoT endpoints with @authentication_classes([]) and @permission_classes([AllowAny])
- ❌ Fully resolve 401 authentication issues
- ❌ Test all credential scenarios (screen_id, auth_token/secret_key, URL params, env vars)
- ❌ Add comprehensive logging and monitoring
- ❌ Improve error messages for debugging
- ❌ Add automatic retry with exponential backoff
- ❌ Simplify credential extraction logic
- ❌ Add heartbeat authentication test suite

**Impact**: Screens cannot reliably report status, breaking monitoring and command execution.

### Screen Pairing Robustness
**Priority**: 🟡 Medium  
**Status**: Partially implemented

- ✅ Pairing session creation and binding
- ✅ Screen credential generation
- ✅ Atomic transaction for pairing (select_for_update)
- ✅ Pairing session cleanup management command
- ❌ Improve pairing expiration handling
- ❌ Add pairing session cleanup automation (scheduled task)
- ❌ Improve error messages for pairing failures
- ❌ Add pairing retry mechanism
- ❌ Test pairing flow edge cases
- ❌ Add pairing session monitoring dashboard

**Impact**: Users may experience pairing failures, requiring manual intervention.

## 2. Mid-Term Improvements

### Proper Template + Widget + Layer System
**Priority**: 🔴 High  
**Status**: Models exist, rendering incomplete

- ✅ Template, Layer, Widget, Content models fully implemented
- ✅ Image widget rendering implemented (ImageWidget.vue)
- ✅ VideoWidget.vue and TextWidget.vue components exist
- ❌ Complete video widget rendering implementation
- ❌ Complete text widget rendering implementation
- ❌ Implement webview widget renderer
- ❌ Implement chart widget renderer
- ❌ Implement clock widget renderer
- ❌ Add widget animation support
- ❌ Implement layer animations
- ❌ Add widget positioning tools in UI
- ❌ Improve widget resize/snap functionality
- ❌ Add widget templates/library
- ❌ Implement widget data binding for dynamic content

**Impact**: Limited widget types available, reducing content flexibility.

### Dynamic Data Fields (Prices, Menus, etc.)
**Priority**: 🟡 Medium  
**Status**: Not started

- ❌ Design dynamic data field system
- ❌ Add data source integration (API, CSV, database)
- ❌ Implement data refresh mechanisms
- ❌ Add data validation and error handling
- ❌ Create widget data binding UI
- ❌ Add caching for external data sources
- ❌ Document data field API
- ❌ Add data source authentication/authorization

**Impact**: Templates cannot display dynamic/real-time data (prices, menus, weather, etc.).

### Better Responsive Web Player (TV Sizes)
**Priority**: 🟡 Medium  
**Status**: Basic implementation exists

- ✅ Responsive scaling implemented (useResponsiveScaling composable)
- ✅ CSS transform: scale() for aspect ratio preservation
- ❌ Improve scaling algorithm for large displays (8K+)
- ❌ Add display-specific optimizations
- ❌ Implement adaptive quality based on screen size
- ❌ Add performance monitoring
- ❌ Optimize rendering for low-end devices
- ❌ Add display calibration tools
- ❌ Improve template container sizing logic

**Impact**: May not render optimally on very large displays or low-end devices.

### Monitoring (CPU / RAM / Latency)
**Priority**: 🟢 Low  
**Status**: Partially implemented

- ✅ Heartbeat accepts optional metrics (CPU, RAM, latency)
- ✅ ScreenStatusLog model stores metrics
- ❌ Add metrics dashboard in admin
- ❌ Implement metrics alerting
- ❌ Add historical metrics storage and retention
- ❌ Create metrics visualization (charts, graphs)
- ❌ Add performance benchmarking
- ❌ Document metrics collection
- ❌ Add metrics export functionality

**Impact**: Limited visibility into screen performance and health.

### Content Scheduling Enhancements
**Priority**: 🟡 Medium  
**Status**: Basic scheduling exists

- ✅ Basic scheduling with repeat types (none, daily, weekly, monthly)
- ✅ SecureRecurrenceCalculator for accurate recurrence
- ✅ Schedule conflict detection
- ❌ Improve schedule conflict resolution UI
- ❌ Add schedule preview/validation
- ❌ Implement timezone support (currently UTC only)
- ❌ Add schedule templates
- ❌ Improve recurrence calculation accuracy for edge cases
- ❌ Add schedule analytics
- ❌ Add schedule execution monitoring

**Impact**: Scheduling may not work correctly for complex scenarios or timezone-aware schedules.

### Template Preview & Designer
**Priority**: 🟡 Medium  
**Status**: Not started

- ❌ Implement visual template preview in dashboard
- ❌ Create drag-and-drop template designer
- ❌ Add layer/widget positioning tools
- ❌ Implement template templates/library
- ❌ Add template export/import (JSON)
- ❌ Create template versioning UI
- ❌ Add template collaboration features
- ❌ Add template thumbnail generation

**Impact**: Users must create templates via forms without visual feedback.

## 3. Long-Term Vision

### Scalability
**Priority**: 🔴 High  
**Status**: Not started

- ❌ Database optimization (indexes, query optimization, select_related/prefetch_related)
- ❌ Implement database connection pooling
- ❌ Add horizontal scaling support
- ❌ Implement load balancing
- ❌ Add caching layers (Redis for sessions, templates, content)
- ❌ Optimize media delivery (CDN integration)
- ❌ Add database read replicas
- ❌ Implement message queue for async operations (Celery already configured)
- ❌ Add database query monitoring and optimization

**Impact**: System may not handle large numbers of screens/users efficiently.

### Multi-Screen Management
**Priority**: 🟡 Medium  
**Status**: Basic support exists

- ✅ Screen CRUD operations
- ✅ Screen grouping by owner/organization
- ❌ Add screen groups/organizations UI
- ❌ Implement bulk operations UI
- ❌ Add screen templates/profiles
- ❌ Create screen assignment workflows
- ❌ Add screen location mapping (geographic)
- ❌ Implement screen hierarchy (parent/child screens)
- ❌ Add screen search and filtering

**Impact**: Managing many screens is cumbersome without grouping/organization.

### Content Scheduling Enhancements
**Priority**: 🟡 Medium  
**Status**: Basic scheduling exists

- ✅ Schedule creation and execution
- ✅ Conflict detection and resolution
- ❌ Add advanced scheduling (complex recurrences, timezone support)
- ❌ Implement schedule preview
- ❌ Add schedule analytics and reporting
- ❌ Create schedule templates
- ❌ Implement conditional scheduling (based on events)
- ❌ Add schedule conflict prevention UI
- ❌ Add schedule execution history

**Impact**: Limited scheduling flexibility may not meet all use cases.

### Analytics & Reporting
**Priority**: 🟢 Low  
**Status**: Basic analytics exist

- ✅ Basic analytics dashboard
- ✅ Analytics store and components exist
- ❌ Add comprehensive reporting system
- ❌ Implement custom report builder
- ❌ Add export functionality (PDF, CSV, Excel)
- ❌ Create report scheduling
- ❌ Add data visualization improvements
- ❌ Implement analytics API
- ❌ Add real-time analytics

**Impact**: Limited insights into system usage and performance.

### Offline / Fallback Modes
**Priority**: 🟡 Medium  
**Status**: Not implemented

- ❌ Implement offline content caching on screens
- ❌ Add fallback template support
- ❌ Create offline mode detection
- ❌ Implement content sync on reconnection
- ❌ Add offline diagnostics
- ❌ Create offline playback mode
- ❌ Document offline behavior
- ❌ Add offline content versioning

**Impact**: Screens may not display content when network is unavailable.

### Advanced Features
**Priority**: 🟢 Low  
**Status**: Not started

- ❌ Multi-language support
- ❌ Custom branding/theming
- ❌ White-label options
- ❌ API rate limiting per user/organization (currently per role)
- ❌ Webhook support for events
- ❌ Third-party integrations
- ❌ Plugin system for custom widgets
- ❌ Mobile app for screen management

**Impact**: Limited customization and integration options.

## 4. Technical Suggestions

### Folder Structure Improvements
**Priority**: 🟢 Low  
**Status**: Current structure is acceptable

- Consider separating API apps more clearly
- Add shared utilities module
- Better organization of serializers
- Separate business logic from views (service layer pattern)
- Add API versioning structure (v1/, v2/)

### Media Storage Per-User
**Priority**: 🟡 Medium  
**Status**: Partially implemented

- ✅ User-based directory structure exists
- ❌ Add user quota management
- ❌ Implement storage cleanup for deleted users
- ❌ Add storage usage reporting
- ❌ Implement storage migration tools
- ❌ Add storage usage dashboard

### API Consistency
**Priority**: 🟡 Medium  
**Status**: Generally consistent

- Standardize error response format across all endpoints
- Implement consistent pagination
- Add API versioning (v1, v2, etc.)
- Improve API documentation (beyond Swagger)
- Add API deprecation strategy
- Standardize authentication methods across endpoints

### Validation & Error Handling
**Priority**: 🟡 Medium  
**Status**: Basic validation exists

- Add comprehensive input validation
- Implement consistent error responses
- Add validation error aggregation
- Improve client-side validation
- Add server-side validation testing
- Add validation error logging

### Security Improvements
**Priority**: 🔴 High  
**Status**: Good security foundation

- ✅ JWT authentication, RBAC, account lockout implemented
- ✅ Command security (HMAC signing, nonce protection)
- ✅ Screen authentication via auth_token/secret_key or screen_id
- ❌ Add rate limiting per user (currently per role)
- ❌ Implement API key authentication for screens (alternative to JWT)
- ❌ Add request signing for screen commands (enhance existing)
- ❌ Improve CORS configuration
- ❌ Add security headers (CSP, HSTS, etc.)
- ❌ Implement audit log retention policies
- ❌ Add security monitoring and alerting
- ❌ Add input sanitization for all user inputs

### Testing
**Priority**: 🟡 Medium  
**Status**: Limited testing

- Add comprehensive unit tests
- Implement integration tests
- Add end-to-end tests
- Create test data fixtures
- Add performance/load testing
- Document testing strategy
- Add automated testing in CI/CD

### Documentation
**Priority**: 🟡 Medium  
**Status**: Basic documentation exists

- ✅ README.md and FuturePlans.md created
- ❌ Add API documentation (beyond Swagger)
- ❌ Create deployment guide
- ❌ Add development setup guide
- ❌ Document database schema
- ❌ Create troubleshooting guide
- ❌ Add architecture diagrams
- ❌ Document environment variables

### Database Migration Strategy
**Priority**: 🟡 Medium  
**Status**: Django migrations exist

- ✅ Auto-migration on container startup (entrypoint.sh)
- Document migration procedure
- Add rollback procedures
- Create migration testing strategy
- Document schema changes
- Add migration monitoring
- Add migration backup procedures

### Performance Optimization
**Priority**: 🟡 Medium  
**Status**: Basic optimization exists

- Add database query optimization (select_related, prefetch_related)
- Implement caching strategy (template caching, content caching)
- Optimize media delivery (CDN, compression)
- Add lazy loading where appropriate
- Implement pagination consistently
- Add performance monitoring
- Optimize WebSocket message handling

### WebSocket Reliability
**Priority**: 🟡 Medium  
**Status**: Partially implemented

- ✅ ScreenConnectionRegistry exists
- ✅ WebSocket support via Django Channels
- ❌ Improve WebSocket reconnection logic
- ❌ Add WebSocket health monitoring
- ❌ Implement WebSocket fallback strategies
- ❌ Add WebSocket message queuing for offline screens
- ❌ Add WebSocket connection pooling

---

**Last Updated**: 2024  
**Priority Legend**: 🔴 High | 🟡 Medium | 🟢 Low
