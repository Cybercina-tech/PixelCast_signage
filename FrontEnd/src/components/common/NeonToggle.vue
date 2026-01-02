<template>
  <button
    :class="['neon-toggle', { 'neon-toggle-active': modelValue }]"
    @click="toggle"
    type="button"
    role="switch"
    :aria-checked="modelValue"
  >
    <span class="neon-toggle-track">
      <span class="neon-toggle-thumb"></span>
    </span>
  </button>
</template>

<script setup>
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue'])

const toggle = () => {
  emit('update:modelValue', !props.modelValue)
}
</script>

<style scoped>
.neon-toggle {
  position: relative;
  width: 52px;
  height: 28px;
  padding: 0;
  background: transparent;
  border: none;
  cursor: pointer;
  outline: none;
  transition: all 0.3s ease;
}

.neon-toggle-track {
  position: relative;
  width: 100%;
  height: 100%;
  background: #DFE6E9; /* Silver Grey when OFF */
  border: 1px solid #C4D1D6;
  border-radius: 14px;
  transition: all 0.3s ease;
}

.neon-toggle-thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 22px;
  height: 22px;
  background: #FFFFFF;
  border-radius: 50%;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  /* Tiny 3D shadow */
  box-shadow: 
    0 2px 4px rgba(0, 0, 0, 0.15),
    0 1px 2px rgba(0, 0, 0, 0.1),
    inset 0 -1px 1px rgba(0, 0, 0, 0.05);
}

/* When ON - Professional Blue */
.neon-toggle-active .neon-toggle-track {
  background: #0984E3; /* Professional Blue */
  border-color: #0871C2;
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.1);
}

.neon-toggle-active .neon-toggle-thumb {
  transform: translateX(24px);
  background: #FFFFFF;
  /* Enhanced 3D shadow when active */
  box-shadow: 
    0 3px 6px rgba(0, 0, 0, 0.2),
    0 1px 3px rgba(0, 0, 0, 0.15),
    inset 0 -1px 2px rgba(0, 0, 0, 0.1);
}

.neon-toggle:hover .neon-toggle-track {
  border-color: #B8C5CA;
}

.neon-toggle-active:hover .neon-toggle-track {
  background: #0871C2; /* Slightly darker blue on hover */
  border-color: #065A9E;
}

.neon-toggle:focus-visible {
  outline: 2px solid #0984E3;
  outline-offset: 2px;
}

/* Dark Mode Styles */
.dark .neon-toggle-track {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.dark .neon-toggle-thumb {
  background: rgba(255, 255, 255, 0.3);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.dark .neon-toggle-active .neon-toggle-track {
  background: rgba(6, 182, 212, 0.2);
  border-color: #06b6d4;
  box-shadow: 0 0 20px rgba(6, 182, 212, 0.4), inset 0 0 20px rgba(6, 182, 212, 0.1);
}

.dark .neon-toggle-active .neon-toggle-thumb {
  background: #06b6d4;
  box-shadow: 0 0 15px rgba(6, 182, 212, 0.8), 0 2px 8px rgba(0, 0, 0, 0.3);
}

.dark .neon-toggle:hover .neon-toggle-track {
  border-color: rgba(255, 255, 255, 0.3);
}

.dark .neon-toggle-active:hover .neon-toggle-track {
  border-color: #00d2ff;
  box-shadow: 0 0 25px rgba(6, 182, 212, 0.5), inset 0 0 25px rgba(6, 182, 212, 0.15);
}

.dark .neon-toggle:focus-visible {
  outline: 2px solid #06b6d4;
}
</style>

