import axios from 'axios'

export const api = axios.create({
  baseURL: '',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export async function fetchPlugins() {
  const res = await api.get('/api/plugins')
  return res.data
}

export async function fetchPlugin(id: string) {
  const res = await api.get(`/api/plugins/${id}`)
  return res.data
}

export async function fetchCredentials() {
  const res = await api.get('/api/credentials')
  return res.data
}

export async function createCredential(data: any) {
  const res = await api.post('/api/credentials', data)
  return res.data
}

export async function updateCredential(id: number, data: any) {
  const res = await api.put(`/api/credentials/${id}`, data)
  return res.data
}

export async function deleteCredential(id: number) {
  const res = await api.delete(`/api/credentials/${id}`)
  return res.data
}

export async function validateCredential(id: number) {
  const res = await api.post(`/api/credentials/${id}/validate`)
  return res.data
}

export async function signCredential(pluginId: string, credId: number, gameId: string) {
  const res = await api.post(`/api/signs/plugins/${pluginId}/credentials/${credId}/games/${gameId}`)
  return res.data
}

export async function signPlugin(pluginId: string) {
  const res = await api.post(`/api/signs/plugins/${pluginId}`)
  return res.data
}

export async function signAll() {
  const res = await api.post('/api/schedules/triggers')
  return res.data
}

export async function fetchLogs(params: Record<string, any> = {}) {
  const res = await api.get('/api/logs', { params })
  return res.data
}

export async function fetchTodaySummary() {
  const res = await api.get('/api/logs/today')
  return res.data
}

export async function clearLogs() {
  const res = await api.delete('/api/logs')
  return res.data
}

export async function fetchCredentialSchedule(id: number, gameId: string) {
  const res = await api.get(`/api/credentials/${id}/schedule/${gameId}`)
  return res.data
}

export async function updateCredentialSchedule(id: number, gameId: string, cron: string, enabled: boolean) {
  const res = await api.put(`/api/credentials/${id}/schedule/${gameId}`, { cron, enabled })
  return res.data
}

export async function fetchCredentialDetail(id: number) {
  const res = await api.get(`/api/credentials/${id}/detail`)
  return res.data
}
