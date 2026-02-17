<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ anomalies: any[] }>()

const sorted = computed(() => {
  return [...props.anomalies].sort((a, b) => {
    const severityScore = (s: string) => (s === 'high' ? 2 : s === 'medium' ? 1 : 0)
    return severityScore(b.severity) - severityScore(a.severity)
  })
})

const iconFor = (severity: string) => {
  if (severity === 'high') return '!!'
  if (severity === 'medium') return '!'
  return '-'
}
</script>

<template>
  <div class="panel">
    <div class="panel-header">
      <h3>Top Anomalies</h3>
      <span class="panel-sub">Last 24h</span>
    </div>
    <ul class="list">
      <li
        v-for="a in sorted.slice(0, 8)"
        :key="a.machine_code + a.metric + a.report_date"
        :class="['item', a.severity === 'high' ? 'critical' : a.severity === 'medium' ? 'warning' : 'info']"
      >
        <div class="icon">{{ iconFor(a.severity) }}</div>
        <div class="content">
          <div class="title">{{ a.machine_code }} · {{ a.metric }}</div>
          <div class="meta">
            {{ a.report_date }} · {{ a.insight }}
          </div>
        </div>
        <div class="severity">{{ a.severity }}</div>
      </li>
    </ul>
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
.list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 8px;
  overflow: hidden;
}
.item {
  display: grid;
  grid-template-columns: 24px 1fr auto;
  gap: 10px;
  align-items: center;
  padding: 10px 12px;
  border: 1px solid var(--panel-border);
  border-radius: 2px;
  background: rgba(10, 15, 24, 0.6);
}
.item.critical {
  border-color: var(--accent-critical);
  box-shadow: inset 0 0 0 1px rgba(255, 23, 68, 0.4);
  animation: criticalBlink 1s steps(2, jump-none) infinite;
}
.item.warning {
  border-color: var(--accent-warning);
}
.icon {
  font-family: var(--font-mono);
  color: var(--accent-critical);
  font-weight: 700;
}
.content {
  display: grid;
  gap: 2px;
}
.title {
  font-weight: 600;
}
.meta {
  font-size: 12px;
  color: var(--text-muted);
}
.severity {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.7px;
  color: var(--text-muted);
}

@keyframes criticalBlink {
  0% {
    border-color: var(--accent-critical);
  }
  50% {
    border-color: #7a0f23;
  }
  100% {
    border-color: var(--accent-critical);
  }
}
</style>
