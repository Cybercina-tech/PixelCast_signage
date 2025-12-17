import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

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

// Settings
import Settings from '../pages/Settings.vue'

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
    path: '/settings',
    name: 'settings',
    component: Settings,
    meta: { requiresAuth: true },
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // If route requires auth and user is not authenticated
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // Try to fetch user info (in case token exists but user state is not set)
    if (authStore.token) {
      try {
        await authStore.fetchMe()
        if (authStore.isAuthenticated) {
          next()
          return
        }
      } catch (error) {
        // Token invalid, redirect to login
      }
    }
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }
  
  // If user is authenticated and trying to access public pages like login/signup
  if (to.meta.public && authStore.isAuthenticated && (to.name === 'login' || to.name === 'signup')) {
    next({ name: 'dashboard' })
    return
  }
  
  next()
})

export default router
