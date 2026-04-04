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
          to="/terms"
          class="hidden text-xs font-medium text-white/55 hover:text-cyan-300 sm:inline sm:text-sm"
        >
          Terms of Service
        </router-link>
      </div>
    </header>

    <main class="relative z-10 mx-auto max-w-4xl px-4 pb-20 pt-10 sm:px-6 lg:px-8">
      <div class="mb-12 text-center sm:mb-14">
        <div
          class="mx-auto mb-6 inline-flex h-16 w-16 items-center justify-center rounded-2xl border border-cyan-400/25 bg-gradient-to-br from-cyan-500/20 to-purple-600/25 shadow-[0_0_40px_rgba(34,211,238,0.15)]"
        >
          <ShieldCheckIcon class="h-8 w-8 text-cyan-300" />
        </div>
        <p class="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-cyan-400/90">
          Privacy &amp; data
        </p>
        <h1 class="mb-4 text-3xl font-bold tracking-tight text-white sm:text-4xl md:text-5xl">
          <span
            class="bg-gradient-to-r from-cyan-300 via-blue-300 to-purple-400 bg-clip-text text-transparent"
          >
            Privacy Policy
          </span>
        </h1>
        <p class="flex flex-wrap items-center justify-center gap-2 text-sm text-white/55">
          <ClockIcon class="h-4 w-4 text-cyan-400/80" />
          <span>Last updated <strong class="font-semibold text-white/80">{{ lastUpdated }}</strong></span>
        </p>
        <p class="mx-auto mt-4 max-w-2xl text-sm leading-relaxed text-slate-400">
          This Privacy Policy describes how PixelCast collects, uses, discloses, and protects personal data when you use
          our digital signage platform and related services (the “Service”). Please read it alongside our
          <router-link class="terms-link" to="/terms">Terms of Service</router-link>.
        </p>
      </div>

      <div class="space-y-8 md:space-y-10">
        <!-- 1 -->
        <section class="terms-glass rounded-2xl p-6 sm:p-8">
          <h2 class="terms-h2">
            <span class="terms-section-num">1</span>
            Scope &amp; agreement
          </h2>
          <div class="terms-prose space-y-4">
            <p>
              This Privacy Policy (“<strong>Policy</strong>”) applies to personal data processed by the operator of the
              PixelCast platform (“<strong>PixelCast</strong>,” “<strong>we</strong>,” “<strong>us</strong>,” or
              “<strong>our</strong>”) in connection with websites, applications, APIs, and services we offer (collectively,
              the “<strong>Service</strong>”).
            </p>
            <p>
              By creating an account, accessing, or using the Service, you acknowledge this Policy. If you use the Service
              on behalf of an organization, you represent that you are authorized to bind that organization. Our
              <router-link class="terms-link" to="/terms">Terms of Service</router-link> govern use of the Service and
              should be read together with this Policy.
            </p>
            <p>
              If you do not agree with this Policy, do not use the Service. We may update this Policy as described in
              Section 13.
            </p>
          </div>
        </section>

        <!-- 2 -->
        <section class="terms-glass rounded-2xl p-6 sm:p-8">
          <h2 class="terms-h2">
            <span class="terms-section-num">2</span>
            Personal data we collect
          </h2>
          <div class="terms-prose space-y-4">
            <p>
              Depending on how you use the Service, we may collect the categories below. Not all categories apply to
              every customer or deployment (for example self-hosted installations may process data differently).
            </p>
            <p><strong>Account and identity.</strong> Information you provide when registering or administering users,
              such as name, email address, organization name, role, and credentials. We process authentication data
              (for example hashed passwords and session tokens) as needed to secure access.</p>
            <p><strong>Usage and technical data.</strong> Information about how the Service is accessed and used, such
              as IP address, device and browser type, approximate location derived from IP, access times, pages or
              features viewed, and diagnostic or performance data.</p>
            <p><strong>Operational and audit logs.</strong> Records relating to signage operations where the Service
              provides them, such as commands to players, execution status, content download activity, screen online or
              offline status, and security or audit events tied to your workspace.</p>
            <p><strong>Content and configuration.</strong> Media files, templates, schedules, recurrence rules, and
              related metadata that you upload or configure for display on your screens.</p>
            <p><strong>Support and communications.</strong> Information you send when contacting us (for example email
              content) and records of those interactions where we keep them for support or compliance.</p>
            <p><strong>Billing (where applicable).</strong> For paid offerings, our payment providers may collect
              billing details, payment method information, and transaction history subject to their own terms and privacy
              notices.</p>
          </div>
        </section>

        <!-- 3 -->
        <section class="terms-glass rounded-2xl p-6 sm:p-8">
          <h2 class="terms-h2">
            <span class="terms-section-num">3</span>
            How we use personal data
          </h2>
          <div class="terms-prose space-y-4">
            <p>We use personal data for purposes such as:</p>
            <ul class="terms-list">
              <li v-for="(item, i) in usagePurposes" :key="i">{{ item }}</li>
            </ul>
            <p>
              We do not sell your personal data. We may use aggregated or de-identified information that does not
              identify you for analytics, product improvement, or reporting where permitted by law.
            </p>
          </div>
        </section>

        <!-- 4 -->
        <section class="terms-glass rounded-2xl p-6 sm:p-8">
          <h2 class="terms-h2">
            <span class="terms-section-num">4</span>
            Legal bases (where applicable)
          </h2>
          <div class="terms-prose space-y-4">
            <p>
              Where laws such as the GDPR or UK GDPR apply, we rely on one or more of the following legal bases, as
              appropriate: performance of a contract with you; legitimate interests that are not overridden by your
              rights (for example securing the Service, preventing abuse, and improving reliability); consent where we
              request it (for example certain cookies or optional communications); compliance with legal obligations;
              and, in limited cases, protection of vital interests.
            </p>
            <p>
              This summary is for transparency and is not legal advice. If you have questions about the basis for a
              specific processing activity, contact us using Section 14.
            </p>
          </div>
        </section>

        <!-- 5 -->
        <section class="terms-glass rounded-2xl p-6 sm:p-8">
          <h2 class="terms-h2">
            <span class="terms-section-num">5</span>
            Sharing &amp; disclosure
          </h2>
          <div class="terms-prose space-y-4">
            <p>We may disclose personal data in the following circumstances:</p>
            <ul class="terms-list">
              <li v-for="(item, i) in sharingItems" :key="i">{{ item }}</li>
            </ul>
            <p>
              We require service providers to protect personal data appropriately and to use it only for the purposes we
              specify, subject to their agreements and applicable law.
            </p>
          </div>
        </section>

        <!-- 6 -->
        <section class="terms-glass rounded-2xl p-6 sm:p-8">
          <h2 class="terms-h2">
            <span class="terms-section-num">6</span>
            International transfers
          </h2>
          <div class="terms-prose space-y-4">
            <p>
              We may process and store personal data in countries other than where you live, including where we or our
              service providers operate facilities. When we transfer personal data from the European Economic Area, United
              Kingdom, or Switzerland to other countries, we use appropriate safeguards where required by law, such as
              standard contractual clauses approved by regulators or other lawful transfer mechanisms.
            </p>
          </div>
        </section>

        <!-- 7 -->
        <section class="terms-glass rounded-2xl p-6 sm:p-8">
          <h2 class="terms-h2">
            <span class="terms-section-num">7</span>
            Retention
          </h2>
          <div class="terms-prose space-y-4">
            <p>
              We retain personal data for as long as necessary to provide the Service, comply with legal obligations,
              resolve disputes, and enforce our agreements. Retention periods vary depending on data type, legal
              requirements, and whether you still have an active account. When data is no longer needed, we delete or
              de-identify it in accordance with our retention practices, subject to backup and disaster-recovery
              constraints.
            </p>
          </div>
        </section>

        <!-- 8 -->
        <section class="terms-glass rounded-2xl p-6 sm:p-8">
          <h2 class="terms-h2">
            <span class="terms-section-num">8</span>
            Security
          </h2>
          <div class="terms-prose space-y-4">
            <p>
              We implement technical and organizational measures designed to protect personal data against unauthorized
              access, loss, or alteration. Examples include:
            </p>
            <ul class="terms-list">
              <li v-for="(m, i) in securityMeasures" :key="i">
                <strong>{{ m.title }}.</strong> {{ m.description }}
              </li>
            </ul>
            <p>
              No method of transmission or storage is completely secure. If we become aware of a breach affecting your
              personal data where notification is required by law, we will follow applicable notification requirements.
            </p>
          </div>
        </section>

        <!-- 9 -->
        <section class="terms-glass rounded-2xl p-6 sm:p-8">
          <h2 class="terms-h2">
            <span class="terms-section-num">9</span>
            Your privacy rights
          </h2>
          <div class="terms-prose space-y-4">
            <p>
              Depending on your location, you may have rights regarding your personal data, which can include requesting
              access, correction, deletion, restriction of processing, objection to certain processing, data portability,
              and withdrawal of consent where processing is based on consent.
            </p>
            <p>
              You may also have the right to lodge a complaint with a supervisory authority in your country or region.
              To exercise rights that apply to you, contact us using Section 14. We may need to verify your identity
              before fulfilling certain requests.
            </p>
            <p>
              If you are a California resident, additional disclosures or rights may apply under applicable U.S. state
              privacy laws; contact us for more information about requests we honor in your jurisdiction.
            </p>
          </div>
        </section>

        <!-- 10 -->
        <section class="terms-glass rounded-2xl p-6 sm:p-8">
          <h2 class="terms-h2">
            <span class="terms-section-num">10</span>
            Cookies &amp; similar technologies
          </h2>
          <div class="terms-prose space-y-4">
            <p>
              We and our partners may use cookies, local storage, and similar technologies to operate the Service,
              maintain sessions, remember preferences, protect against fraud, and understand usage. Some technologies are
              strictly necessary; others may be optional depending on your choices and regional requirements.
            </p>
            <p>
              You can control cookies through your browser settings. Blocking certain cookies may affect functionality of
              the Service (for example staying signed in). Where required, we will obtain consent before using
              non-essential cookies or similar technologies.
            </p>
          </div>
        </section>

        <!-- 11 -->
        <section class="terms-glass rounded-2xl p-6 sm:p-8">
          <h2 class="terms-h2">
            <span class="terms-section-num">11</span>
            Children’s privacy
          </h2>
          <div class="terms-prose space-y-4">
            <p>
              The Service is not directed to children under 16 (or the minimum age required in your jurisdiction), and
              we do not knowingly collect personal data from children for marketing purposes. If you believe we have
              collected information from a child inappropriately, please contact us and we will take appropriate steps.
            </p>
          </div>
        </section>

        <!-- 12 -->
        <section class="terms-glass rounded-2xl p-6 sm:p-8">
          <h2 class="terms-h2">
            <span class="terms-section-num">12</span>
            Third-party links &amp; services
          </h2>
          <div class="terms-prose space-y-4">
            <p>
              The Service may link to or integrate with third-party websites, identity providers, payment processors, or
              infrastructure services. Those third parties process information under their own privacy policies. We are not
              responsible for their practices, content, or security.
            </p>
          </div>
        </section>

        <!-- 13 -->
        <section class="terms-glass rounded-2xl p-6 sm:p-8">
          <h2 class="terms-h2">
            <span class="terms-section-num">13</span>
            Changes to this Policy
          </h2>
          <div class="terms-prose space-y-4">
            <p>
              We may update this Policy from time to time. We will post the revised Policy on this page and update the
              “Last updated” date. Where required by law, we will provide additional notice (for example by email or
              in-product notification). Continued use of the Service after the effective date constitutes acceptance of
              the revised Policy where permitted by law.
            </p>
          </div>
        </section>

        <!-- 14 Contact -->
        <section
          class="rounded-2xl border border-cyan-400/20 bg-gradient-to-br from-slate-900/90 to-slate-950/95 p-6 shadow-[0_0_48px_rgba(34,211,238,0.08)] sm:p-8"
        >
          <h2 class="terms-h2 border-0 pb-0">
            <span class="terms-section-num border-cyan-400/35 bg-cyan-500/15 text-cyan-200">14</span>
            Contact
          </h2>
          <div class="terms-prose mt-4 space-y-4">
            <p>
              Questions about this Privacy Policy or requests regarding personal data:
            </p>
            <ul class="space-y-2 text-sm">
              <li class="flex flex-wrap items-center gap-2">
                <EnvelopeIcon class="h-5 w-5 shrink-0 text-cyan-400/90" />
                <span class="text-white/70">Privacy:</span>
                <a class="terms-link font-medium" href="mailto:privacy@pixelcastsignage.com">privacy@pixelcastsignage.com</a>
              </li>
              <li class="flex flex-wrap items-center gap-2">
                <EnvelopeIcon class="h-5 w-5 shrink-0 text-purple-400/90" />
                <span class="text-white/70">Legal:</span>
                <a class="terms-link font-medium" href="mailto:legal@pixelcastsignage.com">legal@pixelcastsignage.com</a>
              </li>
              <li class="flex flex-wrap items-center gap-2">
                <EnvelopeIcon class="h-5 w-5 shrink-0 text-cyan-400/80" />
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
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import {
  ArrowLeftIcon,
  ClockIcon,
  ShieldCheckIcon,
  EnvelopeIcon,
} from '@heroicons/vue/24/outline'

const authStore = useAuthStore()

const lastUpdated = ref('April 2, 2026')
const currentYear = ref(new Date().getFullYear())

const backRoute = computed(() => (authStore.isAuthenticated ? '/dashboard' : '/'))
const backText = computed(() => (authStore.isAuthenticated ? 'Back to Dashboard' : 'Back to Home'))

const usagePurposes = [
  'Providing, operating, and improving the Service, including screens, templates, schedules, pairing, and user administration features',
  'Authenticating users, enforcing roles and permissions, and protecting accounts',
  'Detecting, preventing, and responding to fraud, abuse, and security incidents',
  'Communicating with you about the Service, including service and security notices',
  'Analyzing usage in aggregate to understand performance and inform product decisions',
  'Complying with legal obligations and responding to lawful requests',
  'Supporting you when you contact us and resolving technical issues',
]

const sharingItems = [
  'With vendors and service providers who assist us (for example hosting, analytics, email delivery, security, or customer support), subject to contracts and confidentiality obligations',
  'With payment processors when you purchase paid offerings; their use of payment data is governed by their terms',
  'When required by law, regulation, legal process, or governmental request, or to protect the rights, safety, and security of PixelCast, our users, or the public',
  'In connection with a merger, acquisition, financing, or sale of assets, subject to appropriate safeguards and notices where required',
  'With your direction or consent, including when you integrate third-party services you choose to enable',
]

const securityMeasures = [
  { title: 'Encryption', description: 'TLS for data in transit and encryption for stored data where appropriate' },
  { title: 'Access controls', description: 'Role-based access and least-privilege principles for our systems' },
  { title: 'Authentication', description: 'Secure credential handling and optional strong authentication where offered' },
  { title: 'Monitoring', description: 'Logging and monitoring to detect and respond to incidents' },
  { title: 'Backups', description: 'Backup and recovery practices designed to support business continuity' },
]
</script>
