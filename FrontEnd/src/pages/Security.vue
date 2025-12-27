<template>
  <AppLayout>
    <div class="space-y-6">
      <div>
        <h1 class="text-2xl font-bold text-primary">Security</h1>
        <p class="text-muted mt-1">Manage your account security settings</p>
      </div>

      <!-- Change Password Section -->
      <Card title="Change Password">
        <form @submit.prevent="handleChangePassword" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-secondary mb-1">Current Password</label>
            <input
              v-model="passwordForm.old_password"
              type="password"
              required
              class="w-full px-3 py-2 border border-border-color rounded-lg bg-card text-primary placeholder:text-muted"
              placeholder="Enter current password"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-secondary mb-1">New Password</label>
            <input
              v-model="passwordForm.new_password"
              type="password"
              required
              minlength="8"
              class="w-full px-3 py-2 border border-border-color rounded-lg bg-card text-primary placeholder:text-muted"
              placeholder="Enter new password"
            />
            <p class="mt-1 text-xs text-muted">Password must be at least 8 characters long</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-secondary mb-1">Confirm New Password</label>
            <input
              v-model="passwordForm.new_password_confirm"
              type="password"
              required
              minlength="8"
              class="w-full px-3 py-2 border border-border-color rounded-lg bg-card text-primary placeholder:text-muted"
              placeholder="Confirm new password"
            />
            <p v-if="passwordForm.new_password && passwordForm.new_password_confirm && passwordForm.new_password !== passwordForm.new_password_confirm" class="mt-1 text-xs text-error">
              Passwords do not match
            </p>
          </div>

          <div class="flex justify-end pt-4">
            <button
              type="submit"
              class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-hover transition-colors"
              :disabled="changingPassword || passwordForm.new_password !== passwordForm.new_password_confirm"
            >
              <span v-if="changingPassword">Changing...</span>
              <span v-else>Change Password</span>
            </button>
          </div>
        </form>
      </Card>

      <!-- Active Sessions Section -->
      <Card title="Active Sessions">
        <div v-if="loadingSessions" class="flex items-center justify-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
        <div v-else-if="sessionsError" class="bg-error/10 border border-error/20 rounded-lg p-4">
          <p class="text-error text-sm break-words">{{ sessionsError }}</p>
        </div>
        <div v-else-if="sessions.length === 0" class="text-center py-8 text-muted">
          <p>No active sessions found</p>
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="session in sessions"
            :key="session.id"
            class="flex items-center justify-between p-4 bg-card border border-border-color rounded-lg"
          >
            <div class="flex-1">
              <div class="flex items-center gap-2 mb-1">
                <p class="font-medium text-primary">{{ session.device || 'Unknown Device' }}</p>
                <span v-if="session.current" class="px-2 py-0.5 bg-primary/20 text-primary text-xs rounded">Current</span>
              </div>
              <p class="text-sm text-secondary">IP: {{ session.ip_address }}</p>
              <p class="text-xs text-muted mt-1">Last activity: {{ formatDate(session.last_activity) }}</p>
            </div>
            <button
              v-if="!session.current"
              @click="handleTerminateSession(session.id)"
              class="px-3 py-1.5 text-sm text-error hover:bg-error/10 rounded transition-colors"
              :disabled="terminatingSession === session.id"
            >
              <span v-if="terminatingSession === session.id">Terminating...</span>
              <span v-else>Terminate</span>
            </button>
          </div>
        </div>
        <div v-if="sessions.length > 0" class="mt-4 pt-4 border-t border-border-color">
          <button
            @click="handleLogoutAll"
            class="px-4 py-2 bg-error text-white rounded-lg hover:bg-error/90 transition-colors"
            :disabled="loggingOutAll"
          >
            <span v-if="loggingOutAll">Logging out...</span>
            <span v-else>Logout from All Sessions</span>
          </button>
          <p class="text-xs text-muted mt-2">This will log you out from all devices. You'll need to log in again.</p>
        </div>
      </Card>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotification } from '@/composables/useNotification'
import { authAPI, usersAPI } from '@/services/api'
import AppLayout from '@/components/layout/AppLayout.vue'
import Card from '@/components/common/Card.vue'
import Modal from '@/components/common/Modal.vue'

const router = useRouter()
const authStore = useAuthStore()
const notify = useNotification()

const changingPassword = ref(false)
const loadingSessions = ref(false)
const loggingOutAll = ref(false)
const terminatingSession = ref(null)
const sessionsError = ref(null)
const passwordForm = ref({
  old_password: '',
  new_password: '',
  new_password_confirm: '',
})
const sessions = ref([])
const showLogoutAllModal = ref(false)

const loadSessions = async () => {
  loadingSessions.value = true
  sessionsError.value = null
  try {
    const response = await authAPI.sessions()
    sessions.value = response.data.sessions || []
  } catch (err) {
    sessionsError.value = err.response?.data?.detail || err.response?.data?.error || 'Failed to load sessions'
    console.error('Failed to load sessions:', err)
  } finally {
    loadingSessions.value = false
  }
}

const handleChangePassword = async () => {
  if (passwordForm.value.new_password !== passwordForm.value.new_password_confirm) {
    notify.error('Passwords do not match')
    return
  }

  changingPassword.value = true
  try {
    await usersAPI.changePasswordMe({
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password,
      new_password_confirm: passwordForm.value.new_password_confirm,
    })
    
    notify.success('Password changed successfully')
    passwordForm.value = {
      old_password: '',
      new_password: '',
      new_password_confirm: '',
    }
  } catch (err) {
    const errorData = err.response?.data
    let errorMessage = 'Failed to change password'
    
    if (errorData) {
      if (errorData.old_password) {
        errorMessage = Array.isArray(errorData.old_password) ? errorData.old_password[0] : errorData.old_password
      } else if (errorData.new_password) {
        errorMessage = Array.isArray(errorData.new_password) ? errorData.new_password[0] : errorData.new_password
      } else if (errorData.detail) {
        errorMessage = errorData.detail
      } else if (errorData.error) {
        errorMessage = errorData.error
      }
    }
    
    notify.error(errorMessage)
  } finally {
    changingPassword.value = false
  }
}

const handleTerminateSession = async (sessionId) => {
  // Note: Since JWT is stateless, we can't actually terminate individual sessions
  // This is a placeholder for future implementation
  notify.info('Individual session termination is not yet implemented. Use "Logout from All Sessions" instead.')
}

const handleLogoutAll = async () => {
  loggingOutAll.value = true
  try {
    await authAPI.logoutAll()
    notify.success('Logged out from all sessions')
    
    // Clear auth state and redirect to login
    authStore.logout()
    router.push('/login')
  } catch (err) {
    const errorMessage = err.response?.data?.detail || err.response?.data?.error || 'Failed to logout from all sessions'
    notify.error(errorMessage)
  } finally {
    loggingOutAll.value = false
    showLogoutAllModal.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  try {
    const date = new Date(dateString)
    return date.toLocaleString()
  } catch {
    return dateString
  }
}

onMounted(() => {
  loadSessions()
})
</script>
