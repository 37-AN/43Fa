<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ days: any[] }>()

const option = computed(() => {
  const dates = props.days.map((d) => d.date)
  const throughput = props.days.map((d) => d.throughput_units)
  const downtime = props.days.map((d) => d.downtime_minutes)

  return {
    backgroundColor: 'transparent',
    grid: { left: 50, right: 40, top: 30, bottom: 40 },
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#0f1722',
      borderColor: '#1f2a3a',
      textStyle: { color: '#d7dde6' },
      formatter: (params: any[]) => {
        return params
          .map((p) => {
            const unit = p.seriesName === 'Throughput' ? 'units' : 'min'
            return `${p.marker} ${p.seriesName}: ${Number(p.value).toFixed(1)} ${unit}`
          })
          .join('<br/>')
      }
    },
    legend: { textStyle: { color: '#c3cbd6' }, data: ['Throughput', 'Downtime'] },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: { lineStyle: { color: '#2a3342' } },
      axisLabel: { color: '#a9b3c1' },
      splitLine: { show: false }
    },
    yAxis: [
      {
        type: 'value',
        name: 'Throughput',
        axisLine: { lineStyle: { color: '#2a3342' } },
        axisLabel: { color: '#a9b3c1' },
        splitLine: { lineStyle: { color: '#1a2330' } }
      },
      {
        type: 'value',
        name: 'Downtime (min)',
        axisLine: { lineStyle: { color: '#2a3342' } },
        axisLabel: { color: '#a9b3c1' },
        splitLine: { lineStyle: { color: '#1a2330' } }
      }
    ],
    series: [
      {
        name: 'Throughput',
        type: 'line',
        smooth: true,
        yAxisIndex: 0,
        data: throughput,
        lineStyle: { color: '#00C853', width: 2 },
        itemStyle: { color: '#00C853' }
      },
      {
        name: 'Downtime',
        type: 'line',
        smooth: true,
        yAxisIndex: 1,
        data: downtime,
        lineStyle: { color: '#FF9100', width: 2 },
        itemStyle: { color: '#FF9100' }
      }
    ]
  }
})
</script>

<template>
  <div class="panel">
    <div class="panel-header">
      <h3>Throughput vs Downtime</h3>
      <span class="panel-sub">Daily aggregate</span>
    </div>
    <v-chart class="chart" :option="option" autoresize />
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
.chart {
  width: 100%;
  height: 100%;
}
</style>
