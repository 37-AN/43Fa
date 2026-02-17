<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  plantName: string
  apiAlive: boolean
  lastRefreshed: Date | null
  autoRefresh: boolean
  selectedShift: string
  shiftOptions: string[]
  loading: boolean
  controlRoomMode: boolean
  isFullscreen: boolean
}>()

const emit = defineEmits<{
  (e: 'toggle-auto-refresh'): void
  (e: 'manual-refresh'): void
  (e: 'update-shift', value: string): void
  (e: 'toggle-control-room'): void
  (e: 'toggle-fullscreen'): void
}>()

const lastRefreshLabel = computed(() => {
  if (!props.lastRefreshed) return '—'
  return props.lastRefreshed.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
})
</script>

<template>
  <header class="top-bar">
    <div class="brand">
      <div class="plant-name">{{ plantName }}</div>
      <div class="status">
        <span class="status-dot" :class="apiAlive ? 'status-ok' : 'status-down'"></span>
        <span class="status-text">{{ apiAlive ? 'API LIVE' : 'API DOWN' }}</span>
      </div>
    </div>

    <div class="status-meta">
      <div class="meta-block">
        <div class="meta-label">Last Refresh</div>
        <div class="meta-value">{{ lastRefreshLabel }}</div>
      </div>
      <div class="meta-block live-indicator" :class="loading ? 'live-loading' : ''">
        <div class="meta-label">Live</div>
        <div class="meta-value">
          <span class="live-dot" :class="autoRefresh ? 'live-on' : 'live-off'"></span>
          {{ autoRefresh ? 'AUTO' : 'MANUAL' }}
        </div>
      </div>
      <button class="btn" type="button" @click="emit('manual-refresh')">Refresh</button>
      <label class="toggle">
        <input type="checkbox" :checked="autoRefresh" @change="emit('toggle-auto-refresh')" />
        <span>Auto-Refresh</span>
      </label>
    </div>

    <div class="controls">
      <label class="select">
        <span>Shift</span>
        <select :value="selectedShift" @change="emit('update-shift', ($event.target as HTMLSelectElement).value)">
          <option v-for="shift in shiftOptions" :key="shift" :value="shift">{{ shift }}</option>
        </select>
      </label>
      <button class="btn" type="button" @click="emit('toggle-control-room')">
        {{ controlRoomMode ? 'Exit Control Room' : 'Control Room Mode' }}
      </button>
      <button class="btn" type="button" @click="emit('toggle-fullscreen')">
        {{ isFullscreen ? 'Exit Full Screen' : 'Full Screen' }}
      </button>
    </div>
  </header>
</template>

<style scoped>
.top-bar {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 16px;
  align-items: center;
  padding: 16px 20px;
  border: 1px solid var(--panel-border);
  background: var(--panel-bg);
}
.brand {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.plant-name {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.6px;
}
.status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 1px;
}
.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 2px;
  border: 1px solid var(--panel-border);
}
.status-ok {
  background: var(--accent-normal);
}
.status-down {
  background: var(--accent-critical);
}
.status-meta {
  display: flex;
  align-items: center;
  gap: 16px;
}
.meta-block {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.meta-label {
  font-size: 11px;
  color: var(--text-muted);
  letter-spacing: 0.8px;
  text-transform: uppercase;
}
.meta-value {
  font-size: 14px;
  font-weight: 600;
}
.live-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 1px;
  margin-right: 6px;
  border: 1px solid var(--panel-border);
}
.live-on {
  background: var(--accent-info);
}
.live-off {
  background: #2a3342;
}
.live-loading .meta-value {
  color: var(--accent-info);
}
.controls {
  display: flex;
  align-items: center;
  gap: 10px;
}
.select {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.7px;
}
.select select {
  background: var(--panel-bg);
  color: var(--text-strong);
  border: 1px solid var(--panel-border);
  padding: 6px 10px;
  border-radius: 2px;
}
.toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.7px;
}
.toggle input {
  accent-color: var(--accent-info);
}
.btn {
  background: transparent;
  color: var(--text-strong);
  border: 1px solid var(--panel-border);
  padding: 8px 12px;
  border-radius: 2px;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.7px;
}
.btn:hover {
  border-color: var(--accent-info);
}
</style>
