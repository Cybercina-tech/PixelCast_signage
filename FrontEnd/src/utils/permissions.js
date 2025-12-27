/**
 * Permission checking utilities for frontend.
 * 
 * Note: These are UI-only checks. Backend APIs enforce actual permissions.
 * If a user accesses a route without permission, the backend will return 403.
 */

// Map routes to required permissions
const ROUTE_PERMISSIONS = {
  '/dashboard': ['view_dashboard'],
  '/screens': ['view_screens'],
  '/templates': ['view_templates'],
  '/contents': ['view_contents'],
  '/schedules': ['view_schedules'],
  '/commands': ['view_commands'],
  '/users': ['view_users'],
  '/logs': ['view_logs'],
  '/analytics': ['view_analytics'],
  '/core/audit-logs': ['view_audit_logs'],
  '/core/backups': ['view_backups'],
  '/settings': ['view_settings'],
}

// Role to permissions mapping (matches backend)
const ROLE_PERMISSIONS = {
  SuperAdmin: [
    'view_dashboard',
    'view_screens', 'create_screens', 'edit_screens', 'delete_screens',
    'view_templates', 'create_templates', 'edit_templates', 'delete_templates',
    'view_contents', 'create_contents', 'edit_contents', 'delete_contents',
    'view_schedules', 'create_schedules', 'edit_schedules', 'delete_schedules',
    'view_commands', 'create_commands', 'execute_commands',
    'view_users', 'create_users', 'edit_users', 'delete_users', 'manage_roles',
    'view_logs',
    'view_analytics',
    'view_audit_logs',
    'view_backups', 'manage_backups',
    'view_settings', 'edit_settings',
    'view_errors',
  ],
  Admin: [
    'view_dashboard',
    'view_screens', 'create_screens', 'edit_screens', 'delete_screens',
    'view_templates', 'create_templates', 'edit_templates', 'delete_templates',
    'view_contents', 'create_contents', 'edit_contents', 'delete_contents',
    'view_schedules', 'create_schedules', 'edit_schedules', 'delete_schedules',
    'view_commands', 'create_commands', 'execute_commands',
    'view_users', 'create_users', 'edit_users', 'delete_users', 'manage_roles',
    'view_logs',
    'view_analytics',
    'view_audit_logs',
    'view_backups', 'manage_backups',
    'view_settings', 'edit_settings',
  ],
  Manager: [
    'view_dashboard',
    'view_screens', 'create_screens', 'edit_screens',
    'view_templates', 'create_templates', 'edit_templates',
    'view_contents', 'create_contents', 'edit_contents',
    'view_schedules', 'create_schedules', 'edit_schedules',
    'view_commands', 'create_commands', 'execute_commands',
    'view_users',
    'view_logs',
    'view_analytics',
    'view_settings',
  ],
  Operator: [
    'view_dashboard',
    'view_screens', 'create_screens', 'edit_screens',
    'view_templates', 'create_templates', 'edit_templates',
    'view_contents', 'create_contents', 'edit_contents',
    'view_schedules', 'create_schedules', 'edit_schedules',
    'view_commands', 'create_commands', 'execute_commands',
    'view_logs',
    'view_settings',
  ],
  Viewer: [
    'view_dashboard',
    'view_screens',
    'view_templates',
    'view_contents',
    'view_schedules',
    'view_commands',
    'view_settings',
  ],
}

/**
 * Get all permissions for a user based on their role.
 * @param {Object} user - User object with role property
 * @returns {Set} Set of permission strings
 */
export function getUserPermissions(user) {
  if (!user || !user.role) {
    return new Set()
  }
  
  const role = user.role
  const permissions = ROLE_PERMISSIONS[role] || []
  
  // SuperAdmin always has all permissions from ROLE_PERMISSIONS
  if (role === 'SuperAdmin') {
    // Return all permissions from SuperAdmin role mapping
    return new Set(ROLE_PERMISSIONS['SuperAdmin'] || [])
  }
  
  return new Set(permissions)
}

/**
 * Check if user has a specific permission.
 * @param {Object} user - User object with role property
 * @param {string} permission - Permission string
 * @returns {boolean} True if user has permission
 */
export function hasPermission(user, permission) {
  if (!user || !user.role) {
    return false
  }
  
  const userPermissions = getUserPermissions(user)
  return userPermissions.has(permission)
}

/**
 * Check if user has permission to access a route.
 * @param {Object} user - User object with role property
 * @param {string} routePath - Route path (e.g., '/dashboard')
 * @returns {boolean} True if user can access the route
 */
export function canAccessRoute(user, routePath) {
  if (!user || !user.role) {
    return false
  }
  
  // SuperAdmin always has access to all routes
  if (user.role === 'SuperAdmin') {
    return true
  }
  
  // Find matching route permissions
  const requiredPermissions = ROUTE_PERMISSIONS[routePath]
  
  // If route doesn't require specific permissions, allow access (for authenticated users)
  if (!requiredPermissions || requiredPermissions.length === 0) {
    return true
  }
  
  // Check if user has at least one of the required permissions
  const userPermissions = getUserPermissions(user)
  return requiredPermissions.some(perm => userPermissions.has(perm))
}

/**
 * Check if user has any of the specified permissions.
 * @param {Object} user - User object with role property
 * @param {string[]} permissions - Array of permission strings
 * @returns {boolean} True if user has at least one permission
 */
export function hasAnyPermission(user, permissions) {
  if (!user || !user.role || !permissions || permissions.length === 0) {
    return false
  }
  
  const userPermissions = getUserPermissions(user)
  return permissions.some(perm => userPermissions.has(perm))
}

/**
 * Check if user has all of the specified permissions.
 * @param {Object} user - User object with role property
 * @param {string[]} permissions - Array of permission strings
 * @returns {boolean} True if user has all permissions
 */
export function hasAllPermissions(user, permissions) {
  if (!user || !user.role || !permissions || permissions.length === 0) {
    return false
  }
  
  const userPermissions = getUserPermissions(user)
  return permissions.every(perm => userPermissions.has(perm))
}

