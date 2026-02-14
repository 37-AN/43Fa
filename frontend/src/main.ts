import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// ECharts runtime setup (renderer + charts + components)
import * as echarts from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import VChart from 'vue-echarts'

echarts.use([CanvasRenderer, LineChart, TooltipComponent, LegendComponent, GridComponent])

const app = createApp(App)
app.use(router)
app.component('v-chart', VChart)
app.mount('#app')
