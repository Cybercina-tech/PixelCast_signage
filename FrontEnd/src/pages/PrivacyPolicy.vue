<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50">
    <!-- Enhanced Header with Gradient -->
    <header class="bg-white/80 backdrop-blur-md border-b border-slate-200/60 sticky top-0 z-50 shadow-sm">
      <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <router-link
          :to="backRoute"
          class="inline-flex items-center group text-slate-600 hover:text-slate-900 transition-all duration-200"
        >
          <ArrowLeftIcon class="w-5 h-5 mr-2 group-hover:-translate-x-1 transition-transform duration-200" />
          <span class="text-sm font-medium">{{ backText }}</span>
        </router-link>
      </div>
    </header>

    <!-- Main Content with Beautiful Layout -->
    <main class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <!-- Enhanced Page Header -->
      <div class="mb-16 text-center">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-slate-900 to-slate-800 mb-6 shadow-lg">
          <ShieldCheckIcon class="w-8 h-8 text-white" />
        </div>
        <h1 class="text-5xl font-bold text-gray-900 mb-4 bg-gradient-to-r from-slate-900 to-slate-700 bg-clip-text text-transparent">
          Privacy Policy
        </h1>
        <p class="text-lg text-slate-600 flex items-center justify-center gap-2">
          <ClockIcon class="w-5 h-5" />
          Last updated: <span class="font-semibold text-slate-900">{{ lastUpdated }}</span>
        </p>
      </div>

      <!-- Content with Enhanced Styling -->
      <div class="space-y-12">
        <!-- Introduction Card -->
        <section class="bg-white rounded-2xl shadow-lg p-8 border border-slate-100 hover:shadow-xl transition-shadow duration-300">
          <div class="flex items-start gap-4 mb-4">
            <div class="flex-shrink-0 w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
              <InformationCircleIcon class="w-6 h-6 text-blue-600" />
            </div>
            <div class="flex-1">
              <p class="text-gray-700 leading-relaxed mb-4 text-lg">
                PixelCast Signage ("we", "our", or "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our digital signage management platform and services (collectively, the "Service").
              </p>
              <p class="text-gray-700 leading-relaxed text-lg">
                By using our Service, you agree to the collection and use of information in accordance with this policy. If you do not agree with our policies and practices, please do not use our Service.
              </p>
            </div>
          </div>
        </section>

        <!-- Information We Collect -->
        <section class="bg-white rounded-2xl shadow-lg p-8 border border-slate-100">
          <div class="flex items-center gap-3 mb-6">
            <div class="w-1 h-12 bg-gradient-to-b from-blue-500 to-purple-500 rounded-full"></div>
            <h2 class="text-3xl font-bold text-gray-900">1. Information We Collect</h2>
          </div>
          
          <div class="space-y-8">
            <div class="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100">
              <h3 class="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <UserIcon class="w-5 h-5 text-blue-600" />
                1.1 Personal Information
              </h3>
              <p class="text-gray-700 leading-relaxed mb-4">
                When you create an account or use our Service, we may collect:
              </p>
              <ul class="space-y-3 text-gray-700">
                <li class="flex items-start gap-3">
                  <CheckCircleIcon class="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <span><strong class="text-gray-900">Account Information:</strong> Username, email address, full name, phone number, and organization name</span>
                </li>
                <li class="flex items-start gap-3">
                  <CheckCircleIcon class="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <span><strong class="text-gray-900">Authentication Data:</strong> Encrypted passwords and authentication tokens</span>
                </li>
                <li class="flex items-start gap-3">
                  <CheckCircleIcon class="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <span><strong class="text-gray-900">Profile Information:</strong> Role, permissions, and preferences</span>
                </li>
              </ul>
            </div>

            <div class="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-6 border border-purple-100">
              <h3 class="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <ChartBarIcon class="w-5 h-5 text-purple-600" />
                1.2 Usage Data
              </h3>
              <p class="text-gray-700 leading-relaxed mb-4">
                We automatically collect information about how you interact with our Service:
              </p>
              <ul class="space-y-3 text-gray-700">
                <li class="flex items-start gap-3">
                  <CheckCircleIcon class="w-5 h-5 text-purple-600 flex-shrink-0 mt-0.5" />
                  <span><strong class="text-gray-900">Log Data:</strong> IP addresses, browser type, device information, access times, and pages viewed</span>
                </li>
                <li class="flex items-start gap-3">
                  <CheckCircleIcon class="w-5 h-5 text-purple-600 flex-shrink-0 mt-0.5" />
                  <span><strong class="text-gray-900">Command Execution Logs:</strong> Records of commands sent to screens, execution status, and timestamps</span>
                </li>
                <li class="flex items-start gap-3">
                  <CheckCircleIcon class="w-5 h-5 text-purple-600 flex-shrink-0 mt-0.5" />
                  <span><strong class="text-gray-900">Content Download Logs:</strong> Information about content downloads, transfer status, and file metadata</span>
                </li>
                <li class="flex items-start gap-3">
                  <CheckCircleIcon class="w-5 h-5 text-purple-600 flex-shrink-0 mt-0.5" />
                  <span><strong class="text-gray-900">Screen Status Logs:</strong> Online/offline status, connection times, and system metrics</span>
                </li>
                <li class="flex items-start gap-3">
                  <CheckCircleIcon class="w-5 h-5 text-purple-600 flex-shrink-0 mt-0.5" />
                  <span><strong class="text-gray-900">Audit Logs:</strong> Comprehensive records of user actions, system changes, and security events</span>
                </li>
              </ul>
            </div>

            <div class="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 border border-green-100">
              <h3 class="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <FolderIcon class="w-5 h-5 text-green-600" />
                1.3 Content Data
              </h3>
              <p class="text-gray-700 leading-relaxed mb-4">
                When you upload content through our Service:
              </p>
              <ul class="space-y-3 text-gray-700">
                <li class="flex items-start gap-3">
                  <CheckCircleIcon class="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                  <span>Media files (images, videos, documents) and associated metadata</span>
                </li>
                <li class="flex items-start gap-3">
                  <CheckCircleIcon class="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                  <span>Template configurations and design data</span>
                </li>
                <li class="flex items-start gap-3">
                  <CheckCircleIcon class="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                  <span>Schedule information and recurrence patterns</span>
                </li>
              </ul>
            </div>
          </div>
        </section>

        <!-- How We Use Information -->
        <section class="bg-white rounded-2xl shadow-lg p-8 border border-slate-100">
          <div class="flex items-center gap-3 mb-6">
            <div class="w-1 h-12 bg-gradient-to-b from-indigo-500 to-blue-500 rounded-full"></div>
            <h2 class="text-3xl font-bold text-gray-900">2. How We Use Your Information</h2>
          </div>
          <p class="text-gray-700 leading-relaxed mb-6 text-lg">
            We use the collected information for the following purposes:
          </p>
          <div class="grid md:grid-cols-2 gap-4">
            <div v-for="(item, index) in usageItems" :key="index" 
                 class="bg-gradient-to-br from-slate-50 to-white rounded-xl p-5 border border-slate-200 hover:border-indigo-300 hover:shadow-md transition-all duration-200">
              <div class="flex items-start gap-3">
                <div class="flex-shrink-0 w-8 h-8 rounded-lg bg-indigo-100 flex items-center justify-center">
                  <span class="text-indigo-600 font-semibold text-sm">{{ index + 1 }}</span>
                </div>
                <div>
                  <h4 class="font-semibold text-gray-900 mb-1">{{ item.title }}</h4>
                  <p class="text-sm text-gray-600">{{ item.description }}</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Data Storage and Security -->
        <section class="bg-white rounded-2xl shadow-lg p-8 border border-slate-100">
          <div class="flex items-center gap-3 mb-6">
            <div class="w-1 h-12 bg-gradient-to-b from-green-500 to-emerald-500 rounded-full"></div>
            <h2 class="text-3xl font-bold text-gray-900">3. Data Storage and Security</h2>
          </div>
          
          <div class="space-y-6">
            <div class="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 border border-green-100">
              <h3 class="text-xl font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <ServerIcon class="w-5 h-5 text-green-600" />
                3.1 Data Storage
              </h3>
              <p class="text-gray-700 leading-relaxed">
                Your data is stored on secure servers located in data centers with industry-standard physical and technical safeguards. We implement appropriate technical and organizational measures to protect your personal information.
              </p>
            </div>

            <div class="bg-gradient-to-br from-red-50 to-orange-50 rounded-xl p-6 border border-red-100">
              <h3 class="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <LockClosedIcon class="w-5 h-5 text-red-600" />
                3.2 Security Measures
              </h3>
              <p class="text-gray-700 leading-relaxed mb-4">
                We employ multiple layers of security:
              </p>
              <div class="grid md:grid-cols-2 gap-3">
                <div v-for="(measure, index) in securityMeasures" :key="index" 
                     class="flex items-start gap-2 bg-white/60 rounded-lg p-3">
                  <ShieldCheckIcon class="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <strong class="text-gray-900 text-sm">{{ measure.title }}:</strong>
                    <p class="text-sm text-gray-600">{{ measure.description }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Other Sections with Similar Styling -->
        <section class="bg-white rounded-2xl shadow-lg p-8 border border-slate-100">
          <div class="flex items-center gap-3 mb-6">
            <div class="w-1 h-12 bg-gradient-to-b from-yellow-500 to-orange-500 rounded-full"></div>
            <h2 class="text-3xl font-bold text-gray-900">4. Cookies and Tracking Technologies</h2>
          </div>
          <p class="text-gray-700 leading-relaxed mb-4">
            We use cookies and similar tracking technologies to:
          </p>
          <ul class="space-y-3 text-gray-700">
            <li class="flex items-start gap-3">
              <CheckCircleIcon class="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <span><strong class="text-gray-900">Authentication:</strong> Maintain your login session and remember your preferences</span>
            </li>
            <li class="flex items-start gap-3">
              <CheckCircleIcon class="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <span><strong class="text-gray-900">Security:</strong> Detect and prevent fraudulent activity</span>
            </li>
            <li class="flex items-start gap-3">
              <CheckCircleIcon class="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <span><strong class="text-gray-900">Analytics:</strong> Understand how users interact with our Service</span>
            </li>
            <li class="flex items-start gap-3">
              <CheckCircleIcon class="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <span><strong class="text-gray-900">Functionality:</strong> Enable features and improve user experience</span>
            </li>
          </ul>
        </section>

        <!-- Contact Section -->
        <section class="bg-gradient-to-br from-slate-900 to-slate-800 rounded-2xl shadow-2xl p-8 text-white">
          <div class="flex items-center gap-3 mb-6">
            <EnvelopeIcon class="w-8 h-8 text-white" />
            <h2 class="text-3xl font-bold">10. Contact Us</h2>
          </div>
          <p class="text-slate-200 leading-relaxed mb-6 text-lg">
            If you have any questions about this Privacy Policy or wish to exercise your rights, please contact us:
          </p>
          <div class="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
            <div class="space-y-3">
              <p class="flex items-center gap-3">
                <EnvelopeIcon class="w-5 h-5" />
                <strong>Email:</strong> <a href="mailto:privacy@pixelcastsignage.com" class="hover:text-blue-300 transition-colors">privacy@pixelcastsignage.com</a>
              </p>
              <p class="flex items-center gap-3">
                <EnvelopeIcon class="w-5 h-5" />
                <strong>Support:</strong> <a href="mailto:support@pixelcastsignage.com" class="hover:text-blue-300 transition-colors">support@pixelcastsignage.com</a>
              </p>
            </div>
          </div>
        </section>
      </div>
    </main>

    <!-- Enhanced Footer -->
    <footer class="bg-white border-t border-slate-200 mt-20">
      <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="flex flex-col sm:flex-row justify-between items-center gap-4 text-sm text-gray-600">
          <p>© {{ currentYear }} PixelCast Signage. All rights reserved.</p>
          <div class="flex items-center gap-4">
            <router-link to="/privacy" class="hover:text-slate-900 transition-colors font-medium">Privacy Policy</router-link>
            <span class="text-slate-300">•</span>
            <router-link to="/terms" class="hover:text-slate-900 transition-colors font-medium">Terms of Service</router-link>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  ArrowLeftIcon,
  ShieldCheckIcon,
  ClockIcon,
  InformationCircleIcon,
  UserIcon,
  ChartBarIcon,
  FolderIcon,
  CheckCircleIcon,
  ServerIcon,
  LockClosedIcon,
  EnvelopeIcon,
} from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()

const lastUpdated = ref('December 22, 2024')
const currentYear = ref(new Date().getFullYear())

// Smart back route - dashboard if authenticated, landing if not
const backRoute = computed(() => {
  return authStore.isAuthenticated ? '/dashboard' : '/'
})

const backText = computed(() => {
  return authStore.isAuthenticated ? 'Back to Dashboard' : 'Back to Home'
})

const usageItems = ref([
  { title: 'Service Delivery', description: 'Provide, maintain, and improve our Service' },
  { title: 'Authentication', description: 'Verify identity and manage access' },
  { title: 'Communication', description: 'Send notifications and updates' },
  { title: 'Security', description: 'Detect and prevent security threats' },
  { title: 'Analytics', description: 'Analyze usage patterns' },
  { title: 'Compliance', description: 'Comply with legal obligations' },
  { title: 'Support', description: 'Provide customer support' },
])

const securityMeasures = ref([
  { title: 'Encryption', description: 'TLS/SSL for data in transit, industry-standard encryption at rest' },
  { title: 'Access Controls', description: 'Role-based access control (RBAC)' },
  { title: 'Authentication', description: 'Multi-factor authentication (MFA) support' },
  { title: 'Monitoring', description: 'Continuous security monitoring' },
  { title: 'Audit Logging', description: 'Comprehensive audit logs' },
  { title: 'Backup', description: 'Regular automated encrypted backups' },
])

onMounted(() => {
  document.title = 'Privacy Policy - PixelCast Signage'
  
  const metaDescription = document.querySelector('meta[name="description"]')
  if (metaDescription) {
    metaDescription.setAttribute('content', 'PixelCast Signage Privacy Policy - Learn how we collect, use, and protect your personal information when using our digital signage management platform.')
  } else {
    const meta = document.createElement('meta')
    meta.name = 'description'
    meta.content = 'PixelCast Signage Privacy Policy - Learn how we collect, use, and protect your personal information when using our digital signage management platform.'
    document.head.appendChild(meta)
  }
})
</script>

<style scoped>
/* Smooth scrolling */
html {
  scroll-behavior: smooth;
}
</style>
