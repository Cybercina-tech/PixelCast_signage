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
          <DocumentTextIcon class="w-8 h-8 text-white" />
        </div>
        <h1 class="text-5xl font-bold text-gray-900 mb-4 bg-gradient-to-r from-slate-900 to-slate-700 bg-clip-text text-transparent">
          Terms of Service
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
            <div class="flex-shrink-0 w-10 h-10 rounded-lg bg-indigo-100 flex items-center justify-center">
              <InformationCircleIcon class="w-6 h-6 text-indigo-600" />
            </div>
            <div class="flex-1">
              <p class="text-gray-700 leading-relaxed mb-4 text-lg">
                These Terms of Service ("Terms") govern your access to and use of ScreenGram's digital signage management platform and related services (collectively, the "Service"). By accessing or using our Service, you agree to be bound by these Terms.
              </p>
              <p class="text-gray-700 leading-relaxed text-lg">
                If you do not agree to these Terms, you may not access or use the Service. These Terms constitute a legally binding agreement between you and ScreenGram.
              </p>
            </div>
          </div>
        </section>

        <!-- Service Description -->
        <section class="bg-white rounded-2xl shadow-lg p-8 border border-slate-100">
          <div class="flex items-center gap-3 mb-6">
            <div class="w-1 h-12 bg-gradient-to-b from-blue-500 to-indigo-500 rounded-full"></div>
            <h2 class="text-3xl font-bold text-gray-900">1. Service Description</h2>
          </div>
          <p class="text-gray-700 leading-relaxed mb-6 text-lg">
            ScreenGram provides a cloud-based digital signage management platform that enables users to:
          </p>
          <div class="grid md:grid-cols-2 gap-4">
            <div v-for="(feature, index) in serviceFeatures" :key="index" 
                 class="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-5 border border-blue-100 hover:border-blue-300 hover:shadow-md transition-all duration-200">
              <div class="flex items-start gap-3">
                <CheckCircleIcon class="w-6 h-6 text-blue-600 flex-shrink-0 mt-0.5" />
                <span class="text-gray-700 font-medium">{{ feature }}</span>
              </div>
            </div>
          </div>
        </section>

        <!-- Account Registration -->
        <section class="bg-white rounded-2xl shadow-lg p-8 border border-slate-100">
          <div class="flex items-center gap-3 mb-6">
            <div class="w-1 h-12 bg-gradient-to-b from-green-500 to-emerald-500 rounded-full"></div>
            <h2 class="text-3xl font-bold text-gray-900">2. Account Registration and Security</h2>
          </div>
          
          <div class="space-y-6">
            <div class="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 border border-green-100">
              <h3 class="text-xl font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <UserPlusIcon class="w-5 h-5 text-green-600" />
                2.1 Account Creation
              </h3>
              <p class="text-gray-700 leading-relaxed">
                To use the Service, you must create an account by providing accurate, current, and complete information. You are responsible for maintaining the confidentiality of your account credentials and for all activities that occur under your account.
              </p>
            </div>

            <div class="bg-gradient-to-br from-red-50 to-orange-50 rounded-xl p-6 border border-red-100">
              <h3 class="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <LockClosedIcon class="w-5 h-5 text-red-600" />
                2.2 Account Security
              </h3>
              <p class="text-gray-700 leading-relaxed mb-4">
                You agree to:
              </p>
              <ul class="space-y-2 text-gray-700">
                <li v-for="(item, index) in securityRequirements" :key="index" class="flex items-start gap-3">
                  <CheckCircleIcon class="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                  <span>{{ item }}</span>
                </li>
              </ul>
            </div>
          </div>
        </section>

        <!-- User Responsibilities -->
        <section class="bg-white rounded-2xl shadow-lg p-8 border border-slate-100">
          <div class="flex items-center gap-3 mb-6">
            <div class="w-1 h-12 bg-gradient-to-b from-purple-500 to-pink-500 rounded-full"></div>
            <h2 class="text-3xl font-bold text-gray-900">3. User Responsibilities</h2>
          </div>
          <p class="text-gray-700 leading-relaxed mb-6 text-lg">
            You are responsible for:
          </p>
          <div class="grid md:grid-cols-2 gap-4">
            <div v-for="(responsibility, index) in userResponsibilities" :key="index" 
                 class="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-5 border border-purple-100 hover:border-purple-300 hover:shadow-md transition-all duration-200">
              <div class="flex items-start gap-3">
                <div class="flex-shrink-0 w-8 h-8 rounded-lg bg-purple-100 flex items-center justify-center">
                  <span class="text-purple-600 font-semibold text-sm">{{ index + 1 }}</span>
                </div>
                <div>
                  <h4 class="font-semibold text-gray-900 mb-1">{{ responsibility.title }}</h4>
                  <p class="text-sm text-gray-600">{{ responsibility.description }}</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Prohibited Usage -->
        <section class="bg-white rounded-2xl shadow-lg p-8 border border-slate-100">
          <div class="flex items-center gap-3 mb-6">
            <div class="w-1 h-12 bg-gradient-to-b from-red-500 to-orange-500 rounded-full"></div>
            <h2 class="text-3xl font-bold text-gray-900">4. Prohibited Usage</h2>
          </div>
          <p class="text-gray-700 leading-relaxed mb-6 text-lg">
            You agree not to use the Service to:
          </p>
          <div class="bg-gradient-to-br from-red-50 to-orange-50 rounded-xl p-6 border border-red-100">
            <div class="grid md:grid-cols-2 gap-4">
              <div v-for="(prohibition, index) in prohibitedUsage" :key="index" 
                   class="flex items-start gap-3 bg-white/60 rounded-lg p-3">
                <XCircleIcon class="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                <div>
                  <strong class="text-gray-900 text-sm">{{ prohibition.title }}:</strong>
                  <p class="text-sm text-gray-600">{{ prohibition.description }}</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Limitation of Liability -->
        <section class="bg-white rounded-2xl shadow-lg p-8 border border-slate-100">
          <div class="flex items-center gap-3 mb-6">
            <div class="w-1 h-12 bg-gradient-to-b from-yellow-500 to-orange-500 rounded-full"></div>
            <h2 class="text-3xl font-bold text-gray-900">7. Limitation of Liability</h2>
          </div>
          <div class="space-y-6">
            <div class="bg-gradient-to-br from-yellow-50 to-orange-50 rounded-xl p-6 border border-yellow-100">
              <h3 class="text-xl font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <ExclamationTriangleIcon class="w-5 h-5 text-yellow-600" />
                7.1 Service Availability
              </h3>
              <p class="text-gray-700 leading-relaxed">
                We strive to provide reliable service but do not guarantee that the Service will be uninterrupted, error-free, or completely secure. The Service is provided "as is" and "as available" without warranties of any kind.
              </p>
            </div>
          </div>
        </section>

        <!-- Contact Section -->
        <section class="bg-gradient-to-br from-slate-900 to-slate-800 rounded-2xl shadow-2xl p-8 text-white">
          <div class="flex items-center gap-3 mb-6">
            <EnvelopeIcon class="w-8 h-8 text-white" />
            <h2 class="text-3xl font-bold">12. Contact Us</h2>
          </div>
          <p class="text-slate-200 leading-relaxed mb-6 text-lg">
            If you have any questions about these Terms, please contact us:
          </p>
          <div class="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
            <div class="space-y-3">
              <p class="flex items-center gap-3">
                <EnvelopeIcon class="w-5 h-5" />
                <strong>Email:</strong> <a href="mailto:legal@screengram.com" class="hover:text-blue-300 transition-colors">legal@screengram.com</a>
              </p>
              <p class="flex items-center gap-3">
                <EnvelopeIcon class="w-5 h-5" />
                <strong>Support:</strong> <a href="mailto:support@screengram.com" class="hover:text-blue-300 transition-colors">support@screengram.com</a>
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
          <p>© {{ currentYear }} ScreenGram. All rights reserved.</p>
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
  DocumentTextIcon,
  ClockIcon,
  InformationCircleIcon,
  CheckCircleIcon,
  UserPlusIcon,
  LockClosedIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
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

const serviceFeatures = ref([
  'Manage and control digital displays remotely',
  'Upload, organize, and schedule content for display',
  'Create and manage templates for digital signage',
  'Execute commands on connected screens',
  'Monitor screen status and system health',
  'Manage users, roles, and permissions',
  'Access analytics and reporting features',
])

const securityRequirements = ref([
  'Use a strong, unique password',
  'Enable multi-factor authentication when available',
  'Notify us immediately of any unauthorized access',
  'Not share your account credentials with others',
  'Maintain the security of your account',
])

const userResponsibilities = ref([
  { title: 'Content', description: 'All content you upload, including ensuring you have the right to use and display such content' },
  { title: 'Compliance', description: 'Complying with all applicable laws, regulations, and third-party rights' },
  { title: 'Screen Management', description: 'Properly configuring and maintaining your connected screens' },
  { title: 'User Management', description: 'Managing users within your organization and ensuring they comply with these Terms' },
  { title: 'Data Backup', description: 'Maintaining backups of your content and configurations' },
  { title: 'Security', description: 'Implementing appropriate security measures for your organization' },
])

const prohibitedUsage = ref([
  { title: 'Illegal Activities', description: 'Violate any applicable laws, regulations, or third-party rights' },
  { title: 'Harmful Content', description: 'Upload, display, or distribute illegal, harmful, or defamatory content' },
  { title: 'Malware', description: 'Upload or distribute viruses, malware, or other harmful code' },
  { title: 'Unauthorized Access', description: 'Attempt to gain unauthorized access to our systems or other users\' accounts' },
  { title: 'Service Disruption', description: 'Interfere with or disrupt the Service, servers, or networks' },
  { title: 'Reverse Engineering', description: 'Reverse engineer, decompile, or disassemble any part of the Service' },
  { title: 'Resale', description: 'Resell, sublicense, or redistribute the Service without permission' },
  { title: 'Automated Access', description: 'Use automated systems to access the Service without authorization' },
])

onMounted(() => {
  document.title = 'Terms of Service - ScreenGram'
  
  const metaDescription = document.querySelector('meta[name="description"]')
  if (metaDescription) {
    metaDescription.setAttribute('content', 'ScreenGram Terms of Service - Read our terms and conditions for using our digital signage management platform.')
  } else {
    const meta = document.createElement('meta')
    meta.name = 'description'
    meta.content = 'ScreenGram Terms of Service - Read our terms and conditions for using our digital signage management platform.'
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
