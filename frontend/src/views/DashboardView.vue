<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import api, { setToken } from '../api/client'
import KpiCards from '../components/KpiCards.vue'

const today = new Date().toISOString().slice(0, 10)
const kpi = ref<any>(null)
const machines = ref<any[]>([])
const anomalies = ref<any[]>([])
const fromDate = ref(today)
const toDate = ref(today)
const selectedMachine = ref('')
const machineOptions = ref<string[]>([])
const loading = ref(false)

const chartOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    formatter: (params: any[]) =>
      params
        .map((p) => `${p.seriesName}: ${Number(p.value).toLocaleString(undefined, { maximumFractionDigits: 2 })}`)
        .join('<br/>')
  },
  legend: { data: ['Output', 'Downtime'] },
  xAxis: { type: 'category', data: machines.value.map((m) => m.date) },
  yAxis: [{ type: 'value', name: 'Throughput' }, { type: 'value', name: 'Downtime' }],
  series: [
    { name: 'Output', type: 'line', yAxisIndex: 0, data: machines.value.map((m) => m.throughput_units) },
    { name: 'Downtime', type: 'line', yAxisIndex: 1, data: machines.value.map((m) => m.downtime_minutes) }
  ]
}))

const loadData = async () => {
  loading.value = true

  const token = localStorage.getItem('token')
  if (token) {
    setToken(token)
  }

  const kpiRes = await api.get('/kpi/overview', { params: { date: toDate.value } })
  kpi.value = kpiRes.data

  const machineRes = await api.get('/kpi/machines', {
    params: { from: fromDate.value, to: toDate.value, machine_id: selectedMachine.value || undefined }
  })
  machines.value = machineRes.data
  machineOptions.value = Array.from(new Set<string>(machineRes.data.map((m: any) => String(m.machine_id))))

  const anomalyRes = await api.get('/anomalies', { params: { from: fromDate.value, to: toDate.value } })
  anomalies.value = anomalyRes.data

  loading.value = false
}

onMounted(loadData)
watch([fromDate, toDate, selectedMachine], loadData)
</script>

<template>
  <main class="dash">
    <h1>Factory Dashboard</h1>
    <section class="filters">
      <label>From <input v-model="fromDate" type="date" /></label>
      <label>To <input v-model="toDate" type="date" /></label>
      <label>Machine
        <select v-model="selectedMachine">
          <option value="">All</option>
          <option v-for="machine in machineOptions" :key="machine" :value="machine">{{ machine }}</option>
        </select>
      </label>
    </section>
    <KpiCards :kpi="kpi" />
    <p v-if="loading">Loading...</p>
    <section class="grid">
      <v-chart class="chart" :option="chartOption" autoresize />
      <div>
        <h3>Worst Machines (by downtime)</h3>
        <table>
          <thead>
            <tr><th>Machine</th><th>Downtime</th><th>Output</th></tr>
          </thead>
          <tbody>
            <tr v-for="m in [...machines].sort((a,b)=>b.downtime_minutes-a.downtime_minutes).slice(0,5)" :key="m.machine_id + m.date">
              <td>{{ m.machine_id }}</td><td>{{ m.downtime_minutes.toFixed(1) }}</td><td>{{ m.throughput_units.toFixed(1) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
    <section>
      <h3>Anomalies</h3>
      <ul><li v-for="a in anomalies" :key="a.machine_code + a.metric">{{ a.report_date }} | {{ a.machine_code }} | {{ a.metric }} | {{ a.severity }} | {{ a.insight }}</li></ul>
    </section>
  </main>
</template>

<style scoped>
.dash { padding: 20px; display: grid; gap: 16px; }
.grid { display: grid; grid-template-columns: 2fr 1fr; gap: 14px; }
.filters { display: flex; gap: 12px; flex-wrap: wrap; }
.chart { height: 340px; }
table { width: 100%; }
@media (max-width: 900px) { .grid { grid-template-columns: 1fr; } }
</style>
