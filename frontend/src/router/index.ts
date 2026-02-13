import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [{ path: '/', component: DashboardView }]
})
