<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import TopBar from '../components/TopBar.vue'
import KpiRow from '../components/KpiRow.vue'
import TrendChart from '../components/panels/TrendChart.vue'
import DowntimeHeatmap from '../components/panels/DowntimeHeatmap.vue'
import AnomaliesPanel from '../components/panels/AnomaliesPanel.vue'
import WorstMachinesPanel from '../components/panels/WorstMachinesPanel.vue'
import RiskPanel from '../components/panels/RiskPanel.vue'
import { useDashboardData } from '../composables/useDashboardData'
import { useFullscreen } from '../composables/useFullscreen'
import { useControlRoomMode } from '../composables/useControlRoomMode'

const {
  fromDate,
  toDate,
  selectedMachine,
  selectedShift,
  shiftOptions,
  kpi,
  machines,
  days,
  shifts,
  anomalies,
  riskPanel,
  machineOptions,
  loading,
  lastRefreshed,
  apiAlive,
  autoRefresh,
  refreshNow
} = useDashboardData()

const { isFullscreen, toggleFullscreen } = useFullscreen()
const { controlRoomMode } = useControlRoomMode()

const plantName = 'ShadowPlant Operations'

const onToggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
}

const onToggleControlRoom = () => {
  controlRoomMode.value = !controlRoomMode.value
}

const onUpdateShift = (value: string) => {
  selectedShift.value = value as any
}

const lastRefreshLabel = computed(() => {
  if (!lastRefreshed.value) return '—'
  return lastRefreshed.value.toLocaleString()
})

const handleKeydown = (event: KeyboardEvent) => {
  if (event.code === 'KeyR') {
    event.preventDefault()
    refreshNow()
  }
  if (event.code === 'F11') {
    event.preventDefault()
    toggleFullscreen()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <main class="dashboard">
    <TopBar
      :plant-name="plantName"
      :api-alive="apiAlive"
      :last-refreshed="lastRefreshed"
      :auto-refresh="autoRefresh"
      :selected-shift="selectedShift"
      :shift-options="shiftOptions"
      :loading="loading"
      :control-room-mode="controlRoomMode"
      :is-fullscreen="isFullscreen"
      @toggle-auto-refresh="onToggleAutoRefresh"
      @manual-refresh="refreshNow"
      @update-shift="onUpdateShift"
      @toggle-control-room="onToggleControlRoom"
      @toggle-fullscreen="toggleFullscreen"
    />

    <section class="filters">
      <label>
        From
        <input v-model="fromDate" type="date" />
      </label>
      <label>
        To
        <input v-model="toDate" type="date" />
      </label>
      <label>
        Machine
        <select v-model="selectedMachine">
          <option value="">All</option>
          <option v-for="machine in machineOptions" :key="machine" :value="machine">{{ machine }}</option>
        </select>
      </label>
      <div class="refresh-meta">
        <span>Last refresh:</span>
        <span class="mono">{{ lastRefreshLabel }}</span>
        <span v-if="loading" class="loading">Refreshing...</span>
      </div>
    </section>

    <KpiRow :kpi="kpi" />

    <section class="grid">
      <div class="panel-shell trend">
        <TrendChart :days="days" />
      </div>
      <div class="panel-shell anomalies">
        <AnomaliesPanel :anomalies="anomalies" />
      </div>
      <div class="panel-shell heatmap">
        <DowntimeHeatmap :shifts="shifts" :selected-shift="selectedShift" />
      </div>
      <div class="panel-shell worst">
        <WorstMachinesPanel :machines="machines" :shifts="shifts" :selected-shift="selectedShift" />
      </div>
      <div class="panel-shell risk">
        <RiskPanel :risk-panel="riskPanel" />
      </div>
    </section>
  </main>
</template>

<style scoped>
.dashboard {
  min-height: 100vh;
  padding: 18px 20px 24px;
  display: grid;
  gap: 16px;
}

.filters {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  align-items: end;
}

.filters label {
  display: grid;
  gap: 6px;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: var(--text-muted);
}

.filters input,
.filters select {
  background: var(--panel-bg);
  color: var(--text-strong);
  border: 1px solid var(--panel-border);
  padding: 8px 10px;
  border-radius: 2px;
}

.refresh-meta {
  display: grid;
  gap: 4px;
  font-size: 12px;
  color: var(--text-muted);
}

.loading {
  color: var(--accent-info);
  text-transform: uppercase;
  letter-spacing: 0.6px;
}

.mono {
  font-family: var(--font-mono);
}

.grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  grid-template-rows: minmax(320px, 1fr) minmax(300px, 1fr) minmax(250px, auto);
  gap: 16px;
  grid-template-areas:
    'trend anomalies'
    'heatmap worst'
    'risk risk';
}

.trend {
  grid-area: trend;
}

.anomalies {
  grid-area: anomalies;
}

.heatmap {
  grid-area: heatmap;
}

.worst {
  grid-area: worst;
}
.risk {
  grid-area: risk;
}

.panel-shell {
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  padding: 14px;
  border-radius: 2px;
  overflow: hidden;
}

@media (max-width: 1200px) {
  .filters {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .grid {
    grid-template-columns: 1fr;
    grid-template-rows: repeat(5, minmax(280px, auto));
    grid-template-areas:
      'trend'
      'heatmap'
      'anomalies'
      'worst'
      'risk';
  }
}
</style>
