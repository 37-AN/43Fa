<script setup lang="ts">
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
  } catch (err) {
    console.error('Login error:', err)
    error.value = 'Invalid credentials'
  }
}
</script>

<template>
  <main class="login">
    <h1>ShadowPlant AI</h1>
    <form @submit.prevent="submit">
      <input 
        v-model="username" 
        type="text"
        placeholder="Username" 
      />
      <input 
        v-model="password" 
        type="password"
        placeholder="Password" 
      />
      <button type="submit">Login</button>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </main>
</template>

<style scoped>
.login { 
  max-width: 360px; 
  margin: 80px auto; 
  display: grid; 
  gap: 12px;
  font-family: system-ui, sans-serif;
}

input { 
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

button { 
  padding: 10px;
  background: #333;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background: #555;
}

.error {
  color: red;
}
</style>
