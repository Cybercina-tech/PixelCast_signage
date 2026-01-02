<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 flex items-center justify-center px-4 py-12 relative overflow-hidden">
    <!-- Animated Background Elements -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-40 -right-40 w-80 h-80 bg-blue-200 dark:bg-blue-900/20 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob"></div>
      <div class="absolute -bottom-40 -left-40 w-80 h-80 bg-indigo-200 dark:bg-indigo-900/20 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-2000"></div>
      <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-purple-200 dark:bg-purple-900/20 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-4000"></div>
    </div>

    <div class="w-full max-w-4xl relative z-10">
      <!-- Frosted Glass Card -->
      <div 
        v-motion
        :initial="{ opacity: 0, y: 20 }"
        :enter="{ opacity: 1, y: 0 }"
        :transition="{ duration: 500 }"
        class="bg-card backdrop-blur-xl rounded-3xl shadow-2xl border border-border-color overflow-hidden"
        style="background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(20px); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);"
      >
        <!-- Header with Logo -->
        <div class="bg-gradient-to-r from-slate-900 via-emerald-700 to-emerald-600 dark:from-emerald-600 dark:via-emerald-500 dark:to-emerald-400 px-8 py-10 text-center relative overflow-hidden">
          <div class="absolute inset-0 opacity-10">
            <div class="absolute inset-0" style="background-image: radial-gradient(circle at 2px 2px, white 1px, transparent 0); background-size: 40px 40px;"></div>
          </div>
          
          <div class="relative z-10">
            <div class="inline-flex items-center justify-center w-20 h-20 bg-white/10 rounded-full mb-4 backdrop-blur-sm border border-white/20">
              <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <h1 class="text-4xl font-bold text-white mb-2 tracking-tight">ScreenGram</h1>
            <p class="text-emerald-100 dark:text-emerald-900 text-base font-medium">Installation Wizard</p>
          </div>
        </div>

        <!-- Stepper Navigation -->
        <div class="px-8 pt-8 pb-4 border-b border-border-color">
          <div class="flex items-center justify-between">
            <div
              v-for="(step, index) in steps"
              :key="index"
              class="flex items-center flex-1"
            >
              <!-- Step Circle -->
              <div class="flex flex-col items-center flex-1">
                <div
                  class="w-12 h-12 rounded-full flex items-center justify-center transition-all duration-300"
                  :class="getStepClass(index)"
                >
                  <component
                    :is="step.icon"
                    v-if="currentStep > index"
                    class="w-6 h-6"
                  />
                  <span v-else class="text-sm font-semibold">{{ index + 1 }}</span>
                </div>
                <span
                  class="mt-2 text-xs font-medium transition-colors duration-300"
                  :class="currentStep >= index ? 'text-primary' : 'text-secondary'"
                >
                  {{ step.label }}
                </span>
              </div>

              <!-- Connector Line -->
              <div
                v-if="index < steps.length - 1"
                class="flex-1 h-0.5 mx-2 transition-all duration-300"
                :class="currentStep > index ? 'bg-emerald-500' : 'bg-slate-200 dark:bg-slate-700'"
              ></div>
            </div>
          </div>
        </div>

        <!-- Step Content -->
        <div class="px-8 py-8 min-h-[400px]">
          <transition
            name="step"
            mode="out-in"
          >
            <!-- Step 1: Welcome -->
            <div
              v-if="currentStep === 1"
              key="step-1"
              class="space-y-6"
            >
              <div class="text-center">
                <div class="inline-flex items-center justify-center w-16 h-16 bg-emerald-100 dark:bg-emerald-900/30 rounded-full mb-4">
                  <RocketLaunchIcon class="w-8 h-8 text-emerald-600 dark:text-emerald-400" />
                </div>
                <h2 class="text-3xl font-bold text-primary mb-3">Welcome to ScreenGram</h2>
                <p class="text-secondary text-lg max-w-2xl mx-auto">
                  Let's get your digital signage system up and running. This wizard will guide you through the installation process.
                </p>
              </div>

              <div class="mt-8 space-y-4">
                <div class="flex items-start gap-3 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-xl">
                  <CheckCircleIcon class="w-6 h-6 text-emerald-600 dark:text-emerald-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 class="font-semibold text-primary mb-1">Database Configuration</h3>
                    <p class="text-sm text-secondary">Connect to your PostgreSQL database</p>
                  </div>
                </div>
                <div class="flex items-start gap-3 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-xl">
                  <CheckCircleIcon class="w-6 h-6 text-emerald-600 dark:text-emerald-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 class="font-semibold text-primary mb-1">Admin Account</h3>
                    <p class="text-sm text-secondary">Create your master administrator account</p>
                  </div>
                </div>
                <div class="flex items-start gap-3 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-xl">
                  <CheckCircleIcon class="w-6 h-6 text-emerald-600 dark:text-emerald-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 class="font-semibold text-primary mb-1">System Setup</h3>
                    <p class="text-sm text-secondary">Finalize installation and configure system</p>
                  </div>
                </div>
              </div>

              <div class="flex justify-center pt-4">
                <button
                  @click="nextStep"
                  class="btn-primary px-8 py-3.5 rounded-xl text-lg font-semibold flex items-center gap-2"
                >
                  Start Installation
                  <ArrowRightIcon class="w-5 h-5" />
                </button>
              </div>
            </div>

            <!-- Step 2: Database -->
            <div
              v-else-if="currentStep === 2"
              key="step-2"
              class="space-y-6"
            >
              <div class="text-center mb-6">
                <div class="inline-flex items-center justify-center w-16 h-16 bg-blue-100 dark:bg-blue-900/30 rounded-full mb-4">
                  <ServerIcon class="w-8 h-8 text-blue-600 dark:text-blue-400" />
                </div>
                <h2 class="text-3xl font-bold text-primary mb-2">Database Configuration</h2>
                <p class="text-secondary">Enter your PostgreSQL database credentials</p>
              </div>

              <form @submit.prevent="testDatabaseConnection" class="space-y-5 max-w-2xl mx-auto">
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label for="db-host" class="label-base block text-sm mb-2">
                      Host <span class="text-red-500">*</span>
                    </label>
                    <input
                      id="db-host"
                      v-model="setupData.db.host"
                      type="text"
                      required
                      class="input-base w-full px-4 py-3 rounded-xl"
                      placeholder="localhost"
                    />
                  </div>
                  <div>
                    <label for="db-port" class="label-base block text-sm mb-2">
                      Port <span class="text-red-500">*</span>
                    </label>
                    <input
                      id="db-port"
                      v-model.number="setupData.db.port"
                      type="number"
                      required
                      class="input-base w-full px-4 py-3 rounded-xl"
                      placeholder="5432"
                    />
                  </div>
                </div>

                <div>
                  <label for="db-name" class="label-base block text-sm mb-2">
                    Database Name <span class="text-red-500">*</span>
                  </label>
                  <input
                    id="db-name"
                    v-model="setupData.db.name"
                    type="text"
                    required
                    class="input-base w-full px-4 py-3 rounded-xl"
                    placeholder="screengram_db"
                  />
                </div>

                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label for="db-user" class="label-base block text-sm mb-2">
                      Username <span class="text-red-500">*</span>
                    </label>
                    <input
                      id="db-user"
                      v-model="setupData.db.user"
                      type="text"
                      required
                      class="input-base w-full px-4 py-3 rounded-xl"
                      placeholder="screengram_user"
                    />
                  </div>
                  <div>
                    <label for="db-password" class="label-base block text-sm mb-2">
                      Password <span class="text-red-500">*</span>
                    </label>
                    <div class="relative">
                      <input
                        id="db-password"
                        v-model="setupData.db.password"
                        :type="showDbPassword ? 'text' : 'password'"
                        required
                        class="input-base w-full px-4 py-3 rounded-xl pr-12"
                        placeholder="Enter password"
                      />
                      <button
                        type="button"
                        @click="showDbPassword = !showDbPassword"
                        class="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-emerald-600 dark:hover:text-emerald-400"
                      >
                        <EyeIcon v-if="!showDbPassword" class="w-5 h-5" />
                        <EyeSlashIcon v-else class="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                </div>

                <!-- Connection Status -->
                <transition name="fade">
                  <div
                    v-if="dbStatus.message"
                    class="p-4 rounded-xl"
                    :class="dbStatus.success ? 'bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800' : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'"
                  >
                    <div class="flex items-start gap-2">
                      <CheckCircleIcon v-if="dbStatus.success" class="w-5 h-5 text-emerald-600 dark:text-emerald-400 flex-shrink-0 mt-0.5" />
                      <XCircleIcon v-else class="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                      <p :class="dbStatus.success ? 'text-emerald-700 dark:text-emerald-300' : 'text-red-700 dark:text-red-300'">
                        {{ dbStatus.message }}
                      </p>
                    </div>
                  </div>
                </transition>

                <div class="flex gap-3 pt-2">
                  <button
                    type="button"
                    @click="prevStep"
                    class="btn-secondary flex-1 py-3 px-4 rounded-xl"
                  >
                    Back
                  </button>
                  <button
                    type="button"
                    @click="testDatabaseConnection"
                    :disabled="dbStatus.loading"
                    class="btn-secondary flex-1 py-3 px-4 rounded-xl disabled:opacity-50 flex items-center justify-center gap-2"
                  >
                    <svg
                      v-if="dbStatus.loading"
                      class="animate-spin h-5 w-5"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>{{ dbStatus.loading ? 'Testing...' : 'Test Connection' }}</span>
                  </button>
                  <button
                    v-if="dbStatus.success"
                    type="button"
                    @click="nextStep"
                    class="btn-primary flex-1 py-3.5 px-4 rounded-xl"
                  >
                    Continue
                    <ArrowRightIcon class="w-5 h-5 inline-block ml-2" />
                  </button>
                </div>
              </form>
            </div>

            <!-- Step 3: Admin -->
            <div
              v-else-if="currentStep === 3"
              key="step-3"
              class="space-y-6"
            >
              <div class="text-center mb-6">
                <div class="inline-flex items-center justify-center w-16 h-16 bg-purple-100 dark:bg-purple-900/30 rounded-full mb-4">
                  <ShieldCheckIcon class="w-8 h-8 text-purple-600 dark:text-purple-400" />
                </div>
                <h2 class="text-3xl font-bold text-primary mb-2">Create Administrator Account</h2>
                <p class="text-secondary">Set up your master administrator account</p>
              </div>

              <form @submit.prevent="createAdmin" class="space-y-5 max-w-2xl mx-auto">
                <div>
                  <label for="admin-username" class="label-base block text-sm mb-2">
                    Username <span class="text-red-500">*</span>
                  </label>
                  <input
                    id="admin-username"
                    v-model="setupData.admin.username"
                    type="text"
                    required
                    class="input-base w-full px-4 py-3 rounded-xl"
                    placeholder="admin"
                  />
                  <p v-if="errors.username" class="text-red-500 text-sm mt-1">{{ errors.username[0] }}</p>
                </div>

                <div>
                  <label for="admin-email" class="label-base block text-sm mb-2">
                    Email <span class="text-red-500">*</span>
                  </label>
                  <input
                    id="admin-email"
                    v-model="setupData.admin.email"
                    type="email"
                    required
                    class="input-base w-full px-4 py-3 rounded-xl"
                    placeholder="admin@example.com"
                  />
                  <p v-if="errors.email" class="text-red-500 text-sm mt-1">{{ errors.email[0] }}</p>
                </div>

                <div>
                  <label for="admin-password" class="label-base block text-sm mb-2">
                    Password <span class="text-red-500">*</span>
                  </label>
                  <div class="relative">
                    <input
                      id="admin-password"
                      v-model="setupData.admin.password"
                      :type="showAdminPassword ? 'text' : 'password'"
                      required
                      minlength="8"
                      class="input-base w-full px-4 py-3 rounded-xl pr-12"
                      placeholder="Minimum 8 characters"
                    />
                    <button
                      type="button"
                      @click="showAdminPassword = !showAdminPassword"
                      class="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-emerald-600 dark:hover:text-emerald-400"
                    >
                      <EyeIcon v-if="!showAdminPassword" class="w-5 h-5" />
                      <EyeSlashIcon v-else class="w-5 h-5" />
                    </button>
                  </div>
                  <p v-if="errors.password" class="text-red-500 text-sm mt-1">{{ errors.password[0] }}</p>
                </div>

                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label for="admin-first-name" class="label-base block text-sm mb-2">
                      First Name
                    </label>
                    <input
                      id="admin-first-name"
                      v-model="setupData.admin.first_name"
                      type="text"
                      class="input-base w-full px-4 py-3 rounded-xl"
                      placeholder="First name"
                    />
                  </div>
                  <div>
                    <label for="admin-last-name" class="label-base block text-sm mb-2">
                      Last Name
                    </label>
                    <input
                      id="admin-last-name"
                      v-model="setupData.admin.last_name"
                      type="text"
                      class="input-base w-full px-4 py-3 rounded-xl"
                      placeholder="Last name"
                    />
                  </div>
                </div>

                <transition name="fade">
                  <div
                    v-if="adminStatus.message"
                    class="p-4 rounded-xl"
                    :class="adminStatus.success ? 'bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800' : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'"
                  >
                    <p :class="adminStatus.success ? 'text-emerald-700 dark:text-emerald-300' : 'text-red-700 dark:text-red-300'">
                      {{ adminStatus.message }}
                    </p>
                  </div>
                </transition>

                <div class="flex gap-3 pt-2">
                  <button
                    type="button"
                    @click="prevStep"
                    class="btn-secondary flex-1 py-3 px-4 rounded-xl"
                  >
                    Back
                  </button>
                  <button
                    type="submit"
                    :disabled="adminStatus.loading || adminStatus.success"
                    class="btn-primary flex-1 py-3.5 px-4 rounded-xl disabled:opacity-50 flex items-center justify-center gap-2"
                  >
                    <svg
                      v-if="adminStatus.loading"
                      class="animate-spin h-5 w-5"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>{{ adminStatus.loading ? 'Creating...' : adminStatus.success ? 'Created' : 'Create Admin' }}</span>
                  </button>
                  <button
                    v-if="adminStatus.success"
                    type="button"
                    @click="nextStep"
                    class="btn-primary flex-1 py-3.5 px-4 rounded-xl"
                  >
                    Continue
                    <ArrowRightIcon class="w-5 h-5 inline-block ml-2" />
                  </button>
                </div>
              </form>
            </div>

            <!-- Step 4: Progress -->
            <div
              v-else-if="currentStep === 4"
              key="step-4"
              class="space-y-6"
            >
              <div class="text-center mb-6">
                <div class="inline-flex items-center justify-center w-16 h-16 bg-indigo-100 dark:bg-indigo-900/30 rounded-full mb-4">
                  <Cog6ToothIcon class="w-8 h-8 text-indigo-600 dark:text-indigo-400 animate-spin" />
                </div>
                <h2 class="text-3xl font-bold text-primary mb-2">Finalizing Installation</h2>
                <p class="text-secondary">Setting up your system...</p>
              </div>

              <!-- Progress Steps -->
              <div class="space-y-4 max-w-2xl mx-auto">
                <div
                  v-for="(progressStep, index) in progressSteps"
                  :key="index"
                  class="flex items-center gap-4 p-4 rounded-xl transition-all duration-300"
                  :class="getProgressStepClass(progressStep.status)"
                >
                  <div class="flex-shrink-0">
                    <div
                      v-if="progressStep.status === 'completed'"
                      class="w-10 h-10 rounded-full bg-emerald-500 flex items-center justify-center"
                    >
                      <CheckCircleIcon class="w-6 h-6 text-white" />
                    </div>
                    <div
                      v-else-if="progressStep.status === 'loading'"
                      class="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center"
                    >
                      <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                    </div>
                    <div
                      v-else
                      class="w-10 h-10 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center"
                    >
                      <span class="text-slate-500 dark:text-slate-400 text-sm font-semibold">{{ index + 1 }}</span>
                    </div>
                  </div>
                  <div class="flex-1">
                    <h3 class="font-semibold text-primary">{{ progressStep.label }}</h3>
                    <p class="text-sm text-secondary">{{ progressStep.description }}</p>
                  </div>
                </div>
              </div>

              <!-- Overall Progress Bar -->
              <div class="max-w-2xl mx-auto pt-6">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-sm font-medium text-secondary">Overall Progress</span>
                  <span class="text-sm font-medium text-primary">{{ overallProgress }}%</span>
                </div>
                <div class="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-3 overflow-hidden">
                  <div
                    class="bg-gradient-to-r from-emerald-500 via-blue-500 to-indigo-500 h-3 rounded-full transition-all duration-500 ease-out relative"
                    :style="{ width: `${overallProgress}%` }"
                  >
                    <div class="absolute inset-0 bg-white/30 animate-pulse"></div>
                  </div>
                </div>
              </div>

              <!-- Completion Message -->
              <transition name="fade">
                <div
                  v-if="installationComplete"
                  class="text-center pt-6"
                >
                  <div class="inline-flex items-center justify-center w-20 h-20 bg-emerald-100 dark:bg-emerald-900/30 rounded-full mb-4">
                    <CheckCircleIcon class="w-10 h-10 text-emerald-600 dark:text-emerald-400" />
                  </div>
                  <h3 class="text-2xl font-bold text-primary mb-2">Installation Complete!</h3>
                  <p class="text-secondary mb-6">Your ScreenGram system is ready to use.</p>
                  <router-link
                    to="/login"
                    class="btn-primary inline-flex items-center px-8 py-3.5 rounded-xl text-lg font-semibold"
                  >
                    Go to Login
                    <ArrowRightIcon class="w-5 h-5 ml-2" />
                  </router-link>
                </div>
              </transition>
            </div>
          </transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  RocketLaunchIcon,
  ServerIcon,
  ShieldCheckIcon,
  Cog6ToothIcon,
  CheckCircleIcon,
  XCircleIcon,
  ArrowRightIcon,
  EyeIcon,
  EyeSlashIcon,
} from '@heroicons/vue/24/outline'
import { setupAPI } from '@/services/api'

const router = useRouter()

// Steps configuration
const steps = [
  { label: 'Welcome', icon: RocketLaunchIcon },
  { label: 'Database', icon: ServerIcon },
  { label: 'Admin', icon: ShieldCheckIcon },
  { label: 'System', icon: Cog6ToothIcon },
]

const currentStep = ref(1)
const showDbPassword = ref(false)
const showAdminPassword = ref(false)
const installationComplete = ref(false)

// Setup data
const setupData = reactive({
  db: {
    host: 'localhost',
    port: 5432,
    name: 'screengram_db',
    user: 'screengram_user',
    password: '',
  },
  admin: {
    username: '',
    email: '',
    password: '',
    first_name: '',
    last_name: '',
  },
})

// Status tracking
const dbStatus = reactive({
  loading: false,
  success: false,
  message: '',
})

const adminStatus = reactive({
  loading: false,
  success: false,
  message: '',
})

const errors = ref({})

// Progress steps
const progressSteps = reactive([
  {
    label: 'Running Database Migrations',
    description: 'Applying schema changes to your database...',
    status: 'pending', // pending, loading, completed, error
  },
  {
    label: 'Setting up System Assets',
    description: 'Initializing default configurations...',
    status: 'pending',
  },
  {
    label: 'Finalizing Installation',
    description: 'Creating lock file and completing setup...',
    status: 'pending',
  },
])

// Computed
const overallProgress = computed(() => {
  const completed = progressSteps.filter(s => s.status === 'completed').length
  return Math.round((completed / progressSteps.length) * 100)
})

// Methods
const getStepClass = (index) => {
  if (currentStep.value > index) {
    return 'bg-emerald-500 text-white'
  } else if (currentStep.value === index) {
    return 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 border-2 border-emerald-500'
  } else {
    return 'bg-slate-200 dark:bg-slate-700 text-slate-500 dark:text-slate-400'
  }
}

const getProgressStepClass = (status) => {
  switch (status) {
    case 'completed':
      return 'bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800'
    case 'loading':
      return 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800'
    case 'error':
      return 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'
    default:
      return 'bg-slate-50 dark:bg-slate-800/50'
  }
}

const nextStep = () => {
  if (currentStep.value < steps.length) {
    currentStep.value++
    
    // Auto-start progress on step 4
    if (currentStep.value === 4) {
      startInstallation()
    }
  }
}

const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

const testDatabaseConnection = async () => {
  dbStatus.loading = true
  dbStatus.success = false
  dbStatus.message = ''
  
  try {
    const response = await setupAPI.testDb({
      name: setupData.db.name,
      user: setupData.db.user,
      password: setupData.db.password,
      host: setupData.db.host,
      port: setupData.db.port,
    })
    
    dbStatus.success = true
    dbStatus.message = response.data.message || 'Database connection successful!'
  } catch (error) {
    dbStatus.success = false
    dbStatus.message = error.response?.data?.message || 'Failed to connect to database. Please check your credentials.'
  } finally {
    dbStatus.loading = false
  }
}

const createAdmin = async () => {
  adminStatus.loading = true
  adminStatus.success = false
  adminStatus.message = ''
  errors.value = {}
  
  try {
    await setupAPI.createAdmin({
      username: setupData.admin.username,
      email: setupData.admin.email,
      password: setupData.admin.password,
      first_name: setupData.admin.first_name,
      last_name: setupData.admin.last_name,
    })
    
    adminStatus.success = true
    adminStatus.message = 'Administrator account created successfully!'
  } catch (error) {
    adminStatus.success = false
    if (error.response?.data) {
      adminStatus.message = error.response.data.message || 'Failed to create admin account'
      if (error.response.data.errors) {
        errors.value = error.response.data.errors
      }
    } else {
      adminStatus.message = 'Failed to create admin account'
    }
  } finally {
    adminStatus.loading = false
  }
}

const startInstallation = async () => {
  // Step 1: Run migrations
  progressSteps[0].status = 'loading'
  try {
    await setupAPI.runMigrations()
    progressSteps[0].status = 'completed'
    progressSteps[0].description = 'Database migrations applied successfully'
  } catch (error) {
    progressSteps[0].status = 'error'
    progressSteps[0].description = error.response?.data?.message || 'Migration failed'
    return
  }
  
  // Step 2: Setup assets (simulated)
  progressSteps[1].status = 'loading'
  await new Promise(resolve => setTimeout(resolve, 1500))
  progressSteps[1].status = 'completed'
  progressSteps[1].description = 'System assets configured'
  
  // Step 3: Finalize
  progressSteps[2].status = 'loading'
  try {
    await setupAPI.finalize()
    progressSteps[2].status = 'completed'
    progressSteps[2].description = 'Installation finalized successfully'
    installationComplete.value = true
  } catch (error) {
    progressSteps[2].status = 'error'
    progressSteps[2].description = error.response?.data?.message || 'Finalization failed'
  }
}

onMounted(async () => {
  // Check installation status
  try {
    const response = await setupAPI.status()
    if (response.data.installed) {
      router.push('/login')
    }
  } catch (error) {
    console.error('Failed to check installation status:', error)
  }
})
</script>

<style scoped>
/* Step Transitions */
.step-enter-active,
.step-leave-active {
  transition: all 0.3s ease;
}

.step-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.step-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

/* Fade Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Blob Animation */
.animate-blob {
  animation: blob 7s infinite;
}

.animation-delay-2000 {
  animation-delay: 2s;
}

.animation-delay-4000 {
  animation-delay: 4s;
}

@keyframes blob {
  0% {
    transform: translate(0px, 0px) scale(1);
  }
  33% {
    transform: translate(30px, -50px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.9);
  }
  100% {
    transform: translate(0px, 0px) scale(1);
  }
}

/* Frosted Glass Effect */
.bg-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}

.dark .bg-card {
  background: rgba(30, 41, 59, 0.85);
}
</style>

