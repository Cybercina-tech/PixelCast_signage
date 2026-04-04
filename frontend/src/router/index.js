import { nextTick } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { canAccessRoute, isDeveloperOrSuperuser } from '@/utils/permissions'
import { pushVirtualPageView } from '@/analytics/dataLayer'

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
import TemplateEditor from '../pages/templates/TemplateEditor.vue'

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

// Tickets (requester)
import TicketsList from '../pages/tickets/TicketsList.vue'
import TicketDetail from '../pages/tickets/TicketDetail.vue'

// Analytics
import AnalyticsDashboard from '../pages/analytics/AnalyticsDashboard.vue'

// Core Infrastructure
import AuditLogs from '../pages/core/AuditLogs.vue'
import Backups from '../pages/core/Backups.vue'
import SystemEmailSettings from '../pages/core/SystemEmailSettings.vue'

// Settings
import Settings from '../pages/Settings.vue'
import LicenseSettings from '../pages/LicenseSettings.vue'

// Platform (SaaS super-admin)
import PlatformTenantsList from '../pages/platform/TenantsList.vue'
import PlatformTenantDetail from '../pages/platform/TenantDetail.vue'
import SuperAdminShell from '../layouts/SuperAdminShell.vue'
import SuperAdminHome from '../pages/super-admin/SuperAdminHome.vue'
import SystemEmailSettingsPanel from '../components/core/SystemEmailSettingsPanel.vue'
import SuperAdminUsers from '../pages/super-admin/SuperAdminUsers.vue'
import SuperAdminGlobalUserManage from '../pages/super-admin/SuperAdminGlobalUserManage.vue'
import SuperAdminBilling from '../pages/super-admin/SuperAdminBilling.vue'
import SuperAdminPricing from '../pages/super-admin/SuperAdminPricing.vue'
import SuperAdminReports from '../pages/super-admin/SuperAdminReports.vue'
import SuperAdminDevices from '../pages/super-admin/SuperAdminDevices.vue'
import SuperAdminLicenses from '../pages/super-admin/SuperAdminLicenses.vue'
import SuperAdminAlerts from '../pages/super-admin/SuperAdminAlerts.vue'
import SuperAdminCapacity from '../pages/super-admin/SuperAdminCapacity.vue'
import SuperAdminSystem from '../pages/super-admin/SuperAdminSystem.vue'
import SuperAdminFlags from '../pages/super-admin/SuperAdminFlags.vue'
import SuperAdminTicketQueue from '../pages/super-admin/SuperAdminTicketQueue.vue'
import SuperAdminTicketDetail from '../pages/super-admin/SuperAdminTicketDetail.vue'
import SuperAdminTicketAnalytics from '../pages/super-admin/SuperAdminTicketAnalytics.vue'
import SuperAdminTicketSettings from '../pages/super-admin/SuperAdminTicketSettings.vue'
import SuperAdminBlogList from '../pages/super-admin/SuperAdminBlogList.vue'
import SuperAdminBlogEditor from '../pages/super-admin/SuperAdminBlogEditor.vue'
import SuperAdminBlogAI from '../pages/super-admin/SuperAdminBlogAI.vue'

// User Management
import Profile from '../pages/Profile.vue'
import Security from '../pages/Security.vue'
import Sessions from '../pages/Sessions.vue'

// Legal Pages
import PrivacyPolicy from '../pages/PrivacyPolicy.vue'
import TermsOfService from '../pages/TermsOfService.vue'
import DataCenter from '../pages/DataCenter.vue'
// Error Pages
import NotFound from '../pages/errors/NotFound.vue'
import Unauthorized from '../pages/errors/Unauthorized.vue'
import Forbidden from '../pages/errors/Forbidden.vue'
import ServerError from '../pages/errors/ServerError.vue'

// Web Player
import WebPlayer from '../pages/player/WebPlayer.vue'

// Installation
import Install from '../pages/Install.vue'

const routes = [
  {
    path: '/',
    name: 'landing',
    component: Landing,
    meta: { public: true },
  },
  {
    path: '/install',
    name: 'install',
    component: () => import('../pages/SetupWizard.vue'),
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
    path: '/forgot-password',
    name: 'forgot-password',
    component: () => import('../pages/ForgotPassword.vue'),
    meta: { public: true },
  },
  {
    path: '/reset-password',
    name: 'reset-password',
    component: () => import('../pages/ResetPassword.vue'),
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
    path: '/data-center',
    name: 'data-center',
    component: DataCenter,
    meta: { public: true },
  },
  {
    path: '/docs',
    name: 'docs',
    meta: { public: true },
    beforeEnter() {
      window.location.replace(`${window.location.origin}/documentation/index.html`)
      return false
    },
    component: { template: '<div />' },
  },
  {
    path: '/docs/changelog',
    name: 'docs-changelog',
    meta: { public: true },
    beforeEnter() {
      window.location.replace(`${window.location.origin}/documentation/changelog.html`)
      return false
    },
    component: { template: '<div />' },
  },
  {
    path: '/blog',
    name: 'blog',
    component: () => import('../pages/Blog.vue'),
    meta: { public: true },
  },
  {
    path: '/pricing',
    name: 'pricing',
    component: () => import('../pages/Pricing.vue'),
    meta: { public: true },
  },
  {
    path: '/blog/:slug',
    name: 'blog-post',
    component: () => import('../pages/BlogPost.vue'),
    meta: { public: true },
  },
  {
    path: '/player',
    name: 'player',
    redirect: (to) => {
      const screenId = to.query.screenId || to.query.screen_id
      if (screenId) {
        return { name: 'player-screen', params: { screenId: String(screenId) } }
      }
      return { name: 'player-connect' }
    },
    meta: { public: true }, // Player uses its own authentication via URL params
  },
  {
    path: '/player/connect',
    name: 'player-connect',
    component: WebPlayer,
    meta: { public: true }, // Public pairing route
  },
  {
    path: '/player/:screenId',
    name: 'player-screen',
    component: WebPlayer,
    beforeEnter: (to) => {
      if (to.query.pair === '1') {
        return { name: 'player-screen', params: to.params }
      }
      return true
    },
    meta: { public: true },
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: Dashboard,
    meta: { requiresAuth: true },
  },
  {
    path: '/super-admin',
    component: SuperAdminShell,
    meta: { requiresAuth: true, requiresRole: ['Developer'] },
    children: [
      {
        path: '',
        name: 'super-admin-home',
        component: SuperAdminHome,
        meta: { requiresAuth: true, requiresRole: ['Developer'] },
      },
      {
        path: 'customers',
        name: 'super-admin-customers',
        component: PlatformTenantsList,
        props: { embedded: true },
        meta: { requiresAuth: true, requiresRole: ['Developer'] },
      },
      {
        path: 'customers/:id',
        name: 'super-admin-customer-detail',
        component: PlatformTenantDetail,
        props: { embedded: true },
        meta: { requiresAuth: true, requiresRole: ['Developer'] },
      },
      {
        path: 'users',
        name: 'super-admin-users',
        component: SuperAdminUsers,
        meta: { requiresAuth: true, requiresRole: ['Developer'] },
      },
      {
        path: 'users/:id',
        name: 'super-admin-user-manage',
        component: SuperAdminGlobalUserManage,
        meta: { requiresAuth: true, requiresRole: ['Developer'] },
      },
      {
        path: 'billing',
        name: 'super-admin-billing',
        component: SuperAdminBilling,
        meta: { requiresAuth: true, requiresRole: ['Developer'] },
      },
      {
        path: 'pricing',
        name: 'super-admin-pricing',
        component: SuperAdminPricing,
        meta: { requiresAuth: true, requiresRole: ['Developer'] },
      },
      {
        path: 'self-hosted-licenses',
        name: 'super-admin-self-hosted-licenses',
        component: SuperAdminLicenses,
        meta: { requiresAuth: true, requiresRole: ['Developer'] },
      },
      {
        path: 'reports',
        name: 'super-admin-reports',
        component: SuperAdminReports,
        meta: { requiresAuth: true, requiresRole: ['Developer'] },
      },
      {
        path: 'devices',
        name: 'super-admin-devices',
        component: SuperAdminDevices,
        meta: { requiresAuth: true, requiresRole: ['Developer'] },
      },
      {
        path: 'alerts',
        name: 'super-admin-alerts',
        component: SuperAdminAlerts,
        meta: { requiresAuth: true, requiresRole: ['Developer'] },
      },
      {
        path: 'capacity',
        name: 'super-admin-capacity',
        component: SuperAdminCapacity,
        meta: { requiresAuth: true, requiresRole: ['Developer'] },
      },
      {
        path: 'smtp',
        name: 'super-admin-smtp',
        component: SystemEmailSettingsPanel,
        props: { showTitle: false },
        meta: { requiresAuth: true, requiresRole: ['Developer'] },
      },
      {
        path: 'system',
        name: 'super-admin-system',
        component: SuperAdminSystem,
        meta: { requiresAuth: true, requiresRole: ['Developer'] },
      },
      {
        path: 'flags',
        name: 'super-admin-flags',
        component: SuperAdminFlags,
        meta: { requiresAuth: true, requiresRole: ['Developer'] },
      },
      {
        path: 'audit-logs',
        name: 'super-admin-audit-logs',
        component: AuditLogs,
        props: { embedded: true },
        meta: {
          requiresAuth: true,
          requiresRole: ['Developer'],
          superAdminTitle: 'Audit log',
          superAdminSubtitle: 'Comprehensive audit trail of all system actions',
        },
      },
      {
        path: 'backups',
        name: 'super-admin-backups',
        component: Backups,
        props: { embedded: true },
        meta: {
          requiresAuth: true,
          requiresRole: ['Developer'],
          superAdminTitle: 'Backups',
          superAdminSubtitle: 'Database and media backup management',
        },
      },
      {
        path: 'tickets',
        name: 'super-admin-tickets',
        component: SuperAdminTicketQueue,
        meta: { requiresAuth: true, requiresRole: ['Developer'] },
      },
      {
        path: 'tickets/analytics',
        name: 'super-admin-ticket-analytics',
        component: SuperAdminTicketAnalytics,
        meta: { requiresAuth: true, requiresRole: ['Developer'] },
      },
      {
        path: 'tickets/settings',
        name: 'super-admin-ticket-settings',
        component: SuperAdminTicketSettings,
        meta: { requiresAuth: true, requiresRole: ['Developer'] },
      },
      {
        path: 'tickets/:id',
        name: 'super-admin-ticket-detail',
        component: SuperAdminTicketDetail,
        meta: { requiresAuth: true, requiresRole: ['Developer'] },
      },
      {
        path: 'blog',
        name: 'super-admin-blog',
        component: SuperAdminBlogList,
        meta: {
          requiresAuth: true,
          requiresRole: ['Developer'],
          superAdminTitle: 'Blog',
          superAdminSubtitle: 'Create and publish marketing articles',
        },
      },
      {
        path: 'blog/new',
        name: 'super-admin-blog-new',
        component: SuperAdminBlogEditor,
        meta: {
          requiresAuth: true,
          requiresRole: ['Developer'],
          superAdminTitle: 'New article',
          superAdminSubtitle: 'Draft, publish, and manage SEO fields',
        },
      },
      {
        path: 'blog/ai',
        name: 'super-admin-blog-ai',
        component: SuperAdminBlogAI,
        meta: {
          requiresAuth: true,
          requiresRole: ['Developer'],
          superAdminTitle: 'Blog AI',
          superAdminSubtitle: 'OpenAI, daily limits, and generation logs',
        },
      },
      {
        path: 'blog/:id',
        name: 'super-admin-blog-edit',
        component: SuperAdminBlogEditor,
        meta: {
          requiresAuth: true,
          requiresRole: ['Developer'],
          superAdminTitle: 'Edit article',
          superAdminSubtitle: 'Update content and publishing status',
        },
      },
    ],
  },
  {
    path: '/platform/tenants',
    redirect: '/super-admin/customers',
  },
  {
    path: '/platform/tenants/:id',
    redirect: (to) => ({ path: `/super-admin/customers/${to.params.id}` }),
  },
  {
    path: '/core/email',
    redirect: '/super-admin/smtp',
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
    path: '/templates/:id/edit',
    name: 'template-editor',
    component: TemplateEditor,
    meta: { requiresAuth: true },
  },
  {
    path: '/templates/new/edit',
    name: 'template-editor-new',
    component: TemplateEditor,
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
    path: '/tickets',
    name: 'tickets',
    component: TicketsList,
    meta: { requiresAuth: true },
  },
  {
    path: '/tickets/:id',
    name: 'ticket-detail',
    component: TicketDetail,
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
    meta: { requiresAuth: true },
  },
  {
    path: '/core/audit-logs',
    name: 'audit-logs',
    component: AuditLogs,
    meta: { requiresAuth: true, requiresRole: ['Developer'] },
  },
  {
    path: '/core/backups',
    name: 'backups',
    component: Backups,
    meta: { requiresAuth: true, requiresRole: ['Developer'] },
  },
  {
    path: '/core/email',
    name: 'system-email-settings',
    component: SystemEmailSettings,
    meta: { requiresAuth: true, requiresRole: ['Developer'] },
  },
  {
    path: '/settings',
    name: 'settings',
    component: Settings,
    meta: { requiresAuth: true },
  },
  {
    path: '/settings/license',
    name: 'settings-license',
    component: LicenseSettings,
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
    meta: { public: true },
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
            if (to.meta.requiresRole) {
              const userRole = authStore.user?.role
              if (
                !isDeveloperOrSuperuser(authStore.user) &&
                !to.meta.requiresRole.includes(userRole)
              ) {
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
  if (to.meta.requiresRole && authStore.isAuthenticated && authStore.user) {
    const userRole = authStore.user?.role
    if (
      !isDeveloperOrSuperuser(authStore.user) &&
      !to.meta.requiresRole.includes(userRole)
    ) {
      next({ name: 'forbidden' })
      return
    }
  }
  
  // Check permissions for authenticated users (UI-only check)
  // Backend API will enforce actual permissions
  if (to.meta.requiresAuth && authStore.isAuthenticated && authStore.user) {
    if (!canAccessRoute(authStore.user, to.path)) {
      next({ name: 'forbidden' })
      return
    }
  }

  next()
})

router.afterEach((to) => {
  nextTick(() => pushVirtualPageView(to))
})

export default router
