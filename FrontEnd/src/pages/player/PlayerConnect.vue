<template>
  <div class="redirect-screen">
    <p>Redirecting to player...</p>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const router = useRouter()
const route = useRoute()

onMounted(() => {
  const screenId = route.query.screenId || route.query.screen_id || route.params.screenId
  if (screenId) {
    router.replace(`/player/${screenId}`)
    return
  }
  router.replace('/player/connect')
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
