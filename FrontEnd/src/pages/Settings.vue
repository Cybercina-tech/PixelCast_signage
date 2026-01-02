<template>
  <AppLayout>
    <div class="settings-container">
      <div class="settings-layout">
        <!-- Left Navigation -->
        <aside class="settings-nav">
          <div class="nav-header">
            <h2 class="nav-title">Settings</h2>
          </div>
          <nav class="nav-menu">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              @click="activeTab = tab.id"
              class="nav-item"
              :class="{ 'nav-item-active': activeTab === tab.id }"
            >
              <component :is="tab.icon" class="nav-icon" />
              <span class="nav-label">{{ tab.label }}</span>
            </button>
          </nav>
        </aside>

        <!-- Right Content Panel -->
        <div class="settings-content">
          <transition name="fade-slide" mode="out-in">
            <!-- Profile Section -->
            <div v-if="activeTab === 'profile'" key="profile" class="settings-panel">
              <div class="panel-header">
                <h3 class="panel-title">Profile Settings</h3>
                <p class="panel-subtitle">Manage your account information and preferences</p>
              </div>

              <div class="panel-body">
                <!-- Avatar Upload -->
                <div class="setting-group">
                  <label class="setting-label">Profile Picture</label>
                  <div class="avatar-upload-area">
                    <div class="avatar-preview">
                      <img
                        v-if="profileSettings.avatar"
                        :src="profileSettings.avatar"
                        alt="Avatar"
                        class="avatar-image"
                      />
                      <div v-else class="avatar-placeholder">
                        {{ userInitials }}
                      </div>
                      <div class="avatar-overlay">
                        <CameraIcon class="w-6 h-6" />
                      </div>
                    </div>
                    <input
                      ref="avatarInput"
                      type="file"
                      accept="image/*"
                      class="hidden"
                      @change="handleAvatarUpload"
                    />
                    <button
                      @click="$refs.avatarInput?.click()"
                      class="avatar-upload-button"
                    >
                      Change Photo
                    </button>
                  </div>
                </div>

                <!-- User Info -->
                <div class="setting-group">
                  <label class="setting-label">Username</label>
                  <input
                    v-model="profileSettings.username"
                    type="text"
                    class="setting-input"
                    placeholder="Enter username"
                    @input="markAsChanged"
                  />
                </div>

                <div class="setting-group">
                  <label class="setting-label">Email</label>
                  <input
                    v-model="profileSettings.email"
                    type="email"
                    class="setting-input"
                    placeholder="Enter email"
                    @input="markAsChanged"
                  />
                </div>

                <div class="setting-group">
                  <label class="setting-label">Full Name</label>
                  <input
                    v-model="profileSettings.fullName"
                    type="text"
                    class="setting-input"
                    placeholder="Enter full name"
                    @input="markAsChanged"
                  />
                </div>

                <!-- Member Since Badge -->
                <div class="setting-group">
                  <label class="setting-label">Member Since</label>
                  <div class="member-badge">
                    <CalendarIcon class="w-4 h-4" />
                    <span>{{ memberSince }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Display Section -->
            <div v-else-if="activeTab === 'display'" key="display" class="settings-panel">
              <div class="panel-header">
                <h3 class="panel-title">Display Settings</h3>
                <p class="panel-subtitle">Customize your visual experience</p>
              </div>

              <div class="panel-body">
                <div class="setting-group">
                  <label class="setting-label">Global Theme</label>
                  <div class="theme-selector">
                    <button
                      v-for="theme in themes"
                      :key="theme.id"
                      @click="displaySettings.theme = theme.id; markAsChanged()"
                      class="theme-option"
                      :class="{ 'theme-option-active': displaySettings.theme === theme.id }"
                    >
                      <component :is="theme.icon" class="w-5 h-5" />
                      <span>{{ theme.label }}</span>
                    </button>
                  </div>
                </div>

                <div class="setting-group">
                  <label class="setting-label">Default Orientation</label>
                  <select
                    v-model="displaySettings.orientation"
                    class="setting-input"
                    @change="markAsChanged"
                  >
                    <option value="landscape">Landscape</option>
                    <option value="portrait">Portrait</option>
                    <option value="auto">Auto</option>
                  </select>
                </div>

                <div class="setting-group">
                  <label class="setting-label">Refresh Interval (seconds)</label>
                  <input
                    v-model.number="displaySettings.refreshInterval"
                    type="number"
                    min="1"
                    max="3600"
                    class="setting-input"
                    @input="markAsChanged"
                  />
                  <p class="setting-hint">How often the dashboard refreshes data</p>
                </div>
              </div>
            </div>

            <!-- Notifications Section -->
            <div v-else-if="activeTab === 'notifications'" key="notifications" class="settings-panel">
              <div class="panel-header">
                <h3 class="panel-title">Notification Center</h3>
                <p class="panel-subtitle">Control what notifications you receive</p>
              </div>

              <div class="panel-body">
                <div class="setting-item">
                  <div class="setting-item-content">
                    <div class="setting-item-info">
                      <h4 class="setting-item-title">Screen Offline Alerts</h4>
                      <p class="setting-item-description">Get notified when a screen goes offline</p>
                    </div>
                    <NeonToggle
                      v-model="notificationSettings.screenOffline"
                      @update:modelValue="markAsChanged"
                    />
                  </div>
                </div>

                <div class="setting-item">
                  <div class="setting-item-content">
                    <div class="setting-item-info">
                      <h4 class="setting-item-title">Template Push Success</h4>
                      <p class="setting-item-description">Notifications when content is successfully deployed</p>
                    </div>
                    <NeonToggle
                      v-model="notificationSettings.templatePush"
                      @update:modelValue="markAsChanged"
                    />
                  </div>
                </div>

                <div class="setting-item">
                  <div class="setting-item-content">
                    <div class="setting-item-info">
                      <h4 class="setting-item-title">System Updates</h4>
                      <p class="setting-item-description">Receive updates about system maintenance and new features</p>
                    </div>
                    <NeonToggle
                      v-model="notificationSettings.systemUpdates"
                      @update:modelValue="markAsChanged"
                    />
                  </div>
                </div>

                <div class="setting-item">
                  <div class="setting-item-content">
                    <div class="setting-item-info">
                      <h4 class="setting-item-title">Email Notifications</h4>
                      <p class="setting-item-description">Send notifications via email</p>
                    </div>
                    <NeonToggle
                      v-model="notificationSettings.email"
                      @update:modelValue="markAsChanged"
                    />
                  </div>
                </div>

                <div class="setting-group">
                  <label class="setting-label">Notification Email</label>
                  <input
                    v-model="notificationSettings.notificationEmail"
                    type="email"
                    class="setting-input"
                    placeholder="notifications@example.com"
                    @input="markAsChanged"
                  />
                </div>
              </div>
            </div>

            <!-- Security Section -->
            <div v-else-if="activeTab === 'security'" key="security" class="settings-panel">
              <div class="panel-header">
                <h3 class="panel-title">Security Settings</h3>
                <p class="panel-subtitle">Manage your account security and sessions</p>
              </div>

              <div class="panel-body">
                <!-- Password Change -->
                <div class="setting-group">
                  <label class="setting-label">Change Password</label>
                  <div class="password-fields">
                    <input
                      v-model="securitySettings.currentPassword"
                      type="password"
                      class="setting-input"
                      placeholder="Current password"
                      @input="markAsChanged"
                    />
                    <input
                      v-model="securitySettings.newPassword"
                      type="password"
                      class="setting-input"
                      placeholder="New password"
                      @input="markAsChanged"
                    />
                    <input
                      v-model="securitySettings.confirmPassword"
                      type="password"
                      class="setting-input"
                      placeholder="Confirm new password"
                      @input="markAsChanged"
                    />
                  </div>
                </div>

                <!-- Session Management -->
                <div class="setting-group">
                  <label class="setting-label">Active Sessions</label>
                  <div class="sessions-list">
                    <div
                      v-for="session in activeSessions"
                      :key="session.id"
                      class="session-item"
                    >
                      <div class="session-info">
                        <div class="session-device">
                          <component :is="session.deviceIcon" class="w-5 h-5" />
                          <div>
                            <p class="session-device-name">{{ session.device }}</p>
                            <p class="session-location">{{ session.location }}</p>
                          </div>
                        </div>
                        <div class="session-meta">
                          <span class="session-time">{{ session.lastActive }}</span>
                          <span
                            v-if="session.current"
                            class="session-badge"
                          >
                            Current
                          </span>
                        </div>
                      </div>
                      <button
                        v-if="!session.current"
                        @click="revokeSession(session.id)"
                        class="session-revoke"
                      >
                        Revoke
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- System Section -->
            <div v-else-if="activeTab === 'system'" key="system" class="settings-panel">
              <div class="panel-header">
                <h3 class="panel-title">System Settings</h3>
                <p class="panel-subtitle">Advanced system configuration</p>
              </div>

              <div class="panel-body">
                <div class="setting-group">
                  <label class="setting-label">API Base URL</label>
                  <input
                    v-model="systemSettings.apiBaseUrl"
                    type="text"
                    class="setting-input"
                    placeholder="http://localhost:8000/api"
                    @input="markAsChanged"
                  />
                </div>

                <div class="setting-group">
                  <label class="setting-label">WebSocket URL</label>
                  <input
                    v-model="systemSettings.wsUrl"
                    type="text"
                    class="setting-input"
                    placeholder="ws://localhost:8000/ws/dashboard/"
                    @input="markAsChanged"
                  />
                </div>

                <div class="setting-group">
                  <label class="setting-label">Storage Backend</label>
                  <select
                    v-model="systemSettings.storageBackend"
                    class="setting-input"
                    @change="markAsChanged"
                  >
                    <option value="local">Local File System</option>
                    <option value="s3">Amazon S3</option>
                  </select>
                </div>

                <div v-if="systemSettings.storageBackend === 's3'" class="setting-group">
                  <label class="setting-label">S3 Bucket Name</label>
                  <input
                    v-model="systemSettings.s3Bucket"
                    type="text"
                    class="setting-input"
                    placeholder="your-bucket-name"
                    @input="markAsChanged"
                  />
                </div>

                <div v-if="systemSettings.storageBackend === 's3'" class="setting-group">
                  <label class="setting-label">S3 Region</label>
                  <input
                    v-model="systemSettings.s3Region"
                    type="text"
                    class="setting-input"
                    placeholder="us-east-1"
                    @input="markAsChanged"
                  />
                </div>
              </div>
            </div>
          </transition>
        </div>
      </div>

      <!-- Sticky Action Bar -->
      <transition name="slide-up">
        <div v-if="hasChanges" class="action-bar">
          <div class="action-bar-content">
            <span class="action-bar-text">You have unsaved changes</span>
            <div class="action-bar-buttons">
              <button
                @click="discardChanges"
                class="action-button action-button-discard"
              >
                Discard
              </button>
              <button
                @click="saveChanges"
                class="action-button action-button-save"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      </transition>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { useNotification } from '@/composables/useNotification'
import AppLayout from '@/components/layout/AppLayout.vue'
import NeonToggle from '@/components/common/NeonToggle.vue'
import {
  UserIcon,
  PaintBrushIcon,
  BellIcon,
  ShieldCheckIcon,
  Cog6ToothIcon,
  CameraIcon,
  CalendarIcon,
  ComputerDesktopIcon,
  DevicePhoneMobileIcon,
  MoonIcon,
  SunIcon,
} from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()
const notify = useNotification()

// Tabs configuration
const tabs = [
  { id: 'profile', label: 'Profile', icon: UserIcon },
  { id: 'display', label: 'Display', icon: PaintBrushIcon },
  { id: 'notifications', label: 'Notifications', icon: BellIcon },
  { id: 'security', label: 'Security', icon: ShieldCheckIcon },
  { id: 'system', label: 'System', icon: Cog6ToothIcon },
]

const activeTab = ref('profile')
const hasChanges = ref(false)

// User data
const user = computed(() => authStore.user)
const userInitials = computed(() => {
  if (!user.value?.username) return 'U'
  const parts = user.value.username.split(' ')
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return user.value.username.substring(0, 2).toUpperCase()
})

const memberSince = computed(() => {
  if (!user.value) return 'N/A'
  const dateStr = user.value.date_joined || user.value.created_at || user.value.joined_at
  if (!dateStr) return 'N/A'
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long' })
  } catch {
    return 'N/A'
  }
})

// Settings state
const profileSettings = ref({
  avatar: null,
  username: '',
  email: '',
  fullName: '',
})

const displaySettings = ref({
  theme: themeStore.theme || 'dark',
  orientation: 'landscape',
  refreshInterval: 30,
})

const themes = [
  { id: 'dark', label: 'Deep Space', icon: MoonIcon },
  { id: 'light', label: 'Light', icon: SunIcon },
]

const notificationSettings = ref({
  screenOffline: true,
  templatePush: true,
  systemUpdates: false,
  email: false,
  notificationEmail: user.value?.email || '',
})

const securitySettings = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
})

const systemSettings = ref({
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  wsUrl: import.meta.env.VITE_WS_HOST || 'ws://localhost:8000/ws/dashboard/',
  storageBackend: 'local',
  s3Bucket: '',
  s3Region: 'us-east-1',
})

// Active sessions (mock data)
const activeSessions = ref([
  {
    id: 1,
    device: 'Chrome on Windows',
    location: 'New York, US',
    lastActive: '2 minutes ago',
    current: true,
    deviceIcon: ComputerDesktopIcon,
  },
  {
    id: 2,
    device: 'Safari on iPhone',
    location: 'New York, US',
    lastActive: '1 hour ago',
    current: false,
    deviceIcon: DevicePhoneMobileIcon,
  },
])

// Track changes - initialize after all settings are defined
const originalSettings = ref({
  profile: JSON.parse(JSON.stringify(profileSettings.value)),
  display: JSON.parse(JSON.stringify(displaySettings.value)),
  notifications: JSON.parse(JSON.stringify(notificationSettings.value)),
  security: JSON.parse(JSON.stringify(securitySettings.value)),
  system: JSON.parse(JSON.stringify(systemSettings.value)),
})

// Initialize profile settings from user data
watch(user, (newUser) => {
  if (newUser) {
    profileSettings.value = {
      avatar: newUser.avatar || null,
      username: newUser.username || '',
      email: newUser.email || '',
      fullName: newUser.full_name || newUser.first_name + ' ' + newUser.last_name || '',
    }
    notificationSettings.value.notificationEmail = newUser.email || ''
    originalSettings.value.profile = JSON.parse(JSON.stringify(profileSettings.value))
  }
}, { immediate: true })

const markAsChanged = () => {
  hasChanges.value = true
}

const discardChanges = () => {
  profileSettings.value = JSON.parse(JSON.stringify(originalSettings.value.profile))
  displaySettings.value = JSON.parse(JSON.stringify(originalSettings.value.display))
  notificationSettings.value = JSON.parse(JSON.stringify(originalSettings.value.notifications))
  securitySettings.value = JSON.parse(JSON.stringify(originalSettings.value.security))
  systemSettings.value = JSON.parse(JSON.stringify(originalSettings.value.system))
  hasChanges.value = false
  notify.info('Changes discarded')
}

const saveChanges = async () => {
  try {
    // Save profile settings
    if (activeTab.value === 'profile') {
      // TODO: API call to update profile
      originalSettings.value.profile = JSON.parse(JSON.stringify(profileSettings.value))
    }

    // Save display settings
    if (activeTab.value === 'display') {
      if (displaySettings.value.theme !== themeStore.theme) {
        themeStore.setTheme(displaySettings.value.theme)
      }
      localStorage.setItem('displaySettings', JSON.stringify(displaySettings.value))
      originalSettings.value.display = JSON.parse(JSON.stringify(displaySettings.value))
    }

    // Save notification settings
    if (activeTab.value === 'notifications') {
      localStorage.setItem('notificationSettings', JSON.stringify(notificationSettings.value))
      originalSettings.value.notifications = JSON.parse(JSON.stringify(notificationSettings.value))
    }

    // Save security settings
    if (activeTab.value === 'security') {
      if (securitySettings.value.newPassword && securitySettings.value.newPassword === securitySettings.value.confirmPassword) {
        // TODO: API call to change password
        securitySettings.value.currentPassword = ''
        securitySettings.value.newPassword = ''
        securitySettings.value.confirmPassword = ''
        originalSettings.value.security = JSON.parse(JSON.stringify(securitySettings.value))
      }
    }

    // Save system settings
    if (activeTab.value === 'system') {
      localStorage.setItem('systemSettings', JSON.stringify(systemSettings.value))
      originalSettings.value.system = JSON.parse(JSON.stringify(systemSettings.value))
    }

    hasChanges.value = false
    notify.success('Settings saved successfully')
  } catch (error) {
    console.error('Error saving settings:', error)
    notify.error('Failed to save settings')
  }
}

const handleAvatarUpload = (event) => {
  const file = event.target.files?.[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      profileSettings.value.avatar = e.target?.result
      markAsChanged()
    }
    reader.readAsDataURL(file)
  }
}

const revokeSession = (sessionId) => {
  activeSessions.value = activeSessions.value.filter(s => s.id !== sessionId)
  notify.success('Session revoked')
}

// Load saved settings
const loadSettings = () => {
  const savedDisplay = localStorage.getItem('displaySettings')
  if (savedDisplay) {
    displaySettings.value = { ...displaySettings.value, ...JSON.parse(savedDisplay) }
  }

  const savedNotifications = localStorage.getItem('notificationSettings')
  if (savedNotifications) {
    notificationSettings.value = { ...notificationSettings.value, ...JSON.parse(savedNotifications) }
  }

  const savedSystem = localStorage.getItem('systemSettings')
  if (savedSystem) {
    systemSettings.value = { ...systemSettings.value, ...JSON.parse(savedSystem) }
  }
}

// Watch for tab changes to reset changes flag
watch(activeTab, () => {
  hasChanges.value = false
})

// Initialize
loadSettings()
</script>

<style scoped>
/* Settings Container - Soft Paper Background */
.settings-container {
  min-height: calc(100vh - 8rem);
  padding: 2rem;
  background: #F8F9FA; /* Soft Paper */
  transition: background-color 0.3s ease;
}

.dark .settings-container {
  background: var(--bg-primary);
}

.settings-layout {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

/* Left Navigation - Warm Grey Background */
.settings-nav {
  background: #F1F3F5; /* Very subtle warm-grey */
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 16px;
  padding: 1.5rem;
  height: fit-content;
  position: sticky;
  top: 6rem;
  transition: all 0.3s ease;
}

.dark .settings-nav {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.nav-header {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  transition: border-color 0.3s ease;
}

.dark .nav-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.nav-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #2D3436; /* Dark Slate */
  transition: color 0.3s ease;
}

.dark .nav-title {
  background: linear-gradient(135deg, #06b6d4, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-menu {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: transparent;
  border: none;
  border-radius: 10px;
  color: #636E72; /* Cool Grey */
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
  font-size: 0.9375rem;
  font-weight: 500;
}

.nav-item:hover {
  background: rgba(0, 0, 0, 0.03);
  color: #2D3436; /* Dark Slate */
}

.nav-item-active {
  background: rgba(9, 132, 227, 0.1); /* Professional Blue with opacity */
  border-left: 3px solid #0984E3; /* Professional Blue */
  color: #0984E3;
  box-shadow: inset 0 0 10px rgba(9, 132, 227, 0.05);
}

.dark .nav-item {
  color: rgba(255, 255, 255, 0.6);
}

.dark .nav-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.8);
}

.dark .nav-item-active {
  background: rgba(6, 182, 212, 0.1);
  border-left-color: #06b6d4;
  color: #06b6d4;
  box-shadow: inset 0 0 20px rgba(6, 182, 212, 0.1);
}

.nav-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  color: #2D3436; /* Dark Slate */
  background: #F1F2F6; /* Faint circular background */
  padding: 6px;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.nav-item:hover .nav-icon {
  background: rgba(9, 132, 227, 0.1);
  color: #0984E3;
}

.nav-item-active .nav-icon {
  background: rgba(9, 132, 227, 0.15);
  color: #0984E3;
}

.dark .nav-icon {
  color: rgba(255, 255, 255, 0.6);
  background: rgba(255, 255, 255, 0.05);
}

.dark .nav-item:hover .nav-icon {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
}

.dark .nav-item-active .nav-icon {
  background: rgba(6, 182, 212, 0.2);
  color: #06b6d4;
}

.nav-label {
  flex: 1;
}

/* Right Content Panel */
.settings-content {
  min-height: 600px;
}

/* Content Cards - Pure White with Diffused Shadow */
.settings-panel {
  background: #FFFFFF; /* Pure white */
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03); /* Very soft diffused shadow */
  animation: fadeIn 0.3s ease;
  transition: all 0.3s ease;
}

.dark .settings-panel {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: none;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.panel-header {
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  transition: border-color 0.3s ease;
}

.dark .panel-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.panel-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #2D3436; /* Bold dark-grey */
  margin-bottom: 0.5rem;
  transition: color 0.3s ease;
}

.dark .panel-title {
  color: rgba(255, 255, 255, 0.9);
}

.panel-subtitle {
  font-size: 0.9375rem;
  color: #636E72; /* Cool Grey - muted */
  transition: color 0.3s ease;
}

.dark .panel-subtitle {
  color: rgba(255, 255, 255, 0.5);
}

.panel-body {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* Setting Groups */
.setting-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.setting-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #2D3436; /* Dark Slate */
  text-transform: uppercase;
  letter-spacing: 0.05em;
  transition: color 0.3s ease;
}

.dark .setting-label {
  color: rgba(255, 255, 255, 0.8);
}

/* Form Inputs - White Background with Soft Focus Glow */
.setting-input {
  width: 100%;
  padding: 0.875rem 1rem;
  background: #FFFFFF;
  border: 1.5px solid #E2E8F0;
  border-radius: 10px;
  color: #2D3436; /* Dark Slate */
  font-size: 0.9375rem;
  transition: all 0.3s ease;
  outline: none;
}

.setting-input::placeholder {
  color: #94A3B8; /* Muted grey */
}

.setting-input:focus {
  border-color: #0984E3; /* Professional Blue */
  box-shadow: 
    0 0 0 2px rgba(9, 132, 227, 0.1), /* Soft glow */
    0 2px 4px rgba(0, 0, 0, 0.05);
  background: #FFFFFF;
}

.dark .setting-input {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
}

.dark .setting-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.dark .setting-input:focus {
  border-color: #06b6d4;
  box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.1), 0 0 20px rgba(6, 182, 212, 0.2);
  background: rgba(255, 255, 255, 0.08);
}

.setting-hint {
  font-size: 0.75rem;
  color: #636E72; /* Cool Grey */
  margin-top: 0.25rem;
  transition: color 0.3s ease;
}

.dark .setting-hint {
  color: rgba(255, 255, 255, 0.4);
}

/* Avatar Upload - Clean Circular Border */
.avatar-upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.avatar-preview {
  position: relative;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid #E2E8F0; /* Clean border */
  cursor: pointer;
  transition: all 0.3s ease;
}

.avatar-preview:hover {
  border-color: #0984E3; /* Professional Blue */
  box-shadow: 0 4px 12px rgba(9, 132, 227, 0.2);
}

.avatar-preview:hover .avatar-overlay {
  opacity: 1;
}

.avatar-image,
.avatar-placeholder {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  background: linear-gradient(135deg, #7FCDBB, #6BCAE2); /* Soft Mint to Light Blue */
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2.5rem;
  font-weight: 700;
}

.avatar-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.avatar-upload-button {
  padding: 0.5rem 1.5rem;
  background: transparent; /* Ghost style */
  border: 1.5px solid #E2E8F0;
  border-radius: 8px;
  color: #2D3436; /* Dark Slate */
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.avatar-upload-button:hover {
  background: rgba(9, 132, 227, 0.05);
  border-color: #0984E3;
  color: #0984E3;
}

.dark .avatar-preview {
  border-color: rgba(6, 182, 212, 0.3);
}

.dark .avatar-preview:hover {
  border-color: #06b6d4;
  box-shadow: 0 0 30px rgba(6, 182, 212, 0.4);
}

.dark .avatar-upload-button {
  background: rgba(6, 182, 212, 0.1);
  border-color: rgba(6, 182, 212, 0.3);
  color: #06b6d4;
}

.dark .avatar-upload-button:hover {
  background: rgba(6, 182, 212, 0.2);
  border-color: #06b6d4;
  box-shadow: 0 0 15px rgba(6, 182, 212, 0.3);
}

/* Member Badge - Soft Mint or Light Blue */
.member-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(127, 205, 187, 0.15); /* Soft Mint */
  border: 1px solid rgba(127, 205, 187, 0.3);
  border-radius: 8px;
  color: #2D3436; /* Dark Slate */
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.dark .member-badge {
  background: rgba(6, 182, 212, 0.1);
  border-color: rgba(6, 182, 212, 0.3);
  color: #06b6d4;
}

/* Theme Selector */
.theme-selector {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.theme-option {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 1rem;
  background: #FFFFFF;
  border: 1.5px solid #E2E8F0;
  border-radius: 12px;
  color: #2D3436; /* Dark Slate */
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9375rem;
  font-weight: 500;
}

.theme-option:hover {
  background: #F8F9FA;
  border-color: #0984E3;
  color: #0984E3;
}

.theme-option-active {
  background: rgba(9, 132, 227, 0.1);
  border-color: #0984E3; /* Professional Blue */
  color: #0984E3;
  box-shadow: 0 2px 8px rgba(9, 132, 227, 0.15);
}

.dark .theme-option {
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.6);
}

.dark .theme-option:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
}

.dark .theme-option-active {
  background: rgba(6, 182, 212, 0.1);
  border-color: #06b6d4;
  color: #06b6d4;
  box-shadow: 0 0 20px rgba(6, 182, 212, 0.3);
}

/* Setting Items (for toggles) */
.setting-item {
  padding: 1.5rem;
  background: #FFFFFF; /* Pure white */
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 12px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
}

.setting-item:hover {
  background: #FFFFFF;
  border-color: rgba(9, 132, 227, 0.2);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
}

.dark .setting-item {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  box-shadow: none;
}

.dark .setting-item:hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.1);
}

.setting-item-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
}

.setting-item-info {
  flex: 1;
}

.setting-item-title {
  font-size: 1rem;
  font-weight: 600;
  color: #2D3436; /* Bold dark-grey */
  margin-bottom: 0.25rem;
  transition: color 0.3s ease;
}

.dark .setting-item-title {
  color: rgba(255, 255, 255, 0.9);
}

.setting-item-description {
  font-size: 0.875rem;
  color: #636E72; /* Cool Grey */
  line-height: 1.5;
  transition: color 0.3s ease;
}

.dark .setting-item-description {
  color: rgba(255, 255, 255, 0.5);
}

/* Password Fields */
.password-fields {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Sessions List */
.sessions-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.session-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  background: #FFFFFF; /* Pure white */
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 12px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
}

.session-item:hover {
  background: #FFFFFF;
  border-color: rgba(9, 132, 227, 0.2);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
}

.dark .session-item {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  box-shadow: none;
}

.dark .session-item:hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.1);
}

.session-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex: 1;
  gap: 1rem;
}

.session-device {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.session-device svg {
  color: #636E72; /* Cool Grey */
  transition: color 0.3s ease;
}

.session-device-name {
  font-size: 0.9375rem;
  font-weight: 500;
  color: #2D3436; /* Dark Slate */
  margin-bottom: 0.25rem;
  transition: color 0.3s ease;
}

.session-location {
  font-size: 0.75rem;
  color: #636E72; /* Cool Grey */
  transition: color 0.3s ease;
}

.session-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.session-time {
  font-size: 0.75rem;
  color: #636E72; /* Cool Grey */
  transition: color 0.3s ease;
}

.dark .session-device svg {
  color: rgba(255, 255, 255, 0.5);
}

.dark .session-device-name {
  color: rgba(255, 255, 255, 0.9);
}

.dark .session-location {
  color: rgba(255, 255, 255, 0.5);
}

.dark .session-time {
  color: rgba(255, 255, 255, 0.4);
}

.session-badge {
  padding: 0.25rem 0.75rem;
  background: rgba(127, 205, 187, 0.2); /* Soft Mint */
  border: 1px solid rgba(127, 205, 187, 0.4);
  border-radius: 6px;
  color: #2D3436; /* Dark Slate */
  font-size: 0.75rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.dark .session-badge {
  background: rgba(16, 185, 129, 0.2);
  border-color: rgba(16, 185, 129, 0.4);
  color: #10b981;
}

.session-revoke {
  padding: 0.5rem 1rem;
  background: rgba(255, 107, 107, 0.1); /* Soft Coral */
  border: 1px solid rgba(255, 107, 107, 0.3);
  border-radius: 8px;
  color: #FF6B6B; /* Soft Coral red */
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.session-revoke:hover {
  background: rgba(255, 107, 107, 0.15);
  border-color: #FF6B6B;
  box-shadow: 0 2px 8px rgba(255, 107, 107, 0.2);
}

.dark .session-revoke {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
  color: #ef4444;
}

.dark .session-revoke:hover {
  background: rgba(239, 68, 68, 0.2);
  border-color: #ef4444;
  box-shadow: 0 0 15px rgba(239, 68, 68, 0.3);
}

/* Sticky Action Bar */
.action-bar {
  position: fixed;
  bottom: 2.5rem; /* Above footer (footer is 2.5rem) */
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  width: calc(100% - 4rem);
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
}

.action-bar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 2rem;
  background: #FFFFFF; /* Pure white */
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1); /* Soft shadow */
  transition: all 0.3s ease;
}

.dark .action-bar-content {
  background: rgba(10, 10, 26, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

.action-bar-text {
  font-size: 0.9375rem;
  color: #2D3436; /* Dark Slate */
  font-weight: 500;
  transition: color 0.3s ease;
}

.dark .action-bar-text {
  color: rgba(255, 255, 255, 0.7);
}

.action-bar-buttons {
  display: flex;
  gap: 1rem;
}

.action-button {
  padding: 0.625rem 1.5rem;
  border-radius: 8px;
  font-size: 0.9375rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

/* Buttons - Ghost Style for Secondary, Solid Indigo Blue for Primary */
.action-button-discard {
  background: transparent; /* Ghost style */
  border: 1.5px solid #E2E8F0;
  color: #2D3436; /* Dark Slate */
  transition: all 0.3s ease;
}

.action-button-discard:hover {
  background: rgba(0, 0, 0, 0.03);
  border-color: #94A3B8;
  color: #1E293B;
}

.dark .action-button-discard {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
}

.dark .action-button-discard:hover {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
}

.action-button-save {
  background: #4F46E5; /* Indigo Blue */
  color: white;
  border: none;
  box-shadow: 0 2px 8px rgba(79, 70, 229, 0.3);
  transition: all 0.3s ease;
}

.action-button-save:hover {
  background: #4338CA; /* Darker Indigo */
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
  transform: translateY(-1px);
}

.dark .action-button-save {
  background: linear-gradient(135deg, #06b6d4, #8b5cf6);
  box-shadow: 0 0 20px rgba(6, 182, 212, 0.3);
}

.dark .action-button-save:hover {
  box-shadow: 0 0 30px rgba(6, 182, 212, 0.5), 0 0 50px rgba(139, 92, 246, 0.3);
  transform: translateY(-2px);
}

/* Transitions */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(100%);
}

/* Responsive */
@media (max-width: 1024px) {
  .settings-layout {
    grid-template-columns: 1fr;
  }

  .settings-nav {
    position: static;
    display: flex;
    flex-direction: row;
    overflow-x: auto;
    padding: 1rem;
  }

  .nav-menu {
    flex-direction: row;
    gap: 0.5rem;
  }

  .nav-item {
    white-space: nowrap;
  }

  .action-bar {
    width: calc(100% - 2rem);
    left: 1rem;
    transform: none;
  }
}
</style>
