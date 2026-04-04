<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 flex items-center justify-center px-4 py-12 relative overflow-hidden">
    <!-- Animated Background Elements -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-40 -right-40 w-80 h-80 bg-blue-200 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob"></div>
      <div class="absolute -bottom-40 -left-40 w-80 h-80 bg-indigo-200 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-2000"></div>
      <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-purple-200 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-4000"></div>
    </div>

    <div v-if="statusChecking" class="w-full max-w-md relative z-10 text-center">
      <div class="bg-card backdrop-blur-lg rounded-2xl shadow-2xl border border-border-color px-8 py-12">
        <p class="text-secondary">Checking installation status…</p>
      </div>
    </div>

    <div v-else-if="alreadyInstalled" class="w-full max-w-lg relative z-10">
      <div
        v-motion
        :initial="{ opacity: 0, y: 20 }"
        :enter="{ opacity: 1, y: 0 }"
        :transition="{ duration: 500 }"
        class="bg-card backdrop-blur-lg rounded-2xl shadow-2xl border border-border-color overflow-hidden text-center px-8 py-12"
      >
        <div class="inline-flex items-center justify-center w-16 h-16 bg-emerald-500/15 rounded-full mb-6 border border-emerald-500/30">
          <svg class="w-9 h-9 text-emerald-600 dark:text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h1 class="text-2xl sm:text-3xl font-bold text-primary mb-3">PixelCast is already installed</h1>
        <p class="text-secondary text-sm sm:text-base mb-8 max-w-md mx-auto">
          Setup on this server is complete. The installation wizard is not available. Sign in or create an account to use the dashboard.
        </p>
        <div class="flex flex-col sm:flex-row gap-3 justify-center">
          <router-link
            to="/login"
            class="btn-primary inline-flex items-center justify-center py-3 px-6 rounded-xl font-semibold"
          >
            Log in
          </router-link>
          <router-link
            to="/signup"
            class="btn-secondary inline-flex items-center justify-center py-3 px-6 rounded-xl font-semibold border border-border-color"
          >
            Create account
          </router-link>
          <router-link
            to="/"
            class="inline-flex items-center justify-center py-3 px-6 rounded-xl text-sm font-medium text-secondary hover:text-primary"
          >
            Home
          </router-link>
        </div>
      </div>
    </div>

    <div v-else class="w-full max-w-3xl relative z-10">
      <!-- Installation Card -->
      <div 
        v-motion
        :initial="{ opacity: 0, y: 20 }"
        :enter="{ opacity: 1, y: 0 }"
        :transition="{ duration: 500 }"
        class="bg-card backdrop-blur-lg rounded-2xl shadow-2xl border border-border-color overflow-hidden"
      >
        <!-- Header -->
        <div class="bg-gradient-to-r from-slate-900 via-emerald-700 to-emerald-600 dark:from-emerald-600 dark:via-emerald-500 dark:to-emerald-400 px-8 py-10 text-center relative overflow-hidden">
          <div class="absolute inset-0 opacity-10">
            <div class="absolute inset-0" style="background-image: radial-gradient(circle at 2px 2px, white 1px, transparent 0); background-size: 40px 40px;"></div>
          </div>
          
          <div class="relative z-10">
            <div class="inline-flex items-center justify-center w-16 h-16 bg-white/10 rounded-full mb-4 backdrop-blur-sm border border-white/20">
              <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h1 class="text-3xl font-bold text-white mb-2 tracking-tight">PixelCast Signage Installation</h1>
            <p class="text-emerald-100 dark:text-emerald-900 text-sm font-medium">Complete the setup to get started</p>
          </div>
        </div>

        <!-- Progress Bar -->
        <div class="px-8 pt-6 pb-4">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm font-medium text-secondary">Step {{ currentStep }} of {{ totalSteps }}</span>
            <span class="text-sm font-medium text-secondary">{{ Math.round((currentStep / totalSteps) * 100) }}%</span>
          </div>
          <div class="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2 overflow-hidden">
            <div 
              class="bg-gradient-to-r from-emerald-500 to-emerald-600 h-2 rounded-full transition-all duration-500 ease-out"
              :style="{ width: `${(currentStep / totalSteps) * 100}%` }"
            ></div>
          </div>
        </div>

        <!-- Step Content -->
        <div class="px-8 py-8">
          <!-- Step 1: Welcome -->
          <div v-if="currentStep === 1" 
            v-motion
            :initial="{ opacity: 0, x: 20 }"
            :enter="{ opacity: 1, x: 0 }"
            class="space-y-6"
          >
            <div>
              <h2 class="text-2xl font-bold text-primary mb-2">Welcome to PixelCast Signage</h2>
              <p class="text-secondary mb-4">
                This installation wizard will guide you through setting up your PixelCast Signage digital signage system.
                The process includes:
              </p>
              <ul class="space-y-2 text-secondary mb-6">
                <li class="flex items-start gap-2">
                  <svg class="w-5 h-5 text-emerald-600 dark:text-emerald-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Testing database connection</span>
                </li>
                <li class="flex items-start gap-2">
                  <svg class="w-5 h-5 text-emerald-600 dark:text-emerald-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Running database migrations</span>
                </li>
                <li class="flex items-start gap-2">
                  <svg class="w-5 h-5 text-emerald-600 dark:text-emerald-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Creating your administrator account</span>
                </li>
                <li class="flex items-start gap-2">
                  <svg class="w-5 h-5 text-emerald-600 dark:text-emerald-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Finalizing setup</span>
                </li>
              </ul>
            </div>
            <button
              @click="nextStep"
              class="btn-primary w-full py-3.5 px-4 rounded-xl"
            >
              Get Started
              <svg class="w-5 h-5 inline-block ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </button>
          </div>

          <!-- Step 2: Database Connection -->
          <div v-if="currentStep === 2"
            v-motion
            :initial="{ opacity: 0, x: 20 }"
            :enter="{ opacity: 1, x: 0 }"
            class="space-y-6"
          >
            <div>
              <h2 class="text-2xl font-bold text-primary mb-2">Database Connection</h2>
              <p class="text-secondary mb-4">
                Testing connection to your database. Please ensure your database is running and accessible.
              </p>
            </div>

            <div v-if="stepsStatus.db === 'loading'" class="flex items-center justify-center py-8">
              <svg class="animate-spin h-8 w-8 text-emerald-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span class="ml-3 text-secondary">Testing connection...</span>
            </div>

            <div v-else-if="stepsStatus.db === 'success'" class="bg-emerald-50 dark:bg-emerald-900/20 border-l-4 border-emerald-500 rounded-lg px-4 py-3">
              <div class="flex items-start gap-2">
                <svg class="w-5 h-5 text-emerald-600 dark:text-emerald-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <div class="flex-1">
                  <p class="text-emerald-700 dark:text-emerald-300 font-medium">Database connection successful!</p>
                  <p v-if="dbDetails.vendor" class="text-sm text-emerald-600 dark:text-emerald-400 mt-1">
                    Connected to {{ dbDetails.vendor }} database: {{ dbDetails.database }}
                  </p>
                </div>
              </div>
            </div>

            <div v-else-if="stepsStatus.db === 'error'" class="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 rounded-lg px-4 py-3">
              <div class="flex items-start gap-2">
                <svg class="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div class="flex-1">
                  <p class="text-red-700 dark:text-red-300 font-medium">Database connection failed</p>
                  <p class="text-sm text-red-600 dark:text-red-400 mt-1">{{ dbError }}</p>
                </div>
              </div>
            </div>

            <div class="flex gap-3">
              <button
                v-if="stepsStatus.db !== 'success'"
                @click="testDatabase"
                :disabled="stepsStatus.db === 'loading'"
                class="btn-secondary flex-1 py-3 px-4 rounded-xl disabled:opacity-50"
              >
                Test Again
              </button>
              <button
                v-if="stepsStatus.db === 'success'"
                @click="nextStep"
                class="btn-primary flex-1 py-3.5 px-4 rounded-xl"
              >
                Continue
                <svg class="w-5 h-5 inline-block ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Step 3: Run Migrations -->
          <div v-if="currentStep === 3"
            v-motion
            :initial="{ opacity: 0, x: 20 }"
            :enter="{ opacity: 1, x: 0 }"
            class="space-y-6"
          >
            <div>
              <h2 class="text-2xl font-bold text-primary mb-2">Database Migrations</h2>
              <p class="text-secondary mb-4">
                Applying database schema migrations. This may take a few moments.
              </p>
            </div>

            <div v-if="stepsStatus.migrations === 'loading'" class="flex items-center justify-center py-8">
              <svg class="animate-spin h-8 w-8 text-emerald-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span class="ml-3 text-secondary">Running migrations...</span>
            </div>

            <div v-else-if="stepsStatus.migrations === 'success'" class="bg-emerald-50 dark:bg-emerald-900/20 border-l-4 border-emerald-500 rounded-lg px-4 py-3">
              <div class="flex items-start gap-2">
                <svg class="w-5 h-5 text-emerald-600 dark:text-emerald-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <div class="flex-1">
                  <p class="text-emerald-700 dark:text-emerald-300 font-medium">Migrations applied successfully!</p>
                  <p v-if="migrationDetails.length > 0" class="text-sm text-emerald-600 dark:text-emerald-400 mt-2">
                    Applied {{ migrationDetails.length }} migration(s)
                  </p>
                </div>
              </div>
            </div>

            <div v-else-if="stepsStatus.migrations === 'error'" class="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 rounded-lg px-4 py-3">
              <div class="flex items-start gap-2">
                <svg class="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div class="flex-1">
                  <p class="text-red-700 dark:text-red-300 font-medium">Migration failed</p>
                  <p class="text-sm text-red-600 dark:text-red-400 mt-1">{{ migrationError }}</p>
                </div>
              </div>
            </div>

            <div class="flex gap-3">
              <button
                v-if="stepsStatus.migrations !== 'success'"
                @click="runMigrations"
                :disabled="stepsStatus.migrations === 'loading'"
                class="btn-secondary flex-1 py-3 px-4 rounded-xl disabled:opacity-50"
              >
                Run Migrations
              </button>
              <button
                v-if="stepsStatus.migrations === 'success'"
                @click="nextStep"
                class="btn-primary flex-1 py-3.5 px-4 rounded-xl"
              >
                Continue
                <svg class="w-5 h-5 inline-block ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Step 4: Create Superuser -->
          <div v-if="currentStep === 4"
            v-motion
            :initial="{ opacity: 0, x: 20 }"
            :enter="{ opacity: 1, x: 0 }"
            class="space-y-6"
          >
            <div>
              <h2 class="text-2xl font-bold text-primary mb-2">Create Administrator Account</h2>
              <p class="text-secondary mb-4">
                Create your administrator account to access the PixelCast Signage dashboard.
              </p>
            </div>

            <form @submit.prevent="createSuperuser" class="space-y-5">
              <div>
                <label for="username" class="label-base block text-sm mb-2">
                  Username <span class="text-red-500">*</span>
                </label>
                <input
                  id="username"
                  v-model="superuserForm.username"
                  type="text"
                  required
                  class="input-base w-full px-4 py-3 rounded-xl"
                  placeholder="Enter username"
                />
                <p v-if="errors.username" class="text-red-500 text-sm mt-1">{{ errors.username[0] }}</p>
              </div>

              <div>
                <label for="email" class="label-base block text-sm mb-2">
                  Email
                </label>
                <input
                  id="email"
                  v-model="superuserForm.email"
                  type="email"
                  class="input-base w-full px-4 py-3 rounded-xl"
                  placeholder="Enter email (optional)"
                />
                <p v-if="errors.email" class="text-red-500 text-sm mt-1">{{ errors.email[0] }}</p>
              </div>

              <div>
                <label for="password" class="label-base block text-sm mb-2">
                  Password <span class="text-red-500">*</span>
                </label>
                <div class="relative">
                  <input
                    id="password"
                    v-model="superuserForm.password"
                    :type="showPassword ? 'text' : 'password'"
                    required
                    minlength="8"
                    class="input-base w-full px-4 py-3 rounded-xl pr-12"
                    placeholder="Enter password (min 8 characters)"
                  />
                  <button
                    type="button"
                    @click="showPassword = !showPassword"
                    class="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-emerald-600 dark:hover:text-emerald-400"
                  >
                    <svg v-if="!showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                    </svg>
                  </button>
                </div>
                <p v-if="errors.password" class="text-red-500 text-sm mt-1">{{ errors.password[0] }}</p>
              </div>

              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label for="first_name" class="label-base block text-sm mb-2">
                    First Name
                  </label>
                  <input
                    id="first_name"
                    v-model="superuserForm.first_name"
                    type="text"
                    class="input-base w-full px-4 py-3 rounded-xl"
                    placeholder="First name"
                  />
                </div>
                <div>
                  <label for="last_name" class="label-base block text-sm mb-2">
                    Last Name
                  </label>
                  <input
                    id="last_name"
                    v-model="superuserForm.last_name"
                    type="text"
                    class="input-base w-full px-4 py-3 rounded-xl"
                    placeholder="Last name"
                  />
                </div>
              </div>

              <div v-if="superuserError" class="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 rounded-lg px-4 py-3">
                <p class="text-red-700 dark:text-red-300 text-sm">{{ superuserError }}</p>
              </div>

              <div v-if="stepsStatus.superuser === 'success'" class="bg-emerald-50 dark:bg-emerald-900/20 border-l-4 border-emerald-500 rounded-lg px-4 py-3">
                <p class="text-emerald-700 dark:text-emerald-300 font-medium">Administrator account created successfully!</p>
              </div>

              <button
                type="submit"
                :disabled="stepsStatus.superuser === 'loading' || stepsStatus.superuser === 'success'"
                class="btn-primary w-full py-3.5 px-4 rounded-xl disabled:opacity-50"
              >
                <span v-if="stepsStatus.superuser === 'loading'">
                  <svg class="animate-spin h-5 w-5 inline-block mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Creating...
                </span>
                <span v-else-if="stepsStatus.superuser === 'success'">
                  Account Created
                </span>
                <span v-else>
                  Create Administrator Account
                </span>
              </button>

              <button
                v-if="stepsStatus.superuser === 'success'"
                @click="nextStep"
                class="btn-primary w-full py-3.5 px-4 rounded-xl"
              >
                Continue
                <svg class="w-5 h-5 inline-block ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </button>
            </form>
          </div>

          <!-- Step 5: Complete Setup -->
          <div v-if="currentStep === 5"
            v-motion
            :initial="{ opacity: 0, x: 20 }"
            :enter="{ opacity: 1, x: 0 }"
            class="space-y-6"
          >
            <div>
              <h2 class="text-2xl font-bold text-primary mb-2">Complete Setup</h2>
              <p class="text-secondary mb-4">
                Finalizing the installation and marking setup as complete.
              </p>
            </div>

            <div v-if="stepsStatus.complete === 'loading'" class="flex items-center justify-center py-8">
              <svg class="animate-spin h-8 w-8 text-emerald-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span class="ml-3 text-secondary">Completing setup...</span>
            </div>

            <div v-else-if="stepsStatus.complete === 'success'" class="text-center py-8">
              <div class="inline-flex items-center justify-center w-20 h-20 bg-emerald-100 dark:bg-emerald-900/30 rounded-full mb-6">
                <svg class="w-10 h-10 text-emerald-600 dark:text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h3 class="text-2xl font-bold text-primary mb-2">Setup Complete!</h3>
              <p class="text-secondary mb-6">
                Your PixelCast Signage installation is complete. You can now access the dashboard.
              </p>
              <router-link
                to="/login"
                class="btn-primary inline-flex items-center py-3.5 px-6 rounded-xl"
              >
                Go to Login
                <svg class="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </router-link>
            </div>

            <div v-else-if="stepsStatus.complete === 'error'" class="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 rounded-lg px-4 py-3">
              <div class="flex items-start gap-2">
                <svg class="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div class="flex-1">
                  <p class="text-red-700 dark:text-red-300 font-medium">Setup completion failed</p>
                  <p class="text-sm text-red-600 dark:text-red-400 mt-1">{{ completeError }}</p>
                </div>
              </div>
            </div>

            <button
              v-if="stepsStatus.complete !== 'success' && stepsStatus.complete !== 'loading'"
              @click="completeSetup"
              class="btn-primary w-full py-3.5 px-4 rounded-xl"
            >
              Complete Setup
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { setupAPI } from '@/services/api'

const statusChecking = ref(true)
const alreadyInstalled = ref(false)

const currentStep = ref(1)
const totalSteps = 5
const showPassword = ref(false)

const stepsStatus = ref({
  db: 'pending',
  migrations: 'pending',
  superuser: 'pending',
  complete: 'pending'
})

const dbDetails = ref({})
const dbError = ref('')
const migrationDetails = ref([])
const migrationError = ref('')
const superuserError = ref('')
const completeError = ref('')
const errors = ref({})

const superuserForm = ref({
  username: '',
  email: '',
  password: '',
  first_name: '',
  last_name: ''
})

const nextStep = () => {
  if (currentStep.value < totalSteps) {
    currentStep.value++
    
    // Auto-run steps when navigating forward
    if (currentStep.value === 2) {
      testDatabase()
    } else if (currentStep.value === 3) {
      runMigrations()
    } else if (currentStep.value === 5) {
      completeSetup()
    }
  }
}

const testDatabase = async () => {
  stepsStatus.value.db = 'loading'
  dbError.value = ''
  
  try {
    const response = await setupAPI.testDb()
    stepsStatus.value.db = 'success'
    dbDetails.value = response.data.details || {}
  } catch (error) {
    stepsStatus.value.db = 'error'
    dbError.value = error.response?.data?.message || 'Failed to connect to database'
  }
}

const runMigrations = async () => {
  stepsStatus.value.migrations = 'loading'
  migrationError.value = ''
  
  try {
    const response = await setupAPI.runMigrations()
    stepsStatus.value.migrations = 'success'
    migrationDetails.value = response.data.applied_migrations || []
  } catch (error) {
    stepsStatus.value.migrations = 'error'
    migrationError.value = error.response?.data?.message || 'Failed to run migrations'
  }
}

const createSuperuser = async () => {
  stepsStatus.value.superuser = 'loading'
  superuserError.value = ''
  errors.value = {}
  
  try {
    await setupAPI.createAdmin(superuserForm.value)
    stepsStatus.value.superuser = 'success'
  } catch (error) {
    stepsStatus.value.superuser = 'error'
    if (error.response?.data) {
      if (error.response.data.message) {
        superuserError.value = error.response.data.message
      }
      if (error.response.data.errors || error.response.data) {
        errors.value = error.response.data.errors || error.response.data
      }
    } else {
      superuserError.value = 'Failed to create administrator account'
    }
  }
}

const completeSetup = async () => {
  stepsStatus.value.complete = 'loading'
  completeError.value = ''
  
  try {
    await setupAPI.finalize()
    stepsStatus.value.complete = 'success'
  } catch (error) {
    stepsStatus.value.complete = 'error'
    completeError.value = error.response?.data?.message || 'Failed to complete setup'
  }
}

onMounted(async () => {
  try {
    const response = await setupAPI.status()
    const status = response.data

    if (status.installed) {
      alreadyInstalled.value = true
      return
    }

    // Auto-advance to first incomplete step (API uses admin_exists)
    if (status.database_connected && status.migrations_applied && status.admin_exists) {
      currentStep.value = 5
    } else if (status.database_connected && status.migrations_applied) {
      currentStep.value = 4
    } else if (status.database_connected) {
      currentStep.value = 3
      stepsStatus.value.db = 'success'
    } else {
      currentStep.value = 2
    }
  } catch (error) {
    console.error('Failed to check setup status:', error)
  } finally {
    statusChecking.value = false
  }
})
</script>

<style scoped>
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
</style>

