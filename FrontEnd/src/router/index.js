import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { canAccessRoute } from '@/utils/permissions'

// Public pages
import Landing from '../pages/Landing.vue'
import Login from '../pages/Login.vue'
import Signup from '../pages/Signup.vue'

// Dashboard
import Dashboard from '../pages/Dashboard.vue'

// Screens
import ScreensList from '../pages/screens/ScreensList.vue'
import ScreenDetails from '../pages/screens/ScreenDetails.vue'

// Templates
import TemplatesList from '../pages/templates/TemplatesList.vue'
import TemplateDetails from '../pages/templates/TemplateDetails.vue'

// Contents
import ContentsList from '../pages/contents/ContentsList.vue'
import ContentDetails from '../pages/contents/ContentDetails.vue'

// Schedules
import SchedulesList from '../pages/schedules/SchedulesList.vue'
import ScheduleDetails from '../pages/schedules/ScheduleDetails.vue'

// Commands
import CommandsList from '../pages/commands/CommandsList.vue'
import CommandDetails from '../pages/commands/CommandDetails.vue'

// Users
import UsersList from '../pages/users/UsersList.vue'
import UserDetails from '../pages/users/UserDetails.vue'

// Logs
import LogsReports from '../pages/logs/LogsReports.vue'

// Analytics
import AnalyticsDashboard from '../pages/analytics/AnalyticsDashboard.vue'

// Core Infrastructure
import AuditLogs from '../pages/core/AuditLogs.vue'
import Backups from '../pages/core/Backups.vue'

// Settings
import Settings from '../pages/Settings.vue'

// User Management
import Profile from '../pages/Profile.vue'
import Security from '../pages/Security.vue'
import Sessions from '../pages/Sessions.vue'

// Legal Pages
import PrivacyPolicy from '../pages/PrivacyPolicy.vue'
import TermsOfService from '../pages/TermsOfService.vue'

// Error Pages
import NotFound from '../pages/errors/NotFound.vue'
import Unauthorized from '../pages/errors/Unauthorized.vue'
import Forbidden from '../pages/errors/Forbidden.vue'
import ServerError from '../pages/errors/ServerError.vue'

// Web Player
import WebPlayer from '../pages/player/WebPlayer.vue'
import PlayerConnect from '../pages/player/PlayerConnect.vue'

const routes = [
  {
    path: '/',
    name: 'landing',
    component: Landing,
    meta: { public: true },
  },
  {
    path: '/login',
    name: 'login',
    component: Login,
    meta: { public: true },
  },
  {
    path: '/signup',
    name: 'signup',
    component: Signup,
    meta: { public: true },
  },
  {
    path: '/privacy',
    name: 'privacy',
    component: PrivacyPolicy,
    meta: { public: true },
  },
  {
    path: '/terms',
    name: 'terms',
    component: TermsOfService,
    meta: { public: true },
  },
  {
    path: '/player',
    name: 'player',
    component: WebPlayer,
    meta: { public: true }, // Player uses its own authentication via URL params
  },
  {
    path: '/player/connect',
    name: 'player-connect',
    component: PlayerConnect,
    meta: { public: true }, // Public pairing route
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: Dashboard,
    meta: { requiresAuth: true },
  },
  {
    path: '/screens',
    name: 'screens',
    component: ScreensList,
    meta: { requiresAuth: true },
  },
  {
    path: '/screens/add',
    name: 'add-screen',
    component: () => import('../pages/screens/AddScreen.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/screens/:id',
    name: 'screen-details',
    component: ScreenDetails,
    meta: { requiresAuth: true },
  },
  {
    path: '/templates',
    name: 'templates',
    component: TemplatesList,
    meta: { requiresAuth: true },
  },
  {
    path: '/templates/:id',
    name: 'template-details',
    component: TemplateDetails,
    meta: { requiresAuth: true },
  },
  {
    path: '/contents',
    name: 'contents',
    component: ContentsList,
    meta: { requiresAuth: true },
  },
  {
    path: '/contents/:id',
    name: 'content-details',
    component: ContentDetails,
    meta: { requiresAuth: true },
  },
  {
    path: '/schedules',
    name: 'schedules',
    component: SchedulesList,
    meta: { requiresAuth: true },
  },
  {
    path: '/schedules/:id',
    name: 'schedule-details',
    component: ScheduleDetails,
    meta: { requiresAuth: true },
  },
  {
    path: '/commands',
    name: 'commands',
    component: CommandsList,
    meta: { requiresAuth: true },
  },
  {
    path: '/commands/:id',
    name: 'command-details',
    component: CommandDetails,
    meta: { requiresAuth: true },
  },
  {
    path: '/users',
    name: 'users',
    component: UsersList,
    meta: { requiresAuth: true },
  },
  {
    path: '/users/:id',
    name: 'user-details',
    component: UserDetails,
    meta: { requiresAuth: true },
  },
  {
    path: '/logs',
    name: 'logs',
    component: LogsReports,
    meta: { requiresAuth: true },
  },
  {
    path: '/analytics',
    name: 'analytics',
    component: AnalyticsDashboard,
    meta: { requiresAuth: true, requiresRole: ['Manager', 'Admin', 'SuperAdmin'] },
  },
  {
    path: '/core/audit-logs',
    name: 'audit-logs',
    component: AuditLogs,
    meta: { requiresAuth: true, requiresRole: ['Manager', 'Admin', 'SuperAdmin'] },
  },
  {
    path: '/core/backups',
    name: 'backups',
    component: Backups,
    meta: { requiresAuth: true, requiresRole: ['Manager', 'Admin', 'SuperAdmin'] },
  },
  {
    path: '/settings',
    name: 'settings',
    component: Settings,
    meta: { requiresAuth: true },
  },
  {
    path: '/profile',
    name: 'profile',
    component: Profile,
    meta: { requiresAuth: true },
  },
  {
    path: '/security',
    name: 'security',
    component: Security,
    meta: { requiresAuth: true },
  },
  {
    path: '/sessions',
    name: 'sessions',
    component: Sessions,
    meta: { requiresAuth: true },
  },
  // Error pages
  {
    path: '/401',
    name: 'unauthorized',
    component: Unauthorized,
    meta: { requiresAuth: false },
  },
  {
    path: '/403',
    name: 'forbidden',
    component: Forbidden,
    meta: { requiresAuth: true },
  },
  {
    path: '/500',
    name: 'server-error',
    component: ServerError,
    meta: { requiresAuth: false },
  },
  {
    path: '/404',
    name: 'not-found',
    component: NotFound,
    meta: { requiresAuth: false },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'catch-all',
    component: NotFound,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

/**
 * Navigation Guard - Backend-Driven Authentication
 * 
 * IMPORTANT: This guard validates authentication with backend API.
 * Frontend role checks are for UX only - backend APIs enforce actual permissions.
 * 
 * Flow:
 * 1. Public routes: Allow access immediately
 * 2. Protected routes: Validate token with backend via fetchMe()
 * 3. Role-based routes: Check role from backend user data (backend API will also enforce)
 * 4. Invalid token: Clear auth state and redirect to login
 */
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Allow public routes to load immediately
  if (to.meta.public) {
    // If user is authenticated and trying to access public pages like login/signup
    if (authStore.isAuthenticated && (to.name === 'login' || to.name === 'signup')) {
      next({ name: 'dashboard' })
      return
    }
    next()
    return
  }
  
  // If route requires auth and user is not authenticated
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // Try to validate token with backend (in case token exists but user state is not set)
    if (authStore.token) {
      try {
        // Validate token by fetching user from backend
        // Set timeout to prevent hanging if API is not available
        const fetchPromise = authStore.fetchMe() // Calls GET /api/users/me/
        const timeoutPromise = new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Timeout')), 2000)
        )
        
        await Promise.race([fetchPromise, timeoutPromise])
        
        // Backend validated token successfully
        if (authStore.isAuthenticated && authStore.user) {
          // UI-only role check for route guard (backend API will also enforce)
          // SuperAdmin always bypasses role checks
          if (to.meta.requiresRole) {
            const userRole = authStore.user?.role // Role from backend
            // SuperAdmin always has access regardless of requiresRole
            if (userRole !== 'SuperAdmin' && !to.meta.requiresRole.includes(userRole)) {
              next({ name: 'forbidden' })
              return
            }
          }
          next()
          return
        }
      } catch (error) {
        // Backend rejected token (401/403) or timeout - clear auth state
        authStore.token = null
        authStore.refreshToken = null
        authStore.isAuthenticated = false
        authStore.user = null
        localStorage.removeItem('auth_token')
        localStorage.removeItem('refresh_token')
      }
    }
    // No valid token or backend validation failed - redirect to login
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }

  // Check role requirements for authenticated users (UI-only check)
  // Backend API will enforce actual permissions
  // SuperAdmin always bypasses role checks
  if (to.meta.requiresRole && authStore.isAuthenticated && authStore.user) {
    const userRole = authStore.user?.role // Role from backend API
    // SuperAdmin always has access regardless of requiresRole
    if (userRole !== 'SuperAdmin' && !to.meta.requiresRole.includes(userRole)) {
      next({ name: 'forbidden' })
      return
    }
  }
  
  // Check permissions for authenticated users (UI-only check)
  // Backend API will enforce actual permissions
  if (to.meta.requiresAuth && authStore.isAuthenticated && authStore.user) {
    // Check if user has permission to access this route
    if (!canAccessRoute(authStore.user, to.path)) {
      // User doesn't have permission - redirect to forbidden page
      next({ name: 'forbidden' })
      return
    }
  }
  
  next()
})

export default router
