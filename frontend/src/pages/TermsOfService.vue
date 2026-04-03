<template>
  <div class="terms-page min-h-screen text-slate-200">
    <div class="terms-starfield pointer-events-none fixed inset-0 z-0" aria-hidden="true" />
    <div class="terms-animated-bg fixed inset-0 z-0 opacity-90" aria-hidden="true" />

    <header
      class="sticky top-0 z-50 border-b border-white/10 bg-slate-950/75 backdrop-blur-xl safe-area-pt"
    >
      <div class="mx-auto flex max-w-4xl items-center justify-between gap-4 px-4 py-4 sm:px-6">
        <router-link
          :to="backRoute"
          class="group inline-flex items-center gap-2 text-sm font-medium text-white/80 transition-colors hover:text-cyan-300"
        >
          <ArrowLeftIcon class="h-5 w-5 shrink-0 transition-transform group-hover:-translate-x-0.5" />
          <span>{{ backText }}</span>
        </router-link>
        <router-link
          to="/privacy"
          class="hidden text-xs font-medium text-white/55 hover:text-cyan-300 sm:inline sm:text-sm"
        >
          Privacy Policy
        </router-link>
      </div>
    </header>

    <main class="relative z-10 mx-auto max-w-4xl px-4 pb-20 pt-10 sm:px-6 lg:px-8">
      <!-- Hero block -->
      <div class="mb-12 text-center sm:mb-14">
        <div
          class="mx-auto mb-6 inline-flex h-16 w-16 items-center justify-center rounded-2xl border border-cyan-400/25 bg-gradient-to-br from-cyan-500/20 to-purple-600/25 shadow-[0_0_40px_rgba(34,211,238,0.15)]"
        >
          <DocumentTextIcon class="h-8 w-8 text-cyan-300" />
        </div>
        <p
          class="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-cyan-400/90"
        >
          Legal orbit
        </p>
        <h1
          class="mb-4 text-3xl font-bold tracking-tight text-white sm:text-4xl md:text-5xl"
        >
          <span
            class="bg-gradient-to-r from-cyan-300 via-blue-300 to-purple-400 bg-clip-text text-transparent"
          >
            Terms of Service
          </span>
        </h1>
        <p class="flex flex-wrap items-center justify-center gap-2 text-sm text-white/55">
          <ClockIcon class="h-4 w-4 text-cyan-400/80" />
          <span>Last updated <strong class="font-semibold text-white/80">{{ lastUpdated }}</strong></span>
        </p>
        <p class="mx-auto mt-4 max-w-2xl text-sm leading-relaxed text-slate-400">
          These Terms govern your use of PixelCast and related services. Please read them carefully—your continued use of
          the Service means you accept them.
        </p>
      </div>

      <div class="space-y-8 md:space-y-10">
        <!-- 1 -->
        <section class="terms-glass rounded-2xl p-6 sm:p-8">
          <h2 class="terms-h2">
            <span class="terms-section-num">1</span>
            Agreement &amp; definitions
          </h2>
          <div class="terms-prose space-y-4">
            <p>
              These Terms of Service (“<strong>Terms</strong>”) form a binding agreement between you (“<strong>you</strong>,”
              “<strong>your</strong>,” or “<strong>Customer</strong>”) and the operator of the PixelCast digital signage
              platform (“<strong>PixelCast</strong>,” “<strong>we</strong>,” “<strong>us</strong>,” or “<strong>our</strong>”).
            </p>
            <p>
              The software, websites, APIs, documentation, and related services we make available (collectively, the
              “<strong>Service</strong>”) include tools to manage screens, templates, schedules, commands, users, and
              monitoring features, as described in your order, subscription, or deployment documentation.
            </p>
            <p>
              By creating an account, accessing, or using the Service, you agree to these Terms and to our
              <router-link class="terms-link" to="/privacy">Privacy Policy</router-link>. If you are accepting on behalf
              of a company or organization, you represent that you have authority to bind that entity.
            </p>
            <p>
              If you do not agree, do not use the Service. We may refuse or suspend access where permitted by law.
            </p>
          </div>
        </section>

        <!-- 2 -->
        <section class="terms-glass rounded-2xl p-6 sm:p-8">
          <h2 class="terms-h2">
            <span class="terms-section-num">2</span>
            The Service
          </h2>
          <div class="terms-prose space-y-4">
            <p>
              PixelCast provides a cloud or self-hosted environment (depending on your deployment) for digital signage
              operations, including remote management of displays, content and template workflows, scheduling, player
              pairing, audit and operational logs, and role-based access for your team.
            </p>
            <p>
              Features may vary by plan, license, or deployment type (for example SaaS with Stripe billing, or
              self-hosted licensing). We may update, add, or retire features where we reasonably believe it improves
              security, compliance, or reliability, subject to applicable law and any separate agreement with you.
            </p>
            <ul class="terms-list">
              <li v-for="(f, i) in serviceHighlights" :key="i">{{ f }}</li>
            </ul>
          </div>
        </section>

        <!-- 3 -->
        <section class="terms-glass rounded-2xl p-6 sm:p-8">
          <h2 class="terms-h2">
            <span class="terms-section-num">3</span>
            Accounts, eligibility &amp; security
          </h2>
          <div class="terms-prose space-y-4">
            <p>
              You must provide accurate registration information and keep it current. You are responsible for all
              activity under your account and for safeguarding credentials. Notify us promptly of suspected unauthorized
              use.
            </p>
            <p>
              You may invite or administer users within your organization subject to roles and permissions we make
              available. You are responsible for your users’ compliance with these Terms.
            </p>
            <ul class="terms-list">
              <li v-for="(s, i) in securityItems" :key="i">{{ s }}</li>
            </ul>
          </div>
        </section>

        <!-- 4 -->
        <section class="terms-glass rounded-2xl p-6 sm:p-8">
          <h2 class="terms-h2">
            <span class="terms-section-num">4</span>
            Plans, trials, billing &amp; taxes
          </h2>
          <div class="terms-prose space-y-4">
            <p>
              <strong>Subscriptions and trials.</strong> If you use a paid or trial offering, fees, renewal, and trial
              length are those presented at checkout or in your order (including any free trial period we offer from time
              to time). When a trial ends, paid features may require a valid subscription to continue.
            </p>
            <p>
              <strong>Payment processing.</strong> For cloud/SaaS offerings, payments may be processed by third-party
              providers (for example Stripe). Your use of payment services may also be subject to that provider’s terms
              and privacy policy.
            </p>
            <p>
              <strong>Taxes.</strong> Fees are stated exclusive of applicable taxes unless otherwise indicated. You are
              responsible for any taxes imposed on your purchase, except taxes based on our net income.
            </p>
            <p>
              <strong>Changes to commercial terms.</strong> We may adjust pricing or plans with reasonable notice where
              required by law or contract. Continued use after the effective date may constitute acceptance of updated
              fees for renewal periods, as described in your agreement or checkout flow.
            </p>
          </div>
        </section>

        <!-- 5 -->
        <section class="terms-glass rounded-2xl p-6 sm:p-8">
          <h2 class="terms-h2">
            <span class="terms-section-num">5</span>
            License to use the Service
          </h2>
          <div class="terms-prose space-y-4">
            <p>
              Subject to these Terms and your compliance with them, we grant you a limited, non-exclusive,
              non-transferable (except as permitted below), revocable license to access and use the Service for your
              internal business purposes during the subscription or license term.
            </p>
            <p>
              You will not (and will not allow third parties to): copy, modify, or create derivative works of the Service
              except as allowed by law; reverse engineer, decompile, or attempt to extract source code except where
              mandatory law permits; probe, scan, or test the vulnerability of our systems without authorization; or use
              the Service to build a competing product or service.
            </p>
          </div>
        </section>

        <!-- 6 -->
        <section class="terms-glass rounded-2xl p-6 sm:p-8">
          <h2 class="terms-h2">
            <span class="terms-section-num">6</span>
            Your content &amp; responsibility
          </h2>
          <div class="terms-prose space-y-4">
            <p>
              You retain ownership of content you upload or instruct us to process (“<strong>Customer Content</strong>”).
              You grant us a worldwide license to host, process, transmit, and display Customer Content only as reasonably
              necessary to provide, secure, and improve the Service, and as described in the Privacy Policy.
            </p>
            <p>
              You represent and warrant that you have all rights, consents, and licenses needed for Customer Content
              and for displaying it on your screens, including publicity, trademark, and copyright permissions where
              applicable. You are solely responsible for the legality and appropriateness of content shown through your
              deployment.
            </p>
          </div>
        </section>

        <!-- 7 -->
        <section class="terms-glass rounded-2xl p-6 sm:p-8">
          <h2 class="terms-h2">
            <span class="terms-section-num">7</span>
            Acceptable use
          </h2>
          <div class="terms-prose space-y-4">
            <p>You agree not to use the Service to:</p>
            <ul class="terms-list">
              <li v-for="(p, i) in prohibitedItems" :key="i">{{ p }}</li>
            </ul>
            <p>
              We may investigate suspected violations and cooperate with law enforcement. We may remove content or suspend
              access where we reasonably believe it is necessary to protect the Service, users, or the public.
            </p>
          </div>
        </section>

        <!-- 8 -->
        <section class="terms-glass rounded-2xl p-6 sm:p-8">
          <h2 class="terms-h2">
            <span class="terms-section-num">8</span>
            Our intellectual property
          </h2>
          <div class="terms-prose space-y-4">
            <p>
              The Service, including software, branding, documentation, and underlying technology, is owned by us or our
              licensors and is protected by intellectual property laws. Except for the limited license in Section 5, no
              rights are granted to you. Feedback you provide may be used by us without obligation or restriction.
            </p>
          </div>
        </section>

        <!-- 9 -->
        <section class="terms-glass rounded-2xl p-6 sm:p-8">
          <h2 class="terms-h2">
            <span class="terms-section-num">9</span>
            Third-party services
          </h2>
          <div class="terms-prose space-y-4">
            <p>
              The Service may integrate with or link to third-party services (including payment processors, identity
              providers, or infrastructure). Those services are governed by their own terms. We are not responsible for
              third-party services or content.
            </p>
          </div>
        </section>

        <!-- 10 -->
        <section class="terms-glass rounded-2xl p-6 sm:p-8">
          <h2 class="terms-h2">
            <span class="terms-section-num">10</span>
            Disclaimers
          </h2>
          <div class="terms-prose space-y-4">
            <p>
              <strong>THE SERVICE IS PROVIDED “AS IS” AND “AS AVAILABLE.”</strong> TO THE MAXIMUM EXTENT PERMITTED BY LAW,
              WE DISCLAIM ALL WARRANTIES, WHETHER EXPRESS, IMPLIED, OR STATUTORY, INCLUDING MERCHANTABILITY, FITNESS FOR
              A PARTICULAR PURPOSE, TITLE, AND NON-INFRINGEMENT. WE DO NOT WARRANT UNINTERRUPTED OR ERROR-FREE OPERATION,
              OR THAT DEFECTS WILL BE CORRECTED.
            </p>
            <p>
              Digital signage may be used in public and regulated environments; you are responsible for compliance with
              local laws, accessibility requirements, and industry rules applicable to your displays and content.
            </p>
          </div>
        </section>

        <!-- 11 -->
        <section class="terms-glass rounded-2xl p-6 sm:p-8">
          <h2 class="terms-h2">
            <span class="terms-section-num">11</span>
            Limitation of liability
          </h2>
          <div class="terms-prose space-y-4">
            <p>
              TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, IN NO EVENT WILL WE OR OUR AFFILIATES, LICENSORS, OR
              SUPPLIERS BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, EXEMPLARY, OR PUNITIVE DAMAGES,
              OR ANY LOSS OF PROFITS, REVENUE, GOODWILL, DATA, OR BUSINESS INTERRUPTION, EVEN IF ADVISED OF THE POSSIBILITY.
            </p>
            <p>
              OUR AGGREGATE LIABILITY ARISING OUT OF OR RELATED TO THE SERVICE OR THESE TERMS WILL NOT EXCEED THE GREATER
              OF (A) THE AMOUNTS YOU PAID US FOR THE SERVICE IN THE TWELVE (12) MONTHS BEFORE THE EVENT GIVING RISE TO THE
              CLAIM, OR (B) ONE HUNDRED U.S. DOLLARS (USD $100), IF YOU HAVE NOT HAD A PAYMENT OBLIGATION.
            </p>
            <p>
              Some jurisdictions do not allow certain limitations; in those cases our liability is limited to the fullest
              extent permitted by law. Nothing in these Terms limits liability that cannot be limited under mandatory law
              (including liability for gross negligence or willful misconduct, where applicable).
            </p>
          </div>
        </section>

        <!-- 12 -->
        <section class="terms-glass rounded-2xl p-6 sm:p-8">
          <h2 class="terms-h2">
            <span class="terms-section-num">12</span>
            Indemnity
          </h2>
          <div class="terms-prose space-y-4">
            <p>
              You will defend, indemnify, and hold harmless PixelCast and its affiliates, officers, directors,
              employees, and agents from any claims, damages, losses, and expenses (including reasonable attorneys’ fees)
              arising out of or related to Customer Content, your use of the Service in breach of these Terms, or your
              violation of applicable law or third-party rights.
            </p>
          </div>
        </section>

        <!-- 13 -->
        <section class="terms-glass rounded-2xl p-6 sm:p-8">
          <h2 class="terms-h2">
            <span class="terms-section-num">13</span>
            Suspension &amp; termination
          </h2>
          <div class="terms-prose space-y-4">
            <p>
              You may stop using the Service at any time. We may suspend or terminate access if you materially breach
              these Terms, if required by law, or to prevent harm to the Service or other customers. Provisions that by
              their nature should survive (including Sections 6–12, 14–18) will survive termination.
            </p>
            <p>
              Upon termination, your right to use the Service ceases. We may delete or retain Customer Content in
              accordance with our retention practices and the Privacy Policy, subject to applicable law.
            </p>
          </div>
        </section>

        <!-- 14 -->
        <section class="terms-glass rounded-2xl p-6 sm:p-8">
          <h2 class="terms-h2">
            <span class="terms-section-num">14</span>
            Privacy &amp; data
          </h2>
          <div class="terms-prose space-y-4">
            <p>
              Our collection and use of personal data is described in the
              <router-link class="terms-link" to="/privacy">Privacy Policy</router-link>. Where we process personal data on
              your behalf as a processor, any data processing terms required by law or contract may apply as set forth in
              your order or a separate data processing addendum, if provided.
            </p>
          </div>
        </section>

        <!-- 15 -->
        <section class="terms-glass rounded-2xl p-6 sm:p-8">
          <h2 class="terms-h2">
            <span class="terms-section-num">15</span>
            Changes to these Terms
          </h2>
          <div class="terms-prose space-y-4">
            <p>
              We may modify these Terms from time to time. We will post the updated Terms and update the “Last updated”
              date. Where required by law, we will provide additional notice (for example by email or in-product notice).
              Continued use after the effective date constitutes acceptance of the revised Terms, except where prohibited
              by law.
            </p>
          </div>
        </section>

        <!-- 16 -->
        <section class="terms-glass rounded-2xl p-6 sm:p-8">
          <h2 class="terms-h2">
            <span class="terms-section-num">16</span>
            Export, sanctions &amp; government use
          </h2>
          <div class="terms-prose space-y-4">
            <p>
              You represent that you are not located in a country subject to embargo or designated as prohibited, and
              that you are not on any government list of restricted parties. You will comply with applicable export and
              sanctions laws. If you are a U.S. government entity, additional restrictions may apply to commercial
              software documentation.
            </p>
          </div>
        </section>

        <!-- 17 -->
        <section class="terms-glass rounded-2xl p-6 sm:p-8">
          <h2 class="terms-h2">
            <span class="terms-section-num">17</span>
            Governing law &amp; disputes
          </h2>
          <div class="terms-prose space-y-4">
            <p>
              Unless mandatory consumer protection law in your country requires otherwise, these Terms are governed by the
              laws applicable to the PixelCast entity contracting with you, without regard to conflict-of-law rules.
            </p>
            <p>
              Courts in that jurisdiction will have exclusive jurisdiction over disputes, except that either party may
              seek injunctive relief in any court of competent jurisdiction to protect intellectual property or
              confidential information. If you are a consumer, you may have additional rights under local law.
            </p>
          </div>
        </section>

        <!-- 18 -->
        <section class="terms-glass rounded-2xl p-6 sm:p-8">
          <h2 class="terms-h2">
            <span class="terms-section-num">18</span>
            General
          </h2>
          <div class="terms-prose space-y-4">
            <p>
              <strong>Entire agreement.</strong> These Terms, together with the Privacy Policy and any order or
              subscription terms you accept, constitute the entire agreement regarding the Service.
            </p>
            <p>
              <strong>Assignment.</strong> You may not assign these Terms without our consent. We may assign in connection
              with a merger, acquisition, or sale of assets.
            </p>
            <p>
              <strong>Severability.</strong> If a provision is invalid, the remainder remains in effect.
            </p>
            <p>
              <strong>No waiver.</strong> Failure to enforce a provision is not a waiver.
            </p>
            <p>
              <strong>Force majeure.</strong> We are not liable for delays or failures due to events beyond our reasonable
              control.
            </p>
          </div>
        </section>

        <!-- 19 Contact -->
        <section
          class="rounded-2xl border border-cyan-400/20 bg-gradient-to-br from-slate-900/90 to-slate-950/95 p-6 shadow-[0_0_48px_rgba(34,211,238,0.08)] sm:p-8"
        >
          <h2 class="terms-h2 border-0 pb-0">
            <span class="terms-section-num border-cyan-400/35 bg-cyan-500/15 text-cyan-200">19</span>
            Contact
          </h2>
          <div class="terms-prose mt-4 space-y-4">
            <p>
              Questions about these Terms:
            </p>
            <ul class="space-y-2 text-sm">
              <li class="flex flex-wrap items-center gap-2">
                <EnvelopeIcon class="h-5 w-5 shrink-0 text-cyan-400/90" />
                <span class="text-white/70">Legal:</span>
                <a class="terms-link font-medium" href="mailto:legal@pixelcastsignage.com">legal@pixelcastsignage.com</a>
              </li>
              <li class="flex flex-wrap items-center gap-2">
                <EnvelopeIcon class="h-5 w-5 shrink-0 text-purple-400/90" />
                <span class="text-white/70">Support:</span>
                <a class="terms-link font-medium" href="mailto:support@pixelcastsignage.com">support@pixelcastsignage.com</a>
              </li>
            </ul>
            <p class="text-xs text-white/45">
              If you use a self-hosted deployment, your administrator may be the first point of contact for account and
              infrastructure questions.
            </p>
          </div>
        </section>
      </div>
    </main>

    <footer class="relative z-10 border-t border-white/10 bg-slate-950/60 py-8 backdrop-blur-md">
      <div class="mx-auto flex max-w-4xl flex-col items-center justify-between gap-4 px-4 text-center text-xs text-white/45 sm:flex-row sm:text-left sm:text-sm">
        <p>© {{ currentYear }} PixelCast. All rights reserved.</p>
        <div class="flex flex-wrap items-center justify-center gap-x-4 gap-y-2">
          <router-link class="hover:text-cyan-300" to="/privacy">Privacy</router-link>
          <span class="text-white/20" aria-hidden="true">·</span>
          <router-link class="hover:text-cyan-300" to="/terms">Terms</router-link>
          <span class="text-white/20" aria-hidden="true">·</span>
          <router-link class="hover:text-cyan-300" to="/data-center">Data Center</router-link>
          <span class="text-white/20" aria-hidden="true">·</span>
          <router-link class="hover:text-cyan-300" to="/docs">Docs</router-link>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import {
  ArrowLeftIcon,
  ClockIcon,
  DocumentTextIcon,
  EnvelopeIcon,
} from '@heroicons/vue/24/outline'

const authStore = useAuthStore()

const lastUpdated = ref('April 2, 2026')
const currentYear = ref(new Date().getFullYear())

const backRoute = computed(() => (authStore.isAuthenticated ? '/dashboard' : '/'))
const backText = computed(() => (authStore.isAuthenticated ? 'Back to Dashboard' : 'Back to Home'))

const serviceHighlights = [
  'Remote screen management, templates, schedules, and commands',
  'Player pairing and web player experiences where enabled',
  'User, role, and permission administration for your organization',
  'Operational logs, monitoring, and analytics features as offered in your plan',
]

const securityItems = [
  'Use strong passwords and protect authentication factors',
  'Promptly revoke access for departing personnel when applicable',
  'Notify us of suspected compromise of accounts or API credentials',
]

const prohibitedItems = [
  'Violate applicable laws, regulations, or third-party rights',
  'Upload or display unlawful, fraudulent, defamatory, harassing, or discriminatory content',
  'Distribute malware, exploit vulnerabilities, or disrupt the Service or third-party networks',
  'Attempt unauthorized access to accounts, systems, or data (including penetration testing without written approval)',
  'Mine cryptocurrency, send spam, or run bulk unsolicited communications through the Service',
  'Resell or redistribute the Service without authorization, or use the Service to build a competing offering',
  'Use automated means to access the Service in violation of our documentation or rate limits',
]

onMounted(() => {
  document.title = 'Terms of Service — PixelCast'

  let meta = document.querySelector('meta[name="description"]')
  if (!meta) {
    meta = document.createElement('meta')
    meta.setAttribute('name', 'description')
    document.head.appendChild(meta)
  }
  meta.setAttribute(
    'content',
    'PixelCast Terms of Service — rules for using our digital signage platform, subscriptions, and acceptable use.',
  )
})
</script>

<style scoped>
.terms-page {
  position: relative;
  overflow-x: hidden;
}

.terms-animated-bg {
  background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 25%, #0f172a 50%, #1e293b 75%, #0a0e27 100%);
  background-size: 400% 400%;
  animation: terms-gradient-shift 22s ease infinite;
}

.terms-starfield::before {
  content: '';
  position: fixed;
  inset: 0;
  background-image:
    radial-gradient(2px 2px at 20% 30%, rgba(255, 255, 255, 0.45), transparent),
    radial-gradient(2px 2px at 60% 70%, rgba(255, 255, 255, 0.35), transparent),
    radial-gradient(1px 1px at 50% 50%, rgba(255, 255, 255, 0.5), transparent),
    radial-gradient(1px 1px at 80% 10%, rgba(255, 255, 255, 0.4), transparent),
    radial-gradient(2px 2px at 30% 80%, rgba(255, 255, 255, 0.35), transparent);
  background-repeat: repeat;
  background-size: 200% 200%;
  animation: terms-star-drift 28s linear infinite;
  opacity: 0.55;
  pointer-events: none;
}

@keyframes terms-star-drift {
  from {
    transform: translateY(0);
  }
  to {
    transform: translateY(-1200px);
  }
}

@keyframes terms-gradient-shift {
  0%,
  100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

.safe-area-pt {
  padding-top: max(0.5rem, env(safe-area-inset-top));
}

.terms-glass {
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  box-shadow: 0 4px 32px rgba(0, 0, 0, 0.25);
}

.terms-h2 {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  font-size: 1.125rem;
  font-weight: 700;
  line-height: 1.35;
  color: rgb(248 250 252);
}

@media (min-width: 640px) {
  .terms-h2 {
    font-size: 1.25rem;
  }
}

.terms-section-num {
  display: inline-flex;
  height: 1.75rem;
  min-width: 1.75rem;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
  border: 1px solid rgba(34, 211, 238, 0.25);
  background: rgba(34, 211, 238, 0.1);
  font-size: 0.75rem;
  font-weight: 800;
  color: rgb(103 232 249);
}

.terms-prose p {
  font-size: 0.9375rem;
  line-height: 1.7;
  color: rgba(226, 232, 240, 0.92);
}

.terms-prose strong {
  color: rgb(248 250 252);
  font-weight: 600;
}

.terms-link {
  color: rgb(103 232 249);
  text-decoration: underline;
  text-underline-offset: 3px;
  transition: color 0.15s ease;
}

.terms-link:hover {
  color: rgb(167 243 208);
}

.terms-list {
  margin: 0.5rem 0 0;
  padding-left: 1.25rem;
  list-style: disc;
  color: rgba(226, 232, 240, 0.9);
  font-size: 0.9375rem;
  line-height: 1.65;
}

.terms-list li {
  margin-bottom: 0.5rem;
}

@media (prefers-reduced-motion: reduce) {
  .terms-starfield::before,
  .terms-animated-bg {
    animation: none !important;
  }
}
</style>
