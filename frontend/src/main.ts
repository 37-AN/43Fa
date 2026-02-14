import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// ECharts runtime setup (renderer + charts + components)
import * as echarts from 'echarts'
import VChart, { use as vueEChartsUse } from 'vue-echarts'

const app = createApp(App)
app.use(router)
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
