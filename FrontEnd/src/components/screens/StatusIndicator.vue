<template>
  <div class="flex items-center gap-2">
    <div
      :class="[
        'w-3 h-3 rounded-full',
        statusClasses[status] || statusClasses.offline,
        status === 'online' ? 'animate-pulse' : ''
      ]"
    ></div>
    <span
      :class="[
        'text-xs font-medium',
        textClasses[status] || textClasses.offline
      ]"
    >
      {{ statusText[status] || 'Offline' }}
    </span>
  </div>
</template>

<script setup>
const props = defineProps({
  status: {
    type: String,
    required: true,
    validator: (value) => ['online', 'offline', 'connecting'].includes(value),
  },
})

const statusClasses = {
  online: 'bg-emerald-400',
  offline: 'bg-red-400',
  connecting: 'bg-yellow-400 animate-pulse',
}

const textClasses = {
  online: 'text-emerald-400',
  offline: 'text-red-400',
  connecting: 'text-yellow-400',
}

const statusText = {
  online: 'Online',
  offline: 'Offline',
  connecting: 'Connecting...',
}
</script>

