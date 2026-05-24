<template>
  <div class="brand-logo" :class="{ 'brand-logo--with-text': showText }">
    <img
      :src="logoSrc"
      :alt="alt"
      class="brand-logo__mark"
      :width="size"
      :height="size"
      decoding="async"
    />
    <span v-if="showText" class="brand-logo__text">{{ text }}</span>
  </div>
</template>

<script setup>
defineProps({
  size: {
    type: [Number, String],
    default: 40,
  },
  showText: {
    type: Boolean,
    default: false,
  },
  text: {
    type: String,
    default: 'PixelCast Signage',
  },
  alt: {
    type: String,
    default: 'PixelCast Signage',
  },
  logoSrc: {
    type: String,
    default: '/favicon.svg',
  },
})
</script>

<style scoped>
.brand-logo {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 0;
}

.brand-logo__mark {
  display: block;
  flex-shrink: 0;
  border-radius: 10px;
  object-fit: contain;
}

.brand-logo__text {
  font-size: 1.125rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  color: var(--text-main);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dark .brand-logo__text {
  background: linear-gradient(135deg, #06b6d4, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
</style>
