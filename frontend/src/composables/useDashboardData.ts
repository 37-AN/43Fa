import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import api, { setToken } from '../api/client'

const AUTO_REFRESH_MS = 30000

export type ShiftOption = 'All' | 'Shift A' | 'Shift B' | 'Shift C'

export const useDashboardData = () => {
  const today = new Date().toISOString().slice(0, 10)
  const fromDate = ref(today)
  const toDate = ref(today)
  const selectedMachine = ref('')
  const selectedShift = ref<ShiftOption>('All')

  const kpi = ref<any>(null)
  const machines = ref<any[]>([])
  const days = ref<any[]>([])
  const shifts = ref<any[]>([])
  const anomalies = ref<any[]>([])
  const riskPanel = ref<any>(null)
  const machineOptions = ref<string[]>([])

  const loading = ref(false)
  const lastRefreshed = ref<Date | null>(null)
  const apiAlive = ref(false)
  const autoRefresh = ref(true)

  let intervalId: number | null = null

  const loadData = async () => {
    loading.value = true

    const token = localStorage.getItem('token')
    if (token) {
      setToken(token)
    }

    try {
      const [kpiRes, machineRes, dayRes, shiftRes, anomalyRes, riskPanelRes, metricsRes] = await Promise.all([
        api.get('/kpi/overview', { params: { date: toDate.value } }),
        api.get('/kpi/machines', {
          params: { from: fromDate.value, to: toDate.value, machine_id: selectedMachine.value || undefined }
        }),
        api.get('/kpi/days', { params: { from: fromDate.value, to: toDate.value } }),
        api.get('/kpi/shifts', {
          params: { from: fromDate.value, to: toDate.value, machine_id: selectedMachine.value || undefined }
        }),
        api.get('/anomalies', { params: { from: fromDate.value, to: toDate.value } }),
        api.get('/risk/panel', { params: { date: toDate.value } }),
        api.get('/metrics')
      ])

      kpi.value = kpiRes.data
      machines.value = machineRes.data
      days.value = dayRes.data
      shifts.value = shiftRes.data
      anomalies.value = anomalyRes.data
      riskPanel.value = riskPanelRes.data
      machineOptions.value = Array.from(new Set<string>(machineRes.data.map((m: any) => String(m.machine_id))))
      apiAlive.value = metricsRes.status === 200
      lastRefreshed.value = new Date()
    } catch (err) {
      console.error('Failed to load dashboard data', err)
      apiAlive.value = false
    } finally {
      loading.value = false
    }
  }

  const startAutoRefresh = () => {
    if (intervalId) return
    intervalId = window.setInterval(() => {
      loadData()
    }, AUTO_REFRESH_MS)
  }

  const stopAutoRefresh = () => {
    if (intervalId) {
      window.clearInterval(intervalId)
      intervalId = null
    }
  }

  const refreshNow = () => loadData()

  const shiftOptions = computed<ShiftOption[]>(() => ['All', 'Shift A', 'Shift B', 'Shift C'])

  onMounted(() => {
    loadData()
    if (autoRefresh.value) startAutoRefresh()
  })

  onUnmounted(() => {
    stopAutoRefresh()
  })

  watch([fromDate, toDate, selectedMachine], loadData)

  watch(autoRefresh, (value) => {
    if (value) startAutoRefresh()
    else stopAutoRefresh()
  })

  return {
    fromDate,
    toDate,
    selectedMachine,
    selectedShift,
    shiftOptions,
    kpi,
    machines,
    days,
    shifts,
    anomalies,
    riskPanel,
    machineOptions,
    loading,
    lastRefreshed,
    apiAlive,
    autoRefresh,
    refreshNow
  }
}
