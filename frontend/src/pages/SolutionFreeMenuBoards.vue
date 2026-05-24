<template>
  <SolutionPageLayout>
    <section class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-14 sm:py-16">
      <router-link to="/" class="solution-back-btn">
        <span aria-hidden="true">←</span>
        Back to home
      </router-link>
      <p class="solution-kicker">Restaurant Solution</p>
      <h1 class="solution-title">Free digital signage for menu boards</h1>
      <p class="solution-lead">
        PixelCast gives restaurants and cafes a practical starting point for digital menu boards. Launch quickly on
        browser-based screens, schedule dayparts, and keep pricing or promotions synchronized across all branches.
      </p>
      <div class="mt-8 flex flex-wrap gap-3">
        <router-link to="/signup" class="solution-cta-primary">Start free menu boards</router-link>
        <router-link to="/pricing" class="solution-cta-secondary">View paid scaling plans</router-link>
      </div>
    </section>

    <section class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pb-16 space-y-8">
      <article class="solution-card">
        <h2 class="solution-card-title">Built for food and beverage teams</h2>
        <ul>
          <li>Daypart scheduling for breakfast, lunch, and dinner menus.</li>
          <li>Fast price or promotion updates for limited-time and seasonal campaigns.</li>
          <li>Template reuse across single stores, chains, and franchise operations.</li>
          <li>Central quality control while each branch keeps local operational flexibility.</li>
        </ul>
      </article>
      <article class="solution-card">
        <h2 class="solution-card-title">Menu board workflow in PixelCast</h2>
        <ol>
          <li>Pair screens in the player flow and assign each display to a branch.</li>
          <li>Create menu templates and upload approved product media.</li>
          <li>Schedule breakfast, lunch, and dinner blocks with location-level targeting.</li>
          <li>Use monitoring and logs to verify content delivery and playback stability.</li>
        </ol>
      </article>
      <article class="solution-card">
        <h2 class="solution-card-title">Recommended next step</h2>
        <p class="solution-body-text">
          Pair one pilot screen first, publish a validated menu template, then scale to additional branches with the
          same workflow and centralized controls.
        </p>
      </article>
      <div class="solution-links-row pb-2">
        <router-link class="solution-inline-link" to="/guides/turn-smart-tv-into-digital-signboard">
          Smart TV menu board guide
        </router-link>
        <router-link class="solution-inline-link" to="/blog">Restaurant signage articles</router-link>
      </div>
    </section>
  </SolutionPageLayout>
</template>

<script setup>
import SolutionPageLayout from '@/components/landing/SolutionPageLayout.vue'
</script>
