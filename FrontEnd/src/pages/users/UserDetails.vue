<template>
  <AppLayout>
    <div v-if="usersStore.loading" class="text-center py-8">Loading...</div>
    <div v-else-if="user" class="space-y-6">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">{{ user.full_name || user.username }}</h1>
          <p class="text-gray-600">{{ user.email }}</p>
        </div>
        <button
          @click="showPasswordModal = true"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Change Password
        </button>
      </div>
      
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Profile Information">
          <dl class="space-y-3">
            <div>
              <dt class="text-sm font-medium text-gray-500">Username</dt>
              <dd class="mt-1 text-sm text-gray-900">{{ user.username }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">Email</dt>
              <dd class="mt-1 text-sm text-gray-900">{{ user.email }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">Full Name</dt>
              <dd class="mt-1 text-sm text-gray-900">{{ user.full_name || 'N/A' }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">Role</dt>
              <dd class="mt-1">
                <span class="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs capitalize">
                  {{ user.role }}
                </span>
              </dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">Organization</dt>
              <dd class="mt-1 text-sm text-gray-900">{{ user.organization_name || 'N/A' }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">Last Login</dt>
              <dd class="mt-1 text-sm text-gray-900">{{ formatDate(user.last_login) }}</dd>
            </div>
          </dl>
        </Card>
        
        <Card title="Access & Permissions">
          <div class="space-y-2">
            <div v-if="user.role === 'SuperAdmin' || user.role === 'Admin'" class="p-2 bg-green-50 rounded">
              Full access to all resources
            </div>
            <div v-else-if="user.role === 'Operator'" class="p-2 bg-blue-50 rounded">
              Can execute commands and manage resources
            </div>
            <div v-else-if="user.role === 'Manager'" class="p-2 bg-yellow-50 rounded">
              Can manage resources and view reports
            </div>
            <div v-else class="p-2 bg-gray-50 rounded">
              Read-only access
            </div>
          </div>
        </Card>
      </div>
      
      <Card title="Recent Activities">
        <div class="space-y-2">
          <div
            v-for="activity in recentActivities"
            :key="activity.id"
            class="p-3 bg-gray-50 rounded-lg"
          >
            <p class="text-sm">{{ activity.message || activity.type }}</p>
            <p class="text-xs text-gray-500 mt-1">{{ formatDate(activity.timestamp || activity.created_at) }}</p>
          </div>
          <div v-if="recentActivities.length === 0" class="text-center text-gray-500 py-4">
            No recent activities
          </div>
        </div>
      </Card>
      
      <Modal :show="showPasswordModal" title="Change Password" @close="showPasswordModal = false">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Old Password</label>
            <input v-model="passwordForm.old_password" type="password" required class="w-full px-3 py-2 border border-gray-300 rounded-lg" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">New Password</label>
            <input v-model="passwordForm.new_password" type="password" required class="w-full px-3 py-2 border border-gray-300 rounded-lg" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Confirm New Password</label>
            <input v-model="passwordForm.new_password_confirm" type="password" required class="w-full px-3 py-2 border border-gray-300 rounded-lg" />
          </div>
        </div>
        <template #footer>
          <button type="button" @click="handlePasswordChange" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            Change Password
          </button>
          <button type="button" @click="showPasswordModal = false" class="px-4 py-2 border border-gray-300 rounded-lg">
            Cancel
          </button>
        </template>
      </Modal>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useUsersStore } from '@/stores/users'
import { useToastStore } from '@/stores/toast'
import AppLayout from '@/components/layout/AppLayout.vue'
import Card from '@/components/common/Card.vue'
import Modal from '@/components/common/Modal.vue'

const route = useRoute()
const usersStore = useUsersStore()
const toastStore = useToastStore()

const user = computed(() => usersStore.currentUser)
const recentActivities = ref([])
const showPasswordModal = ref(false)

const passwordForm = ref({
  old_password: '',
  new_password: '',
  new_password_confirm: '',
})

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

const handlePasswordChange = async () => {
  if (passwordForm.value.new_password !== passwordForm.value.new_password_confirm) {
    toastStore.error('New passwords do not match')
    return
  }
  
  if (!passwordForm.value.old_password) {
    toastStore.error('Old password is required')
    return
  }
  
  if (!passwordForm.value.new_password) {
    toastStore.error('New password is required')
    return
  }
  
  try {
    await usersStore.changePassword(user.value.id, {
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password,
      new_password_confirm: passwordForm.value.new_password_confirm,
    })
    toastStore.success('Password changed successfully')
    showPasswordModal.value = false
    passwordForm.value = { old_password: '', new_password: '', new_password_confirm: '' }
  } catch (error) {
    toastStore.error(error.response?.data?.detail || error.response?.data?.message || 'Failed to change password')
  }
}

onMounted(async () => {
  const userId = route.params.id
  await usersStore.fetchUser(userId)
  // In a real app, you'd fetch recent activities from logs or a separate endpoint
})
</script>
