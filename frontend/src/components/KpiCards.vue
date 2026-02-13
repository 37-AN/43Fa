<script setup lang="ts">
defineProps<{ kpi: any }>()
</script>

<template>
  <section class="cards">
    <div class="card">Availability: {{ (kpi?.availability_proxy ?? 0) * 100 }}%</div>
    <div class="card">Downtime: {{ kpi?.downtime_minutes ?? 0 }}</div>
    <div class="card">Scrap: {{ kpi?.scrap_units ?? 0 }}</div>
    <div class="card">Throughput: {{ kpi?.throughput_units ?? 0 }}</div>
  </section>
</template>

<style scoped>
.cards { display: grid; grid-template-columns: repeat(4, minmax(140px, 1fr)); gap: 10px; }
.card { background: #f7f8fa; padding: 12px; border-radius: 8px; }
</style>
