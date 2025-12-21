# ScreenGram Frontend

Complete Vue.js 3 frontend for ScreenGram Digital Signage Management System.

## 🚀 Quick Start

### Prerequisites

- Node.js 16+ and npm/yarn
- Python backend running (see BackEnd/README.md)
- Backend API accessible at `http://localhost:8000/api` (or configure via environment variables)

### Installation

```bash
cd FrontEnd
npm install
```

### Configuration

Create a `.env` file in the FrontEnd directory (optional):

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_WS_HOST=ws://localhost:8000
```

### Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:5173` (Vite default port)

### Build for Production

```bash
npm run build
```

Build output will be in `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## 📁 Project Structure

```
FrontEnd/src/
├── components/
│   ├── common/          # Reusable components (Card, Table, Modal, Chart, Toast)
│   ├── layout/          # Layout components (AppLayout, Sidebar, Navbar, Footer)
│   ├── home/            # Landing page components
│   ├── analytics/       # Analytics dashboard components
│   ├── content/         # Content management components
│   └── logs/            # Log viewing components
├── pages/
│   ├── Dashboard.vue
│   ├── Login.vue
│   ├── Landing.vue
│   ├── screens/         # Screen management pages
│   ├── templates/       # Template management pages
│   ├── contents/        # Content management pages
│   ├── schedules/       # Schedule management pages
│   ├── commands/        # Command management pages
│   ├── users/           # User management pages
│   ├── logs/            # Log viewing pages
│   ├── analytics/       # Analytics dashboard
│   └── errors/          # Error pages (404, 401, 403, 500)
├── stores/              # Pinia stores for state management
│   ├── auth.js          # Authentication state
│   ├── screens.js       # Screen state
│   ├── templates.js     # Template state
│   ├── content.js       # Content state
│   ├── schedules.js     # Schedule state
│   ├── commands.js      # Command state
│   ├── users.js         # User state
│   ├── analytics.js     # Analytics state
│   ├── bulkOperations.js # Bulk operations state
│   ├── contentValidation.js # Content validation state
│   ├── logs.js          # Logs state
│   ├── dashboard.js     # Dashboard state
│   ├── toast.js         # Toast notifications
│   └── app.js           # App-wide state
├── services/
│   └── api.js           # API service with all endpoints
├── router/
│   └── index.js         # Vue Router configuration
├── composables/
│   └── useWebSocket.js  # WebSocket composable
└── main.js              # Application entry point
```

## 🔐 Authentication

The frontend uses JWT authentication. Tokens are stored in localStorage and automatically included in API requests.

### Login Flow

1. User enters credentials on `/login`
2. Backend validates and returns JWT tokens (access + refresh)
3. Tokens stored in localStorage
4. All subsequent requests include `Authorization: Bearer <token>` header
5. Token expires after 60 minutes (configurable in backend)
6. Refresh token used to get new access token

### Protected Routes

All routes except `/`, `/login`, `/signup` require authentication. The router guard automatically:
- Checks for valid token
- Redirects to login if not authenticated
- Checks role permissions for specific routes (e.g., Analytics requires Manager/Admin)

## 📱 Pages Overview

### Public Pages

- **Landing** (`/`) - Landing page
- **Login** (`/login`) - User authentication
- **Signup** (`/signup`) - User registration

### Protected Pages

- **Dashboard** (`/dashboard`) - Overview and quick stats
- **Screens** (`/screens`, `/screens/:id`) - Screen management
- **Templates** (`/templates`, `/templates/:id`) - Template management
- **Contents** (`/contents`, `/contents/:id`) - Content management
- **Schedules** (`/schedules`, `/schedules/:id`) - Schedule management
- **Commands** (`/commands`, `/commands/:id`) - Command management
- **Users** (`/users`, `/users/:id`) - User and role management
- **Logs** (`/logs`) - System logs and reports
- **Analytics** (`/analytics`) - Analytics dashboard (Manager/Admin only)
- **Settings** (`/settings`) - Application settings

### Error Pages

- **404** (`/404`) - Page not found
- **401** (`/401`) - Unauthorized
- **403** (`/403`) - Forbidden
- **500** (`/500`) - Server error

## 🏪 State Management (Pinia Stores)

### Auth Store (`stores/auth.js`)

Manages authentication state:
- `user`, `token`, `refreshToken`, `isAuthenticated`
- Actions: `login()`, `logout()`, `fetchMe()`, `refreshAccessToken()`

### Screen Store (`stores/screens.js`)

Manages screen data:
- `screens`, `currentScreen`, `loading`, `error`, `filters`
- Actions: `fetchScreens()`, `fetchScreen()`, `createScreen()`, `updateScreen()`, `deleteScreen()`

Similar stores exist for: Templates, Contents, Schedules, Commands, Users, Logs

### Analytics Store (`stores/analytics.js`)

Manages analytics data:
- Screen, command, content, template statistics
- Activity trends
- Actions: `fetchScreenStatistics()`, `fetchCommandStatistics()`, etc.

### Bulk Operations Store (`stores/bulkOperations.js`)

Manages bulk operations:
- Actions for bulk delete, update, activate operations across all modules

### Content Validation Store (`stores/contentValidation.js`)

Manages content validation:
- Single file and bulk validation
- Validation results and errors

## 🔌 API Integration

All API calls are centralized in `services/api.js`. The API service:

- Automatically adds JWT token to requests
- Handles 401/403/500 errors with redirects
- Provides typed API functions for each module

### Example Usage

```javascript
import { screensAPI } from '@/services/api'

// List screens
const response = await screensAPI.list({ page: 1, page_size: 50 })

// Create screen
const newScreen = await screensAPI.create({
  name: 'Screen 1',
  device_id: 'device-001'
})
```

## 🎨 Components

### Common Components

- **Card** - Container component with optional title
- **Table** - Data table with columns, actions, slots
- **Modal** - Modal dialog with header, body, footer slots
- **Chart** - Chart.js wrapper for visualizations
- **Toast** - Toast notification component
- **ToastContainer** - Container for toasts

### Layout Components

- **AppLayout** - Main application layout (sidebar + navbar)
- **Sidebar** - Navigation sidebar
- **Navbar** - Top navigation bar
- **Footer** - Page footer

## 🔄 Features

### Bulk Operations

All list pages support bulk operations:
- Bulk delete
- Bulk update
- Bulk activate
- Select multiple items with checkboxes
- Confirm before executing

### Content Validation

- File upload with automatic validation
- Validation errors displayed inline
- Bulk file validation
- Visual feedback for valid/invalid files

### Real-time Updates

- WebSocket integration for live updates
- Dashboard auto-refreshes every 30 seconds
- Screen status updates in real-time

### Error Handling

- Global error interceptor in API service
- Automatic redirects for 401/403/500 errors
- Toast notifications for user feedback
- Graceful degradation when backend unavailable

## 🧪 Testing Integration

The frontend is designed to work with the backend testing suite. All API endpoints are tested in the backend.

For frontend-specific testing (if added later):
```bash
npm run test  # When test framework is configured
```

## 📦 Build & Deploy

### Development Build

```bash
npm run dev
```

### Production Build

```bash
npm run build
```

### Environment Variables

Create `.env.production`:

```env
VITE_API_BASE_URL=https://api.yourdomain.com/api
VITE_WS_HOST=wss://api.yourdomain.com
```

## 🔧 Troubleshooting

### API Connection Issues

1. Check backend is running: `http://localhost:8000/api`
2. Check CORS settings in backend
3. Verify `VITE_API_BASE_URL` in `.env`

### Authentication Issues

1. Check token in localStorage: `localStorage.getItem('auth_token')`
2. Verify token expiration (60 minutes)
3. Try logging out and logging in again

### Build Errors

1. Clear node_modules and reinstall: `rm -rf node_modules package-lock.json && npm install`
2. Check Node.js version (16+)
3. Review build output for specific errors

## 📚 Integration with Backend

### Required Backend Endpoints

The frontend expects these backend endpoints:

- `/api/auth/token/` - JWT token generation
- `/api/auth/token/refresh/` - Token refresh
- `/api/screens/` - Screen CRUD
- `/api/templates/` - Template CRUD
- `/api/contents/` - Content CRUD
- `/api/schedules/` - Schedule CRUD
- `/api/commands/` - Command CRUD
- `/api/users/` - User management
- `/api/logs/` - Log viewing
- `/api/analytics/` - Analytics data
- `/api/{module}/bulk/*` - Bulk operations
- `/api/content-validation/*` - Content validation

### Backend Configuration

Ensure backend has:
- CORS enabled for frontend origin
- JWT authentication configured
- All modules installed and migrated
- WebSocket support (for real-time features)

## 🎯 Next Steps

1. **Customize Styling**: Modify Tailwind classes for branding
2. **Add Features**: Extend components as needed
3. **Performance**: Add lazy loading for large lists
4. **Accessibility**: Add ARIA labels and keyboard navigation
5. **Testing**: Add unit and E2E tests

## 📞 Support

For backend API documentation, see `BackEnd/api_docs/README.md`

For backend testing, see `BackEnd/TESTING.md`
