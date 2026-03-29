<template>
  <div class="auth-page cosmic-auth min-h-screen flex flex-col items-center justify-center px-4 py-16 relative">
    <div class="cosmic-bg" aria-hidden="true" />
    <div class="cosmic-starfield" aria-hidden="true" />
    <div class="nebula nebula--indigo" aria-hidden="true" />
    <div class="nebula nebula--purple" aria-hidden="true" />

    <div class="w-full max-w-md relative z-10 text-center">
      <div
        v-motion
        :initial="{ opacity: 0, y: 12 }"
        :enter="{ opacity: 1, y: 0 }"
        :transition="{ duration: 400 }"
        class="glass-portal rounded-2xl overflow-hidden px-8 py-10"
      >
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 mb-6 mx-auto">
          <ShieldExclamationIcon class="w-9 h-9 cosmic-icon" />
        </div>
        <p class="text-sm font-medium text-indigo-300/90 tracking-widest uppercase mb-2">403</p>
        <h1 class="cosmic-heading text-2xl font-bold text-white mb-2">Access denied</h1>
        <p class="text-sm text-slate-400 leading-relaxed mb-8">
          {{ message }}
        </p>
        <div class="flex flex-col sm:flex-row gap-3 justify-center">
          <router-link
            to="/dashboard"
            class="cosmic-btn auth-btn inline-flex items-center justify-center gap-2 py-3 px-5 rounded-xl font-semibold text-white transition-all duration-300 min-h-[48px]"
          >
            <HomeIcon class="w-5 h-5" />
            Go to dashboard
          </router-link>
          <button
            type="button"
            class="inline-flex items-center justify-center gap-2 py-3 px-5 rounded-xl font-medium text-slate-300 border border-white/20 hover:border-cyan-400/60 hover:text-cyan-400 hover:bg-cyan-400/10 transition-all duration-300 min-h-[48px]"
            @click="$router.back()"
          >
            <ArrowLeftIcon class="w-5 h-5" />
            Go back
          </button>
        </div>
      </div>

      <router-link
        to="/"
        class="mt-8 inline-flex items-center justify-center gap-2 text-sm text-slate-500 hover:text-slate-300 transition-colors duration-300"
      >
        <ArrowLeftIcon class="h-4 w-4" />
        Back to home
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { ShieldExclamationIcon, HomeIcon, ArrowLeftIcon } from '@heroicons/vue/24/outline'

const route = useRoute()

const message = computed(() => {
  const q = route.query.reason
  if (typeof q === 'string' && q.trim()) return q
  return 'This area is restricted by your role. If you need access, ask a Developer on your team.'
})
</script>

<style scoped>
.auth-page {
  position: relative;
  font-family: 'Plus Jakarta Sans', sans-serif;
}

.cosmic-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  background: linear-gradient(to bottom right, #0B0E14, #161B22, #0B0E14);
  pointer-events: none;
}

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

.nebula {
  position: fixed;
  border-radius: 50%;
  filter: blur(100px);
  pointer-events: none;
  z-index: 1;
  opacity: 0.25;
}
.nebula--indigo {
  width: 400px;
  height: 400px;
  background: rgba(99, 102, 241, 0.4);
  top: -100px;
  right: -100px;
}
.nebula--purple {
  width: 350px;
  height: 350px;
  background: rgba(139, 92, 246, 0.35);
  bottom: -80px;
  left: -80px;
}

.glass-portal {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow:
    0 25px 50px -12px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.cosmic-heading {
  letter-spacing: 0.05em;
  text-shadow: 0 0 30px rgba(99, 102, 241, 0.2);
}

.cosmic-icon {
  filter: drop-shadow(0 0 4px rgba(99, 102, 241, 0.4));
}

.cosmic-btn {
  background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
  box-shadow: 0 4px 20px rgba(99, 102, 241, 0.35);
}
.cosmic-btn:hover {
  box-shadow: 0 8px 30px rgba(99, 102, 241, 0.45), 0 0 40px rgba(34, 211, 238, 0.15);
}
</style>
