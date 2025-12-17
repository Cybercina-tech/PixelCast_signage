# ScreenGram Frontend

A production-ready Vue.js 3 frontend application for the ScreenGram Digital Signage Management System.

## Features

- **Complete Dashboard** with real-time status cards, charts, and activity feed
- **Screen Management** - List, view details, health monitoring, command queue, and logs
- **Template Management** - Create, edit templates with hierarchical structure (Template → Layer → Widget → Content)
- **Content Management** - Upload, manage, and track content downloads
- **Schedule Management** - Create and manage time-based schedules with repeat options
- **Command Management** - Send commands to screens, track execution status
- **User & Role Management** - Manage users with role-based access control
- **Logs & Reports** - View and export logs (Screen Status, Content Download, Command Execution)
- **Settings** - Configure API, WebSocket, storage, security, and notifications

## Technology Stack

- **Vue.js 3.4+** - Progressive JavaScript framework
- **Vue Router 4.3+** - Official router for Vue.js
- **Pinia 2.1+** - State management library
- **Tailwind CSS 3.4+** - Utility-first CSS framework
- **Chart.js** - Charting library for metrics visualization
- **Axios** - HTTP client for API requests
- **Heroicons** - Beautiful SVG icons
- **Vite 5.1+** - Next-generation frontend build tool

## Project Structure

```
FrontEnd/
├── src/
│   ├── components/
│   │   ├── common/          # Reusable components (Table, Modal, Card, Chart, Toast)
│   │   ├── home/            # Landing page components
│   │   └── layout/          # Layout components (AppLayout, Navbar, Sidebar, Footer)
│   ├── composables/         # Vue composables (useWebSocket)
│   ├── pages/               # Page components
│   │   ├── screens/         # Screen management pages
│   │   ├── templates/       # Template management pages
│   │   ├── contents/        # Content management pages
│   │   ├── schedules/       # Schedule management pages
│   │   ├── commands/        # Command management pages
│   │   ├── users/           # User management pages
│   │   └── logs/            # Logs and reports pages
│   ├── router/              # Vue Router configuration
│   ├── services/            # API service layer
│   ├── stores/              # Pinia stores (state management)
│   ├── App.vue              # Root component
│   └── main.js              # Application entry point
├── package.json
├── vite.config.js
├── tailwind.config.js
└── README.md
```

## Setup Instructions

### Prerequisites

- Node.js 18+ and npm/yarn
- Backend API running (see BackEnd README)

### Installation

1. **Navigate to the FrontEnd directory:**
   ```bash
   cd FrontEnd
   ```

2. **Install dependencies:**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Configure environment variables:**
   
   Create a `.env` file in the `FrontEnd` directory:
   ```env
   VITE_API_BASE_URL=http://localhost:8000/api
   VITE_WS_HOST=ws://localhost:8000
   ```
   
   For production, update these values to match your backend server:
   ```env
   VITE_API_BASE_URL=https://api.yourdomain.com/api
   VITE_WS_HOST=wss://api.yourdomain.com
   ```

4. **Start the development server:**
   ```bash
   npm run dev
   # or
   yarn dev
   ```
   
   The application will be available at `http://localhost:5173` (or the port shown in the terminal).

5. **Build for production:**
   ```bash
   npm run build
   # or
   yarn build
   ```
   
   The production build will be in the `dist` directory.

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

## License

See main project LICENSE file.
