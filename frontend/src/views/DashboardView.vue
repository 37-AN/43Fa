<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import VChart from 'vue-echarts'
import api, { setToken } from '../api/client'
import KpiCards from '../components/KpiCards.vue'

const today = new Date().toISOString().slice(0, 10)
const kpi = ref<any>(null)
const machines = ref<any[]>([])
const anomalies = ref<any[]>([])

const chartOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { data: ['Output', 'Downtime'] },
  xAxis: { type: 'category', data: machines.value.map((m) => `${m.report_date}-${m.machine_id}`) },
  yAxis: { type: 'value' },
  series: [
    { name: 'Output', type: 'line', data: machines.value.map((m) => m.output) },
    { name: 'Downtime', type: 'line', data: machines.value.map((m) => m.downtime) }
  ]
}))

onMounted(async () => {
  const token = localStorage.getItem('token')
  if (token) {
    setToken(token)
  }

  const kpiRes = await api.get('/kpi/overview', { params: { date: today } })
  kpi.value = kpiRes.data
  const machineRes = await api.get('/kpi/machines', { params: { from: today, to: today } })
  machines.value = machineRes.data
  const anomalyRes = await api.get('/anomalies', { params: { from: today, to: today } })
  anomalies.value = anomalyRes.data
})
</script>

<template>
  <main class="dash">
    <h1>Factory Dashboard</h1>
    <KpiCards :kpi="kpi" />
    <section class="grid">
      <v-chart class="chart" :option="chartOption" autoresize />
      <div>
        <h3>Worst Machines (by downtime)</h3>
        <table>
          <thead>
            <tr><th>Machine</th><th>Downtime</th><th>Output</th></tr>
          </thead>
          <tbody>
            <tr v-for="m in [...machines].sort((a,b)=>b.downtime-a.downtime).slice(0,5)" :key="m.machine_id + m.report_date">
              <td>{{ m.machine_id }}</td><td>{{ m.downtime.toFixed(1) }}</td><td>{{ m.output.toFixed(1) }}</td>
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
.chart { height: 340px; }
table { width: 100%; }
@media (max-width: 900px) { .grid { grid-template-columns: 1fr; } }
</style>
