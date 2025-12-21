<template>
  <AppLayout>
    <div class="space-y-6">
      <!-- Header -->
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Audit Logs</h1>
          <p class="text-sm text-gray-600 mt-1">Comprehensive audit trail of all system actions</p>
        </div>
        <button
          @click="loadSummary"
          class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
        >
          View Summary
        </button>
      </div>

      <!-- Filters -->
      <Card>
        <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Action Type</label>
            <select
              v-model="filters.action_type"
              @change="applyFilters"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg"
            >
              <option value="">All Actions</option>
              <option value="create">Create</option>
              <option value="update">Update</option>
              <option value="delete">Delete</option>
              <option value="login">Login</option>
              <option value="logout">Logout</option>
              <option value="backup">Backup</option>
              <option value="read">Read</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Resource Type</label>
            <input
              v-model="filters.resource_type"
              @input="applyFilters"
              type="text"
              placeholder="e.g., Screen, Template"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Severity</label>
            <select
              v-model="filters.severity"
              @change="applyFilters"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg"
            >
              <option value="">All</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              v-model="filters.success"
              @change="applyFilters"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg"
            >
              <option :value="null">All</option>
              <option :value="true">Success</option>
              <option :value="false">Failed</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
            <input
              v-model="filters.start_date"
              @change="applyFilters"
              type="date"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">End Date</label>
            <input
              v-model="filters.end_date"
              @change="applyFilters"
              type="date"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <input
              v-model="filters.search"
              @input="applyFilters"
              type="text"
              placeholder="Search description, resource, user..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>
          <div class="flex items-end">
            <button
              @click="clearFilters"
              class="w-full px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </Card>

      <!-- Summary Modal -->
      <Modal :show="showSummaryModal" title="Audit Log Summary" @close="showSummaryModal = false">
        <div v-if="coreStore.auditLogSummary" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div class="p-4 bg-blue-50 rounded-lg">
              <div class="text-sm text-gray-600">Total Count</div>
              <div class="text-2xl font-bold text-blue-900">{{ coreStore.auditLogSummary.total_count || 0 }}</div>
            </div>
            <div class="p-4 bg-green-50 rounded-lg">
              <div class="text-sm text-gray-600">Success Count</div>
              <div class="text-2xl font-bold text-green-900">{{ coreStore.auditLogSummary.success_count || 0 }}</div>
            </div>
            <div class="p-4 bg-red-50 rounded-lg">
              <div class="text-sm text-gray-600">Failed Count</div>
              <div class="text-2xl font-bold text-red-900">{{ coreStore.auditLogSummary.failed_count || 0 }}</div>
            </div>
            <div class="p-4 bg-purple-50 rounded-lg">
              <div class="text-sm text-gray-600">Success Rate</div>
              <div class="text-2xl font-bold text-purple-900">
                {{ (coreStore.auditLogSummary.success_rate || 0).toFixed(1) }}%
              </div>
            </div>
          </div>
          <div v-if="coreStore.auditLogSummary.action_type_counts">
            <h3 class="font-semibold mb-2">Actions by Type</h3>
            <div class="space-y-2">
              <div
                v-for="(count, action) in coreStore.auditLogSummary.action_type_counts"
                :key="action"
                class="flex justify-between items-center p-2 bg-gray-50 rounded"
              >
                <span class="capitalize">{{ action }}</span>
                <span class="font-semibold">{{ count }}</span>
              </div>
            </div>
          </div>
          <div v-if="coreStore.auditLogSummary.severity_counts">
            <h3 class="font-semibold mb-2">Actions by Severity</h3>
            <div class="space-y-2">
              <div
                v-for="(count, severity) in coreStore.auditLogSummary.severity_counts"
                :key="severity"
                class="flex justify-between items-center p-2 bg-gray-50 rounded"
              >
                <span class="capitalize">{{ severity }}</span>
                <span class="font-semibold">{{ count }}</span>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-8 text-gray-500">Loading summary...</div>
      </Modal>

      <!-- Audit Logs Table -->
      <Card>
        <div v-if="coreStore.loading" class="text-center py-8">Loading audit logs...</div>
        <div v-else-if="coreStore.error" class="text-center py-8 text-red-600">
          {{ coreStore.error }}
        </div>
        <div v-else-if="coreStore.auditLogs.length === 0" class="text-center py-8 text-gray-500">
          No audit logs found
        </div>
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Timestamp</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Resource</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Severity</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="log in coreStore.auditLogs" :key="log.id">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ formatDate(log.timestamp) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <div class="font-medium text-gray-900">{{ log.username || 'N/A' }}</div>
                  <div class="text-gray-500 text-xs">{{ log.user_role || '' }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs capitalize">
                    {{ log.action_type || 'N/A' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <div class="font-medium">{{ log.resource_type || 'N/A' }}</div>
                  <div class="text-gray-500 text-xs">{{ log.resource_name || '' }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    :class="getSeverityClass(log.severity)"
                    class="px-2 py-1 rounded text-xs capitalize"
                  >
                    {{ log.severity || 'low' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    :class="log.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                    class="px-2 py-1 rounded text-xs font-medium"
                  >
                    {{ log.success ? 'Success' : 'Failed' }}
                  </span>
                </td>
                <td class="px-6 py-4 text-sm text-gray-900 max-w-md truncate">
                  {{ log.description || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    @click="viewLog(log)"
                    class="text-indigo-600 hover:text-indigo-900"
                  >
                    View
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>

      <!-- Log Detail Modal -->
      <Modal :show="showDetailModal" title="Audit Log Details" @close="showDetailModal = false">
        <div v-if="selectedLog" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Timestamp</label>
              <div class="mt-1 text-sm text-gray-900">{{ formatDate(selectedLog.timestamp) }}</div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">User</label>
              <div class="mt-1 text-sm text-gray-900">{{ selectedLog.username }} ({{ selectedLog.user_role }})</div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Action Type</label>
              <div class="mt-1">
                <span class="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs capitalize">
                  {{ selectedLog.action_type }}
                </span>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Severity</label>
              <div class="mt-1">
                <span :class="getSeverityClass(selectedLog.severity)" class="px-2 py-1 rounded text-xs capitalize">
                  {{ selectedLog.severity }}
                </span>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Resource Type</label>
              <div class="mt-1 text-sm text-gray-900">{{ selectedLog.resource_type || 'N/A' }}</div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Resource Name</label>
              <div class="mt-1 text-sm text-gray-900">{{ selectedLog.resource_name || 'N/A' }}</div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">IP Address</label>
              <div class="mt-1 text-sm text-gray-900">{{ selectedLog.ip_address || 'N/A' }}</div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Status</label>
              <div class="mt-1">
                <span
                  :class="selectedLog.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                  class="px-2 py-1 rounded text-xs font-medium"
                >
                  {{ selectedLog.success ? 'Success' : 'Failed' }}
                </span>
              </div>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Description</label>
            <div class="mt-1 text-sm text-gray-900">{{ selectedLog.description || 'N/A' }}</div>
          </div>
          <div v-if="selectedLog.changes">
            <label class="block text-sm font-medium text-gray-700">Changes</label>
            <pre class="mt-1 p-3 bg-gray-50 rounded text-xs overflow-auto">{{ JSON.stringify(selectedLog.changes, null, 2) }}</pre>
          </div>
          <div v-if="selectedLog.metadata">
            <label class="block text-sm font-medium text-gray-700">Metadata</label>
            <pre class="mt-1 p-3 bg-gray-50 rounded text-xs overflow-auto">{{ JSON.stringify(selectedLog.metadata, null, 2) }}</pre>
          </div>
          <div v-if="selectedLog.error_message">
            <label class="block text-sm font-medium text-gray-700">Error Message</label>
            <div class="mt-1 p-3 bg-red-50 rounded text-sm text-red-900">{{ selectedLog.error_message }}</div>
          </div>
        </div>
      </Modal>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useCoreStore } from '@/stores/core'
import AppLayout from '@/components/layout/AppLayout.vue'
import Card from '@/components/common/Card.vue'
import Modal from '@/components/common/Modal.vue'

const coreStore = useCoreStore()

const filters = ref({
  action_type: '',
  resource_type: '',
  severity: '',
  success: null,
  start_date: '',
  end_date: '',
  search: '',
})

const showSummaryModal = ref(false)
const showDetailModal = ref(false)
const selectedLog = ref(null)

const applyFilters = () => {
  coreStore.setAuditLogFilters(filters.value)
  coreStore.fetchAuditLogs()
}

const clearFilters = () => {
  filters.value = {
    action_type: '',
    resource_type: '',
    severity: '',
    success: null,
    start_date: '',
    end_date: '',
    search: '',
  }
  coreStore.clearAuditLogFilters()
  coreStore.fetchAuditLogs()
}

const loadSummary = async () => {
  showSummaryModal.value = true
  await coreStore.fetchAuditLogSummary()
}

const viewLog = async (log) => {
  selectedLog.value = log
  showDetailModal.value = true
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

const getSeverityClass = (severity) => {
  const classes = {
    low: 'bg-gray-100 text-gray-800',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-orange-100 text-orange-800',
    critical: 'bg-red-100 text-red-800',
  }
  return classes[severity?.toLowerCase()] || classes.low
}

onMounted(() => {
  coreStore.fetchAuditLogs()
})

// Watch for filter changes
watch(filters, () => {
  // Debounce search input
  if (filters.value.search !== undefined) {
    clearTimeout(window.filterTimeout)
    window.filterTimeout = setTimeout(() => {
      applyFilters()
    }, 500)
  }
}, { deep: true })
</script>
