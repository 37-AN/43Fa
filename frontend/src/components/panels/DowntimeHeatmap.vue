<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ shifts: any[]; selectedShift: string }>()

const option = computed(() => {
  const shiftLabels = Array.from(new Set(props.shifts.map((s) => s.shift))).sort()
  const machineLabels = Array.from(new Set(props.shifts.map((s) => s.machine_id))).sort()

  const filtered = props.selectedShift === 'All'
    ? props.shifts
    : props.shifts.filter((s) => `Shift ${s.shift}` === props.selectedShift || s.shift === props.selectedShift)

  const data = filtered.map((s) => {
    const x = shiftLabels.indexOf(s.shift)
    const y = machineLabels.indexOf(s.machine_id)
    return [x, y, s.downtime_minutes]
  })

  return {
    backgroundColor: 'transparent',
    grid: { left: 120, right: 40, top: 30, bottom: 40 },
    tooltip: {
      position: 'top',
      backgroundColor: '#0f1722',
      borderColor: '#1f2a3a',
      textStyle: { color: '#d7dde6' },
      formatter: (params: any) => {
        const xLabel = shiftLabels[params.data[0]]
        const yLabel = machineLabels[params.data[1]]
        return `${yLabel} / ${xLabel}<br/>Downtime: ${Number(params.data[2]).toFixed(1)} min`
      }
    },
    xAxis: {
      type: 'category',
      data: shiftLabels,
      axisLine: { lineStyle: { color: '#2a3342' } },
      axisLabel: { color: '#a9b3c1' }
    },
    yAxis: {
      type: 'category',
      data: machineLabels,
      axisLine: { lineStyle: { color: '#2a3342' } },
      axisLabel: { color: '#a9b3c1' }
    },
    visualMap: {
      min: 0,
      max: Math.max(10, ...filtered.map((s) => s.downtime_minutes || 0)),
      calculable: false,
      orient: 'horizontal',
      left: 'center',
      bottom: 0,
      textStyle: { color: '#a9b3c1' },
      inRange: {
        color: ['#0b2a1a', '#00C853', '#FF9100', '#FF1744']
      }
    },
    series: [
      {
        type: 'heatmap',
        data,
        label: { show: false },
        emphasis: {
          itemStyle: {
            borderColor: '#d7dde6',
            borderWidth: 1
          }
        }
      }
    ]
  }
})
</script>

<template>
  <div class="panel">
    <div class="panel-header">
      <h3>Downtime Heatmap</h3>
      <span class="panel-sub">Machine vs shift</span>
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
