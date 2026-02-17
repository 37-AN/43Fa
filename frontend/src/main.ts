import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// ECharts modular runtime setup (renderer + charts + components)
import * as echarts from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, HeatmapChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent, GridComponent, VisualMapComponent } from 'echarts/components'
import VChart from 'vue-echarts'

console.log('Creating Vue app...')
try {
  const app = createApp(App)
  app.use(router)
  // register renderer, charts and components
  echarts.use([CanvasRenderer, LineChart, HeatmapChart, TooltipComponent, LegendComponent, GridComponent, VisualMapComponent])

  app.component('v-chart', VChart)
  // provide echarts instance for vue-echarts and other code
  app.provide('echarts', echarts)
  app.config.globalProperties.$echarts = echarts
  // expose on window for any third-party code expecting a global
  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore
  window.echarts = echarts

  app.config.errorHandler = (err, instance, info) => {
    console.error('Vue error:', err, info)
  }

  // Suppress errors from browser extensions
  app.config.warnHandler = () => null

  console.log('Mounting Vue app to #app...')
  app.mount('#app')
  console.log('Vue app mounted successfully')
} catch (err) {
  console.error('Failed to create/mount app:', err)
}
