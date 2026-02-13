<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

onMounted(async () => {
  await router.replace('/')
})
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api, { setToken } from '../api/client'

const router = useRouter()
const username = ref('admin')
const password = ref('admin123')
const error = ref('')

const submit = async () => {
  error.value = ''
  try {
    const { data } = await api.post('/auth/login', { username: username.value, password: password.value })
    localStorage.setItem('token', data.access_token)
    setToken(data.access_token)
    await router.push('/dashboard')
  } catch {
    error.value = 'Invalid credentials'
  }
}
</script>

<template>
  <main class="login">
    <h1>ShadowPlant AI</h1>
    <p>Login has been removed in MVP demo mode. Redirecting to dashboard…</p>
    <input v-model="username" placeholder="Username" />
    <input v-model="password" placeholder="Password" type="password" />
    <button @click="submit">Login</button>
    <p v-if="error">{{ error }}</p>
  </main>
</template>

<style scoped>
.login { max-width: 560px; margin: 80px auto; display: grid; gap: 12px; }
.login { max-width: 360px; margin: 80px auto; display: grid; gap: 12px; }
button { padding: 10px; }
</style>
