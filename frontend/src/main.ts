import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// ECharts modular runtime setup (renderer + charts + components)
import * as echarts from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import VChart, { use as vueEChartsUse } from 'vue-echarts'

const app = createApp(App)
app.use(router)
// register renderer, charts and components
echarts.use([CanvasRenderer, LineChart, TooltipComponent, LegendComponent, GridComponent])

app.component('v-chart', VChart)
// register echarts instance with vue-echarts and provide globally
vueEChartsUse(echarts)
app.provide('echarts', echarts)
app.config.globalProperties.$echarts = echarts
// expose on window for any third-party code expecting a global
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
window.echarts = echarts

app.mount('#app')
