export const SUPER_ADMIN_NAV_GROUPS = [
  {
    id: 'overview',
    label: 'Overview',
    items: [
      { label: 'Dashboard', to: '/super-admin', icon: 'ChartBarIcon', match: 'exact' },
      { label: 'Blog', to: '/super-admin/blog', icon: 'NewspaperIcon' },
      { label: 'Blog AI', to: '/super-admin/blog/ai', icon: 'SparklesIcon' },
      { label: 'Reports & cohorts', to: '/super-admin/reports', icon: 'ChartBarIcon' },
    ],
  },
  {
    id: 'customers',
    label: 'Customers',
    items: [
      { label: 'Tenants', to: '/super-admin/customers', icon: 'BuildingOffice2Icon' },
      { label: 'All users', to: '/super-admin/users', icon: 'UsersIcon' },
      { label: 'Devices', to: '/super-admin/devices', icon: 'ServerStackIcon' },
    ],
  },
  {
    id: 'revenue',
    label: 'Revenue',
    items: [
      { label: 'Billing', to: '/super-admin/billing', icon: 'CurrencyDollarIcon' },
      { label: 'Pricing catalog', to: '/super-admin/pricing', icon: 'TagIcon' },
      { label: 'Self-hosted licenses', to: '/super-admin/self-hosted-licenses', icon: 'KeyIcon' },
      { label: 'Gateway instances', to: '/super-admin/gateway-instances', icon: 'GlobeAltIcon' },
    ],
  },
  {
    id: 'support',
    label: 'Support',
    items: [
      {
        label: 'Ticket queue',
        to: '/super-admin/tickets',
        icon: 'ChatBubbleLeftRightIcon',
        // Avoid prefix match: /super-admin/tickets/settings and …/analytics also start with …/tickets/
        match: 'tickets-queue',
      },
      { label: 'Ticket analytics', to: '/super-admin/tickets/analytics', icon: 'ChartBarIcon' },
      { label: 'Ticket settings', to: '/super-admin/tickets/settings', icon: 'Cog6ToothIcon' },
    ],
  },
  {
    id: 'operations',
    label: 'Operations',
    items: [
      { label: 'Alerts & logs', to: '/super-admin/alerts', icon: 'BellAlertIcon' },
      { label: 'Capacity', to: '/super-admin/capacity', icon: 'ServerStackIcon' },
      { label: 'Communications', to: '/super-admin/smtp', icon: 'EnvelopeIcon' },
      { label: 'Feature flags', to: '/super-admin/flags', icon: 'FlagIcon' },
      { label: 'Audit log', to: '/super-admin/audit-logs', icon: 'ClipboardDocumentListIcon' },
      { label: 'Backups', to: '/super-admin/backups', icon: 'CpuChipIcon' },
    ],
  },
  {
    id: 'infrastructure',
    label: 'Infrastructure',
    items: [
      { label: 'System health', to: '/super-admin/system', icon: 'ServerStackIcon' },
    ],
  },
]
