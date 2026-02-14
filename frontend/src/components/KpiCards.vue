<script setup lang="ts">
defineProps<{ kpi: any }>()
</script>

<template>
  <section class="cards">
    <div class="card">Availability: {{ (kpi?.availability_percent ?? 0).toFixed(2) }}%</div>
    <div class="card">OEE Proxy: {{ (kpi?.oee_proxy ?? 0).toFixed(2) }}%</div>
    <div class="card">Downtime: {{ kpi?.downtime_minutes ?? 0 }}</div>
    <div class="card">Scrap Rate: {{ (kpi?.scrap_percent ?? 0).toFixed(2) }}%</div>
    <div class="card">Throughput: {{ kpi?.throughput_units ?? 0 }}</div>
  </section>
</template>

<style scoped>
.cards { display: grid; grid-template-columns: repeat(5, minmax(140px, 1fr)); gap: 10px; }
.card { background: #f7f8fa; padding: 12px; border-radius: 8px; }
</style>
