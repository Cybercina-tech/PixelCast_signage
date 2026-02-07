<template>
  <div class="wizard-page cosmic-wizard min-h-screen w-full flex items-center justify-center px-4 py-4 relative">
    <!-- Deep space gradient -->
    <div class="cosmic-bg" aria-hidden="true" />
    <!-- Animated starfield -->
    <div class="cosmic-starfield" aria-hidden="true" />
    <!-- Nebula accents (reduced opacity so they don't create a cut-off shadow at card bottom) -->
    <div class="nebula nebula--indigo" aria-hidden="true" />
    <div class="nebula nebula--purple" aria-hidden="true" />

    <!-- Return to Base: cosmic exit button (top-left, above starfield) -->
    <div class="exit-btn-wrapper fixed top-6 left-6 z-50 group">
      <router-link
        to="/"
        class="exit-btn cosmic-exit inline-flex items-center gap-2 px-3 py-2 sm:px-4 sm:py-2.5 rounded-xl bg-white/5 border border-white/10 backdrop-blur-md text-slate-300 hover:bg-white/10 hover:border-indigo-500/60 hover:text-indigo-200 transition-all duration-300 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:ring-offset-2 focus:ring-offset-[#0B0E14]"
        title="All installation progress will be lost."
        aria-label="Back to landing page. All installation progress will be lost."
      >
        <ArrowLeftIcon class="w-5 h-5 flex-shrink-0 cosmic-icon" aria-hidden="true" />
        <span class="hidden sm:inline text-sm font-medium tracking-wide">Back to Base</span>
      </router-link>
      <div
        class="exit-tooltip absolute left-0 top-full mt-2 px-3 py-2 rounded-lg bg-slate-900/95 border border-white/10 backdrop-blur-sm text-xs text-slate-300 whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity duration-200 shadow-xl z-50"
        role="tooltip"
      >
        All installation progress will be lost.
      </div>
    </div>

    <div class="w-full max-w-2xl relative z-10 flex flex-col max-h-[90vh] min-h-0">
      <!-- Command Center glass card: max 90vh, scroll inside card only; scrollbar-gutter prevents horizontal shift -->
      <div
        v-motion
        :initial="{ opacity: 0, y: 20 }"
        :enter="{ opacity: 1, y: 0 }"
        :transition="{ duration: 500 }"
        class="command-center command-center-scroll rounded-3xl overflow-hidden flex flex-col max-h-[90vh] min-h-0 w-full"
      >
        <!-- Header: compact -->
        <div class="px-4 sm:px-5 py-2 sm:py-3 text-center border-b border-white/10 relative flex-shrink-0">
          <div class="cosmic-icon-wrap inline-flex items-center justify-center w-9 h-9 sm:w-10 sm:h-10 rounded-lg bg-white/5 border border-white/10 mb-1">
            <svg class="w-5 h-5 sm:w-6 sm:h-6 text-indigo-400 cosmic-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <h1 class="cosmic-title text-lg sm:text-xl font-bold text-white mb-0 tracking-wide">PixelCast Signage</h1>
          <p class="text-slate-400 text-[11px] font-medium">Installation Wizard</p>
        </div>

        <!-- Flight Path: compact step indicator -->
        <div class="flight-path px-4 sm:px-5 pt-2 pb-1.5 border-b border-white/10 flex-shrink-0">
          <div class="flex items-center justify-between w-full mx-auto gap-0.5">
            <div
              v-for="(step, index) in steps"
              :key="index"
              class="flex items-center flex-1 min-w-0"
            >
              <div class="flex flex-col items-center flex-1 min-w-0">
                <div
                  class="flight-node w-6 h-6 sm:w-7 sm:h-7 rounded-full flex items-center justify-center transition-all duration-300 flex-shrink-0"
                  :class="getStepClass(index)"
                >
                  <component
                    :is="step.icon"
                    v-if="currentStep > index + 1"
                    class="w-3.5 h-3.5 sm:w-4 sm:h-4 cosmic-icon text-indigo-300"
                  />
                  <span v-else class="text-[10px] sm:text-xs font-semibold">{{ index + 1 }}</span>
                </div>
                <span
                  class="mt-0.5 text-[9px] sm:text-[10px] font-medium transition-colors duration-300 truncate max-w-full"
                  :class="currentStep >= index + 1 ? 'text-slate-300' : 'text-slate-500'"
                >
                  {{ step.label }}
                </span>
              </div>
              <div
                v-if="index < steps.length - 1"
                class="flex-1 h-0.5 mx-0.5 min-w-[8px] transition-all duration-300 rounded-full"
                :class="currentStep > index + 1 ? 'bg-indigo-500/80 flight-path-line--active' : 'bg-white/10'"
              />
            </div>
          </div>
        </div>

        <!-- Step Content: scrollable body; scrollbar-gutter: stable prevents horizontal shift when scrollbar appears -->
        <div class="wizard-card-body px-4 sm:px-5 py-2 sm:py-3 min-h-0 overflow-y-auto flex-1">
          <transition
            name="fade-slide"
            mode="out-in"
          >
            <!-- Step 1: Welcome — Mission Initialization (compact for 1080p) -->
            <div
              v-if="currentStep === 1"
              key="step-1"
              class="space-y-2"
            >
              <div class="text-center">
                <div class="cosmic-icon-wrap inline-flex items-center justify-center w-10 h-10 sm:w-11 sm:h-11 rounded-lg bg-indigo-500/10 border border-indigo-500/30 mb-1">
                  <RocketLaunchIcon class="w-5 h-5 sm:w-6 sm:h-6 text-indigo-400 cosmic-icon" />
                </div>
                <h2 class="cosmic-heading text-base sm:text-lg font-bold text-white mb-0.5">Mission Initialization</h2>
                <p class="text-slate-400 text-[11px] max-w-xl mx-auto leading-snug">
                  Configure your command center. This wizard will guide you through database, admin account, and system setup.
                </p>
              </div>

              <div class="mt-2 space-y-1 max-w-xl mx-auto">
                <div class="flex items-start gap-2 p-2 rounded-lg bg-white/5 border border-white/10">
                  <ServerIcon class="w-4 h-4 sm:w-5 sm:h-5 text-indigo-400 cosmic-icon flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 class="font-semibold text-slate-200 text-xs sm:text-sm mb-0">Database Configuration</h3>
                    <p class="text-[11px] sm:text-xs text-slate-500">Connect to your PostgreSQL database</p>
                  </div>
                </div>
                <div class="flex items-start gap-2 p-2 rounded-lg bg-white/5 border border-white/10">
                  <ShieldCheckIcon class="w-4 h-4 sm:w-5 sm:h-5 text-indigo-400 cosmic-icon flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 class="font-semibold text-slate-200 text-xs sm:text-sm mb-0">Admin Account</h3>
                    <p class="text-[11px] sm:text-xs text-slate-500">Create your master administrator account</p>
                  </div>
                </div>
                <div class="flex items-start gap-2 p-2 rounded-lg bg-white/5 border border-white/10">
                  <Cog6ToothIcon class="w-4 h-4 sm:w-5 sm:h-5 text-indigo-400 cosmic-icon flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 class="font-semibold text-slate-200 text-xs sm:text-sm mb-0">System Setup</h3>
                    <p class="text-[11px] sm:text-xs text-slate-500">Finalize installation and boot sequence</p>
                  </div>
                </div>
              </div>

              <div class="flex justify-center pt-2">
                <button
                  @click="nextStep"
                  type="button"
                  class="cosmic-btn-launch px-6 py-3 rounded-xl text-sm font-semibold text-white flex items-center gap-2 border-0"
                >
                  Start Installation
                  <ArrowRightIcon class="w-4 h-4" />
                </button>
              </div>
            </div>

            <!-- Step 2: Database — compact -->
            <div
              v-else-if="currentStep === 2"
              key="step-2"
              class="space-y-2"
            >
              <div class="text-center mb-2">
                <div class="cosmic-icon-wrap inline-flex items-center justify-center w-9 h-9 sm:w-10 sm:h-10 rounded-lg bg-indigo-500/10 border border-indigo-500/30 mb-1">
                  <ServerIcon class="w-5 h-5 sm:w-6 sm:h-6 text-indigo-400 cosmic-icon" />
                </div>
                <h2 class="cosmic-heading text-base sm:text-lg font-bold text-white mb-0.5">Database Configuration</h2>
                <p class="text-slate-400 text-[11px]">Enter your PostgreSQL database credentials</p>
              </div>

              <form @submit.prevent="testDatabaseConnection" class="space-y-2 max-w-2xl mx-auto">
                <div class="grid grid-cols-2 gap-3">
                  <div>
                    <label for="db-host" class="block text-sm font-medium text-slate-400 mb-1.5">Host <span class="text-red-400">*</span></label>
                    <input
                      id="db-host"
                      v-model="setupData.db.host"
                      type="text"
                      required
                      class="cosmic-input w-full px-4 py-3 rounded-xl bg-black/40 border border-white/10 text-white placeholder-slate-500 focus:outline-none transition-all duration-300"
                      placeholder="localhost"
                    />
                  </div>
                  <div>
                    <label for="db-port" class="block text-sm font-medium text-slate-400 mb-1.5">Port <span class="text-red-400">*</span></label>
                    <input
                      id="db-port"
                      v-model.number="setupData.db.port"
                      type="number"
                      required
                      class="cosmic-input w-full px-4 py-3 rounded-xl bg-black/40 border border-white/10 text-white placeholder-slate-500 focus:outline-none transition-all duration-300"
                      placeholder="5432"
                    />
                  </div>
                </div>

                <div>
                  <label for="db-name" class="block text-sm font-medium text-slate-400 mb-1.5">Database Name <span class="text-red-400">*</span></label>
                  <input
                    id="db-name"
                    v-model="setupData.db.name"
                    type="text"
                    required
                    class="cosmic-input w-full px-4 py-3 rounded-xl bg-black/40 border border-white/10 text-white placeholder-slate-500 focus:outline-none transition-all duration-300"
                    placeholder="screengram_db"
                  />
                </div>

                <div class="grid grid-cols-2 gap-3">
                  <div>
                    <label for="db-user" class="block text-sm font-medium text-slate-400 mb-1.5">Username <span class="text-red-400">*</span></label>
                    <input
                      id="db-user"
                      v-model="setupData.db.user"
                      type="text"
                      required
                      class="cosmic-input w-full px-4 py-3 rounded-xl bg-black/40 border border-white/10 text-white placeholder-slate-500 focus:outline-none transition-all duration-300"
                      placeholder="screengram_user"
                    />
                  </div>
                  <div>
                    <label for="db-password" class="block text-sm font-medium text-slate-400 mb-1.5">Password</label>
                    <div class="relative">
                      <input
                        id="db-password"
                        v-model="setupData.db.password"
                        :type="showDbPassword ? 'text' : 'password'"
                        class="cosmic-input w-full px-4 py-3 rounded-xl pr-12 bg-black/40 border border-white/10 text-white placeholder-slate-500 focus:outline-none transition-all duration-300"
                        placeholder="Optional: leave blank to use username as password"
                      />
                      <button
                        type="button"
                        @click="showDbPassword = !showDbPassword"
                        class="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-500 hover:text-indigo-400 transition-colors"
                      >
                        <EyeIcon v-if="!showDbPassword" class="w-5 h-5 cosmic-icon" />
                        <EyeSlashIcon v-else class="w-5 h-5 cosmic-icon" />
                      </button>
                    </div>
                  </div>
                </div>

                <!-- Connection Status -->
                <transition name="fade">
                  <div
                    v-if="dbStatus.message"
                    class="p-4 rounded-xl border"
                    :class="dbStatus.success ? 'bg-emerald-500/10 border-emerald-500/30' : 'bg-red-500/10 border-red-500/30'"
                  >
                    <div class="flex items-start gap-2">
                      <CheckCircleIcon v-if="dbStatus.success" class="w-5 h-5 text-emerald-400 cosmic-icon flex-shrink-0 mt-0.5" />
                      <XCircleIcon v-else class="w-5 h-5 text-red-400 cosmic-icon flex-shrink-0 mt-0.5" />
                      <p :class="dbStatus.success ? 'text-emerald-300' : 'text-red-300'" class="text-sm">
                        {{ dbStatus.message }}
                      </p>
                    </div>
                  </div>
                </transition>

                <div class="flex justify-between items-center gap-4 pt-1.5">
                  <button
                    type="button"
                    @click="prevStep"
                    class="cosmic-btn-prev inline-flex items-center gap-2 py-2.5 px-4 rounded-xl border border-white/10 bg-transparent text-white/60 hover:text-white hover:border-indigo-500/60 transition-all duration-300 active:scale-95 text-sm font-medium"
                    aria-label="Return to previous step"
                  >
                    <ArrowLeftIcon class="w-4 h-4 flex-shrink-0" aria-hidden="true" />
                    Back
                  </button>
                  <div class="flex items-center gap-2 flex-1 justify-end min-w-0">
                    <button
                      type="button"
                      @click="testDatabaseConnection"
                      :disabled="dbStatus.loading"
                      class="cosmic-input-btn flex-1 sm:flex-none py-2.5 px-4 rounded-xl disabled:opacity-50 flex items-center justify-center gap-2 border border-white/20 text-slate-300 hover:bg-white/5 hover:border-indigo-500/50 transition-all text-sm"
                    >
                      <svg
                        v-if="dbStatus.loading"
                        class="animate-spin h-5 w-5 text-indigo-400"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                      >
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      <span>{{ dbStatus.loading ? 'Scanning...' : 'Test Connection' }}</span>
                    </button>
                    <button
                      v-if="dbStatus.success"
                      type="button"
                      @click="nextStep"
                      class="cosmic-btn py-2.5 px-4 rounded-xl text-white font-medium flex items-center justify-center gap-2 text-sm"
                    >
                      Continue
                      <ArrowRightIcon class="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </form>
            </div>

            <!-- Step 3: Admin — compact -->
            <div
              v-else-if="currentStep === 3"
              key="step-3"
              class="space-y-2"
            >
              <div class="text-center mb-2">
                <div class="cosmic-icon-wrap inline-flex items-center justify-center w-9 h-9 sm:w-10 sm:h-10 rounded-lg bg-indigo-500/10 border border-indigo-500/30 mb-1">
                  <ShieldCheckIcon class="w-5 h-5 sm:w-6 sm:h-6 text-indigo-400 cosmic-icon" />
                </div>
                <h2 class="cosmic-heading text-base sm:text-lg font-bold text-white mb-0.5">Create Administrator Account</h2>
                <p class="text-slate-400 text-[11px]">Set up your master administrator identity</p>
              </div>

              <form @submit.prevent="createAdmin" class="space-y-2 max-w-2xl mx-auto">
                <!-- Username: floating label -->
                <div class="input-wrap">
                  <div class="input-group relative group">
                    <input
                      id="admin-username"
                      v-model="setupData.admin.username"
                      type="text"
                      required
                      class="cosmic-input w-full px-4 py-3 rounded-xl bg-black/40 border border-white/10 text-white placeholder-transparent focus:outline-none transition-all duration-300"
                      placeholder=" "
                      @focus="focusAdminUsername = true"
                      @blur="focusAdminUsername = false"
                    />
                    <label
                      for="admin-username"
                      class="floating-label cosmic-floating-label"
                      :class="{ 'floating-label--active': setupData.admin.username || focusAdminUsername }"
                    >
                      Username <span class="text-red-400">*</span>
                    </label>
                  </div>
                  <p v-if="errors.username" class="text-red-400 text-sm mt-1">{{ errors.username[0] }}</p>
                </div>

                <!-- Email: floating label -->
                <div class="input-wrap">
                  <div class="input-group relative group">
                    <input
                      id="admin-email"
                      v-model="setupData.admin.email"
                      type="email"
                      required
                      class="cosmic-input w-full px-4 py-3 rounded-xl bg-black/40 border border-white/10 text-white placeholder-transparent focus:outline-none transition-all duration-300"
                      placeholder=" "
                      @focus="focusAdminEmail = true"
                      @blur="focusAdminEmail = false"
                    />
                    <label
                      for="admin-email"
                      class="floating-label cosmic-floating-label"
                      :class="{ 'floating-label--active': setupData.admin.email || focusAdminEmail }"
                    >
                      Email <span class="text-red-400">*</span>
                    </label>
                  </div>
                  <p v-if="errors.email" class="text-red-400 text-sm mt-1">{{ errors.email[0] }}</p>
                </div>

                <!-- Password: floating label -->
                <div class="input-wrap">
                  <div class="input-group relative group">
                    <input
                      id="admin-password"
                      v-model="setupData.admin.password"
                      :type="showAdminPassword ? 'text' : 'password'"
                      minlength="8"
                      class="cosmic-input w-full px-4 py-3 rounded-xl pr-12 bg-black/40 border border-white/10 text-white placeholder-transparent focus:outline-none transition-all duration-300"
                      placeholder=" "
                      @focus="focusAdminPassword = true"
                      @blur="focusAdminPassword = false"
                    />
                    <label
                      for="admin-password"
                      class="floating-label cosmic-floating-label"
                      :class="{ 'floating-label--active': setupData.admin.password || focusAdminPassword }"
                    >
                      Password <span class="text-red-400">*</span> (min 8 characters)
                    </label>
                    <button
                      type="button"
                      @click="showAdminPassword = !showAdminPassword"
                      class="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-500 hover:text-indigo-400 transition-colors"
                    >
                      <EyeIcon v-if="!showAdminPassword" class="w-5 h-5 cosmic-icon" />
                      <EyeSlashIcon v-else class="w-5 h-5 cosmic-icon" />
                    </button>
                  </div>
                  <p v-if="errors.password" class="text-red-400 text-sm mt-1">{{ errors.password[0] }}</p>
                </div>

                <div class="grid grid-cols-2 gap-3">
                  <!-- First name: floating label -->
                  <div class="input-wrap">
                    <div class="input-group relative group">
                      <input
                        id="admin-first-name"
                        v-model="setupData.admin.first_name"
                        type="text"
                        class="cosmic-input w-full px-4 py-3 rounded-xl bg-black/40 border border-white/10 text-white placeholder-transparent focus:outline-none transition-all duration-300"
                        placeholder=" "
                        @focus="focusAdminFirstName = true"
                        @blur="focusAdminFirstName = false"
                      />
                      <label
                        for="admin-first-name"
                        class="floating-label cosmic-floating-label"
                        :class="{ 'floating-label--active': setupData.admin.first_name || focusAdminFirstName }"
                      >
                        First Name
                      </label>
                    </div>
                  </div>
                  <!-- Last name: floating label -->
                  <div class="input-wrap">
                    <div class="input-group relative group">
                      <input
                        id="admin-last-name"
                        v-model="setupData.admin.last_name"
                        type="text"
                        class="cosmic-input w-full px-4 py-3 rounded-xl bg-black/40 border border-white/10 text-white placeholder-transparent focus:outline-none transition-all duration-300"
                        placeholder=" "
                        @focus="focusAdminLastName = true"
                        @blur="focusAdminLastName = false"
                      />
                      <label
                        for="admin-last-name"
                        class="floating-label cosmic-floating-label"
                        :class="{ 'floating-label--active': setupData.admin.last_name || focusAdminLastName }"
                      >
                        Last Name
                      </label>
                    </div>
                  </div>
                </div>

                <transition name="fade">
                  <div
                    v-if="adminStatus.message"
                    class="p-4 rounded-xl border"
                    :class="adminStatus.success ? 'bg-emerald-500/10 border-emerald-500/30' : 'bg-red-500/10 border-red-500/30'"
                  >
                    <p :class="adminStatus.success ? 'text-emerald-300' : 'text-red-300'" class="text-sm">
                      {{ adminStatus.message }}
                    </p>
                  </div>
                </transition>

                <div class="flex justify-between items-center gap-4 pt-1.5">
                  <button
                    type="button"
                    @click="prevStep"
                    class="cosmic-btn-prev inline-flex items-center gap-2 py-2.5 px-4 rounded-xl border border-white/10 bg-transparent text-white/60 hover:text-white hover:border-indigo-500/60 transition-all duration-300 active:scale-95 text-sm font-medium"
                    aria-label="Return to previous step"
                  >
                    <ArrowLeftIcon class="w-4 h-4 flex-shrink-0" aria-hidden="true" />
                    Back
                  </button>
                  <div class="flex items-center gap-2 flex-1 justify-end min-w-0">
                    <button
                      type="submit"
                      :disabled="adminStatus.loading || adminStatus.success"
                      class="cosmic-btn-confirm flex-1 sm:flex-none py-2.5 px-4 rounded-xl text-white font-semibold disabled:opacity-50 flex items-center justify-center gap-2 border-0 text-sm"
                    >
                      <svg
                        v-if="adminStatus.loading"
                        class="animate-spin h-5 w-5"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                      >
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      <span>{{ adminStatus.loading ? 'Verifying...' : adminStatus.success ? 'Identity Confirmed' : 'Confirm Identity' }}</span>
                    </button>
                    <button
                      v-if="adminStatus.success"
                      type="button"
                      @click="nextStep"
                      class="cosmic-btn py-2.5 px-4 rounded-xl text-white font-medium flex items-center justify-center gap-2 text-sm"
                    >
                      Continue
                      <ArrowRightIcon class="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </form>
            </div>

            <!-- Step 4: System Boot Sequence — compact -->
            <div
              v-else-if="currentStep === 4"
              key="step-4"
              class="space-y-2"
            >
              <div class="text-center mb-2">
                <div class="cosmic-icon-wrap inline-flex items-center justify-center w-9 h-9 sm:w-10 sm:h-10 rounded-lg bg-indigo-500/10 border border-indigo-500/30 mb-1">
                  <Cog6ToothIcon class="w-5 h-5 sm:w-6 sm:h-6 text-indigo-400 cosmic-icon animate-spin" />
                </div>
                <h2 class="cosmic-heading text-base sm:text-lg font-bold text-white mb-0.5">System Boot Sequence</h2>
                <p class="text-slate-400 text-[11px] boot-glow">Initializing command center...</p>
              </div>

              <!-- Boot sequence steps with glowing text -->
              <div class="space-y-1.5 max-w-2xl mx-auto">
                <div
                  v-for="(progressStep, index) in progressSteps"
                  :key="index"
                  class="flex items-center gap-3 p-3 rounded-xl transition-all duration-300"
                  :class="getProgressStepClass(progressStep.status)"
                >
                  <div class="flex-shrink-0">
                    <div
                      v-if="progressStep.status === 'completed'"
                      class="w-10 h-10 rounded-full bg-emerald-500/80 flex items-center justify-center shadow-[0_0_12px_rgba(34,197,94,0.4)]"
                    >
                      <CheckCircleIcon class="w-6 h-6 text-white cosmic-icon" />
                    </div>
                    <div
                      v-else-if="progressStep.status === 'loading'"
                      class="w-10 h-10 rounded-full bg-indigo-500/80 flex items-center justify-center shadow-[0_0_12px_rgba(99,102,241,0.4)]"
                    >
                      <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                    </div>
                    <div
                      v-else
                      class="w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center"
                    >
                      <span class="text-slate-500 text-sm font-semibold">{{ index + 1 }}</span>
                    </div>
                  </div>
                  <div class="flex-1">
                    <h3 class="font-semibold text-slate-200 boot-step-label">{{ progressStep.label }}</h3>
                    <p class="text-sm boot-glow text-slate-400">{{ progressStep.description }}</p>
                  </div>
                </div>
              </div>

              <!-- System Boot Progress Bar -->
              <div class="max-w-2xl mx-auto pt-4">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-sm font-medium text-slate-400">Boot Progress</span>
                  <span class="text-sm font-semibold text-indigo-300 boot-glow">{{ overallProgress }}%</span>
                </div>
                <div class="w-full h-2 bg-black/40 rounded-full overflow-hidden border border-white/10">
                  <div
                    class="boot-progress-bar h-2 rounded-full transition-all duration-500 ease-out relative"
                    :style="{ width: `${overallProgress}%` }"
                  />
                </div>
              </div>

              <!-- Completion Message -->
              <transition name="fade">
                <div
                  v-if="installationComplete"
                  class="text-center pt-6"
                >
                  <div class="cosmic-icon-wrap inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-emerald-500/20 border border-emerald-500/40 mb-4 shadow-[0_0_24px_rgba(34,197,94,0.2)]">
                    <CheckCircleIcon class="w-10 h-10 text-emerald-400 cosmic-icon" />
                  </div>
                  <h3 class="cosmic-heading text-2xl font-bold text-white mb-2">Installation Complete!</h3>
                  <p class="text-slate-400 mb-6">Your PixelCast command center is ready.</p>
                  <router-link
                    to="/login"
                    class="cosmic-btn inline-flex items-center px-8 py-3.5 rounded-xl text-base font-semibold text-white"
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
  ArrowLeftIcon,
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
const focusAdminUsername = ref(false)
const focusAdminEmail = ref(false)
const focusAdminPassword = ref(false)
const focusAdminFirstName = ref(false)
const focusAdminLastName = ref(false)

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

// Progress steps — System Boot Sequence copy
const progressSteps = reactive([
  {
    label: 'Initializing Core Modules',
    description: 'Applying schema changes to your database...',
    status: 'pending', // pending, loading, completed, error
  },
  {
    label: 'Syncing Galactic Assets',
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

// Methods — Flight Path node classes
const getStepClass = (index) => {
  const stepNum = index + 1
  if (currentStep.value > stepNum) {
    return 'bg-indigo-500/80 text-white shadow-[0_0_12px_rgba(99,102,241,0.5)]'
  }
  if (currentStep.value === stepNum) {
    return 'bg-indigo-500/20 text-indigo-300 border-2 border-indigo-500/60 shadow-[0_0_16px_rgba(99,102,241,0.3)]'
  }
  return 'bg-white/5 text-slate-500 border border-white/10'
}

const getProgressStepClass = (status) => {
  switch (status) {
    case 'completed':
      return 'bg-emerald-500/10 border border-emerald-500/30 boot-step--completed'
    case 'loading':
      return 'bg-indigo-500/10 border border-indigo-500/30 boot-step--loading'
    case 'error':
      return 'bg-red-500/10 border border-red-500/30'
    default:
      return 'bg-white/5 border border-white/10'
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
  
  // Step 3: Finalize (send db credentials so .env gets DB_PASSWORD / POSTGRES_PASSWORD; empty password => username used as password)
  progressSteps[2].status = 'loading'
  try {
    await setupAPI.finalize({
      db_name: setupData.db.name,
      db_user: setupData.db.user,
      db_password: setupData.db.password || undefined,
      db_host: setupData.db.host,
      db_port: setupData.db.port,
    })
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
/* Page: Deep Space — full viewport, scrollable when content is tall */
.cosmic-wizard {
  font-family: 'Plus Jakarta Sans', sans-serif;
  position: relative;
  min-height: 100vh;
  min-height: 100dvh; /* dynamic viewport height on mobile */
}

/* Background: gradient from spec */
.cosmic-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  background: linear-gradient(to bottom right, #0B0E14, #151921, #080A0F);
  pointer-events: none;
}

/* Starfield */
.cosmic-starfield {
  position: fixed;
  inset: 0;
  z-index: 1;
  pointer-events: none;
  opacity: 0.6;
  animation: cosmicTwinkle 6s ease-in-out infinite;
}

.cosmic-starfield::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(1.5px 1.5px at 15% 25%, rgba(255,255,255,0.9), transparent),
    radial-gradient(1px 1px at 25% 15%, rgba(255,255,255,0.7), transparent),
    radial-gradient(1.5px 1.5px at 75% 30%, rgba(255,255,255,0.8), transparent),
    radial-gradient(1px 1px at 85% 20%, rgba(255,255,255,0.6), transparent),
    radial-gradient(1.5px 1.5px at 10% 60%, rgba(255,255,255,0.7), transparent),
    radial-gradient(1px 1px at 30% 70%, rgba(255,255,255,0.8), transparent),
    radial-gradient(1.5px 1.5px at 60% 80%, rgba(255,255,255,0.6), transparent),
    radial-gradient(1px 1px at 80% 55%, rgba(255,255,255,0.9), transparent),
    radial-gradient(1.5px 1.5px at 45% 35%, rgba(255,255,255,0.5), transparent),
    radial-gradient(1px 1px at 55% 45%, rgba(255,255,255,0.7), transparent),
    radial-gradient(1.5px 1.5px at 20% 85%, rgba(255,255,255,0.6), transparent),
    radial-gradient(1px 1px at 90% 75%, rgba(255,255,255,0.5), transparent),
    radial-gradient(1.5px 1.5px at 5% 40%, rgba(255,255,255,0.8), transparent),
    radial-gradient(1px 1px at 95% 50%, rgba(255,255,255,0.6), transparent),
    radial-gradient(1.5px 1.5px at 40% 10%, rgba(255,255,255,0.7), transparent),
    radial-gradient(1px 1px at 70% 65%, rgba(255,255,255,0.8), transparent);
  background-size: 100% 100%;
  background-repeat: repeat;
}

@keyframes cosmicTwinkle {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 0.9; }
}

/* Nebula accents — reduced opacity so they don’t create a dark cut-off at card bottom */
.nebula {
  position: fixed;
  border-radius: 50%;
  filter: blur(100px);
  pointer-events: none;
  z-index: 1;
  opacity: 0.12;
}
.nebula--indigo {
  width: 380px;
  height: 380px;
  background: rgba(99, 102, 241, 0.28);
  top: -120px;
  right: -120px;
}
.nebula--purple {
  width: 320px;
  height: 320px;
  background: rgba(139, 92, 246, 0.22);
  bottom: -100px;
  left: -100px;
}

/* Command Center card — glassmorphic, max 90vh so scroll is inside card */
.command-center {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow:
    0 25px 50px -12px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

/* Card scroll area: stable gutter prevents horizontal shift when scrollbar appears (global Energy Rail applies) */
.wizard-card-body {
  scrollbar-gutter: stable;
}

/* Return to Base: cosmic exit button */
.exit-btn-wrapper {
  font-family: 'Plus Jakarta Sans', sans-serif;
}
.exit-btn .cosmic-icon {
  transition: filter 0.3s ease;
}
.exit-btn:hover .cosmic-icon {
  filter: drop-shadow(0 0 8px rgba(99, 102, 241, 0.6));
}
.exit-tooltip {
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.05);
}

/* Typography */
.cosmic-title,
.cosmic-heading {
  letter-spacing: 0.05em;
  text-shadow: 0 0 30px rgba(99, 102, 241, 0.2);
}

.cosmic-icon {
  filter: drop-shadow(0 0 6px rgba(99, 102, 241, 0.4));
}

.cosmic-icon-wrap {
  box-shadow: 0 0 20px rgba(99, 102, 241, 0.15);
}

/* Flight path line glow when active */
.flight-path-line--active {
  box-shadow: 0 0 8px rgba(99, 102, 241, 0.4);
}

/* Step transition: fade-slide (spaceship monitor) */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.35s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(24px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-24px);
}

/* Fade */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Input: Electric Indigo focus glow */
.cosmic-input {
  border-color: rgba(255, 255, 255, 0.1);
}

.cosmic-input:focus {
  border-color: #6366F1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.25), 0 0 20px rgba(99, 102, 241, 0.15);
}

/* Start Installation button — pulse glow */
.cosmic-btn-launch {
  background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
  box-shadow: 0 4px 24px rgba(99, 102, 241, 0.5);
  animation: cosmic-pulse 2s ease-in-out infinite;
}

.cosmic-btn-launch:hover {
  box-shadow: 0 8px 32px rgba(99, 102, 241, 0.6), 0 0 40px rgba(99, 102, 241, 0.2);
}

@keyframes cosmic-pulse {
  0%, 100% { box-shadow: 0 4px 24px rgba(99, 102, 241, 0.5); }
  50% { box-shadow: 0 6px 28px rgba(99, 102, 241, 0.6), 0 0 30px rgba(99, 102, 241, 0.15); }
}

/* Ghost / secondary buttons */
.cosmic-btn-ghost:hover {
  border-color: rgba(255, 255, 255, 0.25);
}

/* Return to Previous: cosmic Back button (Step 2 & 3) — ghost + indigo hover + tactile */
.cosmic-btn-prev:hover {
  box-shadow: 0 0 12px rgba(99, 102, 241, 0.25);
}

/* Primary action button */
.cosmic-btn {
  background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
  box-shadow: 0 4px 20px rgba(99, 102, 241, 0.35);
}

.cosmic-btn:hover {
  box-shadow: 0 8px 30px rgba(99, 102, 241, 0.45);
}

/* Confirm Identity — high-stakes style */
.cosmic-btn-confirm {
  background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
  box-shadow: 0 4px 24px rgba(99, 102, 241, 0.4), 0 0 20px rgba(99, 102, 241, 0.2);
}

.cosmic-btn-confirm:hover:not(:disabled) {
  box-shadow: 0 6px 28px rgba(99, 102, 241, 0.5), 0 0 30px rgba(99, 102, 241, 0.25);
}

/* Floating labels (Step 3) */
.input-wrap {
  position: relative;
}

.input-wrap .input-group {
  margin-top: 0;
}

.floating-label {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1rem;
  pointer-events: none;
  transition: transform 0.2s ease, font-size 0.2s ease, color 0.2s ease, top 0.2s ease;
}

.cosmic-floating-label {
  color: rgb(148 163 184);
}

.floating-label--active {
  top: -0.75rem;
  transform: translateY(0);
  font-size: 0.75rem;
  font-weight: 500;
}

.floating-label--active.cosmic-floating-label {
  color: rgb(148 163 184);
}

/* System Boot: glowing text */
.boot-glow {
  text-shadow: 0 0 12px rgba(99, 102, 241, 0.3);
}

.boot-step-label {
  text-shadow: 0 0 8px rgba(99, 102, 241, 0.2);
}

.boot-step--loading .boot-step-label {
  text-shadow: 0 0 10px rgba(99, 102, 241, 0.4);
}

.boot-step--completed .boot-step-label {
  text-shadow: 0 0 8px rgba(34, 197, 94, 0.3);
}

/* Boot progress bar */
.boot-progress-bar {
  background: linear-gradient(90deg, #6366F1, #818CF8);
  box-shadow: 0 0 16px rgba(99, 102, 241, 0.5);
}
</style>

