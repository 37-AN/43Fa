<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ riskPanel: any | null }>()

const rows = computed(() => {
  if (!props.riskPanel?.top_risk_machines) return []
  return props.riskPanel.top_risk_machines
})
</script>

<template>
  <div class="panel">
    <div class="panel-header">
      <h3>Risk Panel</h3>
      <span class="panel-sub">Top 5 machines</span>
    </div>

    <table>
      <thead>
        <tr>
          <th>Rank</th>
          <th>Machine</th>
          <th>Risk</th>
          <th>7D Fail</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in rows" :key="row.machine_id">
          <td class="mono">#{{ row.maintenance_urgency_rank }}</td>
          <td>{{ row.machine_id }}</td>
          <td class="mono danger">{{ row.risk_score.toFixed(1) }}</td>
          <td class="mono">{{ (row.failure_probability_next_7_days * 100).toFixed(1) }}%</td>
        </tr>
      </tbody>
    </table>

    <div v-if="rows.length > 0" class="recommendations">
      <h4>Prescriptive Actions</h4>
      <p v-for="(rec, index) in rows[0].recommendations" :key="index">{{ rec }}</p>
    </div>
  </div>
</template>

<style scoped>
.panel {
  height: 100%;
  display: grid;
  grid-template-rows: auto 1fr auto;
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

.danger {
  color: var(--accent-warning);
}

.recommendations {
  border-top: 1px solid var(--panel-border);
  padding-top: 8px;
}

.recommendations h4 {
  margin: 0 0 6px;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

.recommendations p {
  margin: 0 0 4px;
  font-size: 12px;
  color: var(--text-muted);
}
</style>
