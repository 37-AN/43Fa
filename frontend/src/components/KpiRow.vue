<script setup lang="ts">
const props = defineProps<{ kpi: any }>()

const toFixed = (value: number | undefined, digits = 2) => (value ?? 0).toFixed(digits)
</script>

<template>
  <section class="kpi-row">
    <div class="kpi-card">
      <div class="kpi-label">Availability</div>
      <div class="kpi-value">{{ toFixed(props.kpi?.availability_percent) }}%</div>
      <div class="kpi-sub">Target &gt; 95%</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">OEE Proxy</div>
      <div class="kpi-value">{{ toFixed(props.kpi?.oee_proxy) }}%</div>
      <div class="kpi-sub">Composite efficiency</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Scrap %</div>
      <div class="kpi-value warning">{{ toFixed(props.kpi?.scrap_percent) }}%</div>
      <div class="kpi-sub">Yield losses</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Downtime</div>
      <div class="kpi-value critical">{{ toFixed(props.kpi?.downtime_minutes, 1) }} min</div>
      <div class="kpi-sub">Accumulated</div>
    </div>
  </section>
</template>

<style scoped>
.kpi-row {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}
.kpi-card {
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  padding: 16px;
  border-radius: 2px;
  display: grid;
  gap: 6px;
}
.kpi-label {
  font-size: 12px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.8px;
}
.kpi-value {
  font-family: var(--font-mono);
  font-size: 28px;
  font-weight: 700;
  color: var(--accent-normal);
}
.kpi-sub {
  font-size: 12px;
  color: var(--text-subtle);
}
.kpi-value.warning {
  color: var(--accent-warning);
}
.kpi-value.critical {
  color: var(--accent-critical);
}
</style>
