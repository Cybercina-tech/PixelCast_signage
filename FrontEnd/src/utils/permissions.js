/**
 * Permission checking utilities for frontend.
 *
 * Note: These are UI-only checks. Backend APIs enforce actual permissions.
 */

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

const ROLE_PERMISSIONS = {
  Developer: [
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
  Manager: [
    'view_dashboard',
    'view_screens', 'create_screens', 'edit_screens', 'delete_screens',
    'view_templates', 'create_templates', 'edit_templates', 'delete_templates',
    'view_contents', 'create_contents', 'edit_contents', 'delete_contents',
    'view_schedules', 'create_schedules', 'edit_schedules', 'delete_schedules',
    'view_commands', 'create_commands', 'execute_commands',
    'view_users', 'create_users', 'edit_users', 'delete_users',
    'view_analytics',
  ],
  Employee: [
    'view_screens', 'create_screens', 'edit_screens',
    'view_schedules', 'create_schedules', 'edit_schedules',
    'view_contents', 'create_contents', 'edit_contents',
  ],
}

/**
 * @param {Object} user - User object with role property
 * @returns {Set<string>}
 */
export function getUserPermissions(user) {
  if (!user || !user.role) {
    return new Set()
  }

  const role = user.role
  const permissions = ROLE_PERMISSIONS[role] || []

  return new Set(permissions)
}

export function hasPermission(user, permission) {
  if (!user || !user.role) {
    return false
  }
  return getUserPermissions(user).has(permission)
}

/**
 * Match longest registered route prefix (supports nested paths like /screens/:id).
 */
export function canAccessRoute(user, routePath) {
  if (!user || !user.role) {
    return false
  }

  if (user.role === 'Developer') {
    return true
  }

  const path = routePath.split('?')[0]
  const prefixes = Object.keys(ROUTE_PERMISSIONS).sort((a, b) => b.length - a.length)

  for (const prefix of prefixes) {
    if (path === prefix || path.startsWith(`${prefix}/`)) {
      const required = ROUTE_PERMISSIONS[prefix]
      const userPermissions = getUserPermissions(user)
      return required.some((perm) => userPermissions.has(perm))
    }
  }

  return true
}

export function hasAnyPermission(user, permissions) {
  if (!user || !user.role || !permissions || permissions.length === 0) {
    return false
  }

  const userPermissions = getUserPermissions(user)
  return permissions.some((perm) => userPermissions.has(perm))
}

export function hasAllPermissions(user, permissions) {
  if (!user || !user.role || !permissions || permissions.length === 0) {
    return false
  }

  const userPermissions = getUserPermissions(user)
  return permissions.every((perm) => userPermissions.has(perm))
}
