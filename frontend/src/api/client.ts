import axios from 'axios'

const apiBaseUrl = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({ baseURL: apiBaseUrl })

export const setToken = (token: string) => {
  api.defaults.headers.common.Authorization = `Bearer ${token}`
}

export default api
