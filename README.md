# ScreenGram - Digital Signage Management System

A production-ready digital signage management platform with Vue.js 3 frontend and Django backend.

> 📋 **Feature Planning**: For a complete overview of implemented features, missing features, and the development roadmap, see [FeaturePlan.md](./FeaturePlan.md).

## 🚀 Overview

ScreenGram is a comprehensive digital signage management system that enables users to:
- Manage digital displays (screens) remotely
- Create and manage content templates
- Schedule content playback
- Monitor screen health and status in real-time
- Execute commands on remote screens
- Manage users with role-based access control

## 🔒 Security

The system implements production-ready security features:
- ✅ **JWT Authentication** - Secure token-based authentication
- ✅ **Role-Based Access Control** - Granular permission system
- ✅ **Account Lockout** - Protection against brute force attacks (5 attempts, 15min lockout)
- ✅ **Enhanced Password Security** - PBKDF2 hashing, strength checking, validation
- ✅ **User Enumeration Prevention** - Generic error messages
- ✅ **Input Sanitization** - Comprehensive XSS and injection prevention
- ✅ **Audit Logging** - Complete audit trail for all critical actions
- ✅ **Rate Limiting** - Multi-strategy API rate limiting
- ✅ **Environment Variable Security** - Sensitive config via environment variables

## 📁 Project Structure

```
ScreenGram/
├── FrontEnd/          # Vue.js 3 frontend application
├── BackEnd/           # Django REST API backend
├── README.md          # This file
└── FeaturePlan.md     # Feature roadmap and planning
```

## Features

### Frontend (Vue.js 3)
- **Complete Dashboard** with real-time status cards, charts, and activity feed
- **Screen Management** - List, view details, health monitoring, command queue, and logs
- **Template Management** - Create, edit templates with hierarchical structure (Template → Layer → Widget → Content)
- **Content Management** - Upload, manage, and track content downloads
- **Schedule Management** - Create and manage time-based schedules with repeat options
- **Command Management** - Send commands to screens, track execution status
- **User & Role Management** - Manage users with role-based access control
- **Logs & Reports** - View and export logs (Screen Status, Content Download, Command Execution)
- **Core Infrastructure** - Audit logs and backup management (Manager/Admin only)
- **Settings** - Configure API, WebSocket, storage, security, and notifications

### Backend (Django)
- **RESTful API** - Complete REST API with Swagger/OpenAPI documentation
- **WebSocket Support** - Real-time communication with screens
- **User Management** - Secure user management with enhanced security
- **Caching System** - Redis/LocMem caching for performance
- **Rate Limiting** - Multi-strategy rate limiting
- **Audit Logging** - Comprehensive audit trail
- **Backup System** - Automated database and media backups
- **Security Features** - Account lockout, password security, input sanitization

## Technology Stack

### Frontend
- **Vue.js 3.4+** - Progressive JavaScript framework
- **Vue Router 4.3+** - Official router for Vue.js
- **Pinia 2.1+** - State management library
- **Tailwind CSS 3.4+** - Utility-first CSS framework
- **Chart.js** - Charting library for metrics visualization
- **Axios** - HTTP client for API requests
- **Heroicons** - Beautiful SVG icons
- **Vite 5.1+** - Next-generation frontend build tool

### Backend
- **Django 5.2+** - Python web framework
- **Django REST Framework** - REST API framework
- **Django Channels** - WebSocket support
- **JWT Authentication** - Token-based authentication
- **Redis** - Caching and rate limiting
- **PostgreSQL/SQLite** - Database
- **Celery** - Background task processing
- **Swagger/OpenAPI** - API documentation

## Quick Start

### Backend Setup

1. **Navigate to BackEnd directory:**
   ```bash
   cd BackEnd
   ```

2. **Create virtual environment and install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set environment variables:**
   ```bash
   # Create .env file
   SECRET_KEY=your-secret-key-here
   DEBUG=False
   ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com
   ACCOUNT_LOCKOUT_ENABLED=True
   MAX_LOGIN_ATTEMPTS=5
   LOCKOUT_DURATION=900
   ```

4. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start development server:**
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. **Navigate to FrontEnd directory:**
   ```bash
   cd FrontEnd
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment variables:**
   ```bash
   # Create .env file
   VITE_API_BASE_URL=http://localhost:8000/api
   VITE_WS_HOST=ws://localhost:8000
   ```

4. **Start development server:**
   ```bash
   npm run dev
   ```

## Documentation

- **[FeaturePlan.md](./FeaturePlan.md)** - Complete feature roadmap and planning document
- **API Documentation** - Available at `/api/docs/` when backend is running (Swagger UI)
- **Backend README** - See `BackEnd/` directory for detailed backend documentation

## Backend API Configuration

The frontend is designed to work with the ScreenGram Django backend. Ensure the backend is running and accessible at the URL specified in your `.env` file.

### API Endpoints

The frontend uses the following API endpoints (configured in `src/services/api.js`):

- **Authentication:** `/api/auth/login/`, `/api/auth/logout/`, `/api/auth/token/`
- **Users:** `/api/users/`, `/api/users/{id}/`, `/api/users/me/`
- **Screens:** `/api/screens/`, `/api/screens/{id}/`
- **Templates:** `/api/templates/`, `/api/templates/{id}/activate_on_screen/`
- **Layers:** `/api/layers/`
- **Widgets:** `/api/widgets/`
- **Contents:** `/api/contents/`, `/api/contents/{id}/upload/`
- **Schedules:** `/api/schedules/`, `/api/schedules/{id}/execute/`
- **Commands:** `/api/commands/`, `/api/commands/{id}/retry/`
- **Logs:** `/api/logs/screen-status/`, `/api/logs/content-download/`, `/api/logs/command-execution/`

### WebSocket Configuration

For real-time updates, configure WebSocket connection:

- **Dashboard WebSocket:** `ws://your-backend/ws/dashboard/?token=<JWT_TOKEN>`
- **Screen WebSocket:** `ws://your-backend/ws/screen/?auth_token=xxx&secret_key=yyy`

The WebSocket URL is configured via `VITE_WS_HOST` environment variable.

## Authentication

The frontend uses JWT (JSON Web Tokens) for authentication:

1. User logs in via `/login` page
2. Backend returns JWT access token (and optionally refresh token)
3. Token is stored in localStorage and included in API requests
4. Token is automatically refreshed when expired (if refresh token is available)

## State Management

The application uses Pinia stores for state management:

- **auth** - Authentication state and user info
- **screens** - Screen data and operations
- **templates** - Template, layer, and widget data
- **content** - Content data and upload operations
- **schedules** - Schedule data and execution
- **commands** - Command queue and execution status
- **users** - User management
- **logs** - Log data and filtering
- **dashboard** - Dashboard statistics and metrics
- **toast** - Toast notification system

## Key Features

### Real-time Updates

The application supports real-time updates via WebSocket connections. The `useWebSocket` composable handles:
- Automatic connection management
- Reconnection with exponential backoff
- Event subscription/unsubscription
- Heartbeat/ping-pong mechanism

### Responsive Design

All pages are responsive and work on:
- Desktop (1920px+)
- Tablet (768px - 1919px)
- Mobile (< 768px)

### Error Handling

- API errors are caught and displayed via toast notifications
- Network errors trigger automatic retries where appropriate
- 401 errors automatically redirect to login page

### Data Filtering & Search

Most list pages support:
- Text search across relevant fields
- Status/type filtering
- Date range filtering (for logs)
- Real-time filter application

## Development

### Adding New Pages

1. Create component in `src/pages/`
2. Add route in `src/router/index.js`
3. Create/update Pinia store if needed
4. Add navigation link in `src/components/layout/Sidebar.vue`

### Adding New API Endpoints

1. Add endpoint function in `src/services/api.js`
2. Add corresponding action in relevant Pinia store
3. Use in component/page

### Styling

The project uses Tailwind CSS. Custom styles can be added in:
- `src/style.css` - Global styles
- Component `<style>` blocks - Component-specific styles

## Production Deployment

1. **Build the application:**
   ```bash
   npm run build
   ```

2. **Deploy the `dist` directory** to your web server (nginx, Apache, etc.)

3. **Configure reverse proxy** to handle API requests and WebSocket connections

4. **Set environment variables** on your hosting platform

### Example Nginx Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    # Frontend
    location / {
        root /var/www/screengram-frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # WebSocket
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## Troubleshooting

### API Connection Issues

- Verify `VITE_API_BASE_URL` is correct
- Check CORS settings on backend
- Ensure backend is running and accessible

### WebSocket Connection Issues

- Verify `VITE_WS_HOST` is correct
- Check WebSocket URL format (ws:// or wss://)
- Ensure backend WebSocket server is running
- Check firewall/network settings

### Build Issues

- Clear `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Clear Vite cache: `rm -rf node_modules/.vite`
- Check Node.js version (requires 18+)

## Support

For issues and questions:
- Check backend API documentation
- Review browser console for errors
- Check network tab for API request/response details

## Security Features

ScreenGram implements industry-standard security practices:

### Authentication & Authorization
- JWT token-based authentication
- Role-based access control (5 roles: SuperAdmin, Admin, Operator, Manager, Viewer)
- Session management with automatic token refresh

### Account Protection
- Account lockout after 5 failed login attempts
- 15-minute lockout duration (configurable)
- IP-based and username-based tracking
- User enumeration prevention

### Password Security
- PBKDF2 password hashing (260,000+ iterations)
- Minimum 8-character requirement
- Password strength checking
- User attribute similarity validation
- Common password prevention

### Data Protection
- Comprehensive input sanitization
- XSS and SQL injection prevention
- CSRF protection
- Secure environment variable configuration
- Passwords never exposed in API responses

### Audit & Monitoring
- Complete audit trail for all critical actions
- Login/logout logging
- Password change tracking (high severity)
- Role change tracking (critical severity)
- User CRUD operation logging

### API Security
- Rate limiting (configurable per role)
- Request validation
- Secure error messages
- CORS configuration

For detailed security information, see the backend documentation and security audit reports.

## License

See main project LICENSE file.
