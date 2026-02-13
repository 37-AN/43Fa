<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

onMounted(async () => {
  await router.replace('/')
})
</script>

<template>
  <main class="login">
    <h1>ShadowPlant AI</h1>
    <p>Login has been removed in MVP demo mode. Redirecting to dashboard…</p>
  </main>
</template>

<style scoped>
.login { max-width: 560px; margin: 80px auto; display: grid; gap: 12px; }
</style>
