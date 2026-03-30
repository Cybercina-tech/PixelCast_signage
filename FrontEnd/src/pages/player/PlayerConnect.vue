<template>
  <div class="redirect-screen">
    <p>Redirecting to player...</p>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

onMounted(() => {
  router.replace('/player')
})
</script>

<style scoped>
.redirect-screen {
  position: fixed;
  inset: 0;
  background: #000;
  color: #666;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: sans-serif;
}
</style>
