<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ machines: any[]; shifts: any[]; selectedShift: string }>()

const rows = computed(() => {
  if (props.selectedShift !== 'All') {
    const filtered = props.shifts.filter(
      (s) => `Shift ${s.shift}` === props.selectedShift || s.shift === props.selectedShift
    )
    const aggregated: Record<string, { downtime: number; throughput: number }> = {}
    filtered.forEach((s) => {
      const key = s.machine_id
      if (!aggregated[key]) aggregated[key] = { downtime: 0, throughput: 0 }
      aggregated[key].downtime += s.downtime_minutes
      aggregated[key].throughput += s.throughput_units
    })
    return Object.entries(aggregated)
      .map(([machine_id, data]) => ({ machine_id, ...data }))
      .sort((a, b) => b.downtime - a.downtime)
      .slice(0, 6)
  }

  const aggregated: Record<string, { downtime: number; throughput: number }> = {}
  props.machines.forEach((m) => {
    const key = m.machine_id
    if (!aggregated[key]) aggregated[key] = { downtime: 0, throughput: 0 }
    aggregated[key].downtime += m.downtime_minutes
    aggregated[key].throughput += m.throughput_units
  })

  return Object.entries(aggregated)
    .map(([machine_id, data]) => ({ machine_id, ...data }))
    .sort((a, b) => b.downtime - a.downtime)
    .slice(0, 6)
})
</script>

<template>
  <div class="panel">
    <div class="panel-header">
      <h3>Worst Machines</h3>
      <span class="panel-sub">Top downtime</span>
    </div>
    <table>
      <thead>
        <tr>
          <th>Machine</th>
          <th>Downtime (min)</th>
          <th>Throughput</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in rows" :key="row.machine_id">
          <td>{{ row.machine_id }}</td>
          <td class="mono warning">{{ row.downtime.toFixed(1) }}</td>
          <td class="mono">{{ row.throughput.toFixed(1) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.panel {
  height: 100%;
  display: grid;
  grid-template-rows: auto 1fr;
  gap: 8px;
}
.panel-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
}
.panel-header h3 {
  font-size: 14px;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 1px;
}
.panel-sub {
  font-size: 12px;
  color: var(--text-muted);
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 8px 6px;
  border-bottom: 1px solid var(--panel-border);
  font-size: 12px;
}

th {
  text-align: left;
  text-transform: uppercase;
  letter-spacing: 0.7px;
  color: var(--text-muted);
}

.mono {
  font-family: var(--font-mono);
}

.warning {
  color: var(--accent-warning);
}
</style>
