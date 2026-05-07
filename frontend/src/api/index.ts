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

export async function fetchAccounts() {
  const res = await api.get('/api/accounts')
  return res.data
}

export async function createAccount(data: any) {
  const res = await api.post('/api/accounts', data)
  return res.data
}

export async function updateAccount(id: number, data: any) {
  const res = await api.patch(`/api/accounts/${id}`, data)
  return res.data
}

export async function deleteAccount(id: number) {
  const res = await api.delete(`/api/accounts/${id}`)
  return res.data
}

export async function validateAccount(id: number, plugin: string = 'kuro') {
  const res = await api.post(`/api/accounts/${id}/validate?plugin=${plugin}`)
  return res.data
}

// backward-compatible aliases
export const fetchCredentials = fetchAccounts
export const createCredential = createAccount
export const updateCredential = updateAccount
export const deleteCredential = deleteAccount
export const validateCredential = validateAccount

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

export async function fetchAccountSchedule(id: number, gameId: string, plugin: string) {
  const res = await api.get(`/api/accounts/${id}/schedule/${gameId}`, { params: { plugin } })
  return res.data
}

export async function updateAccountSchedule(id: number, gameId: string, cron: string, enabled: boolean, plugin: string) {
  const res = await api.put(`/api/accounts/${id}/schedule/${gameId}`, { cron, enabled }, { params: { plugin } })
  return res.data
}

export async function fetchAccountDetail(id: number, plugin: string) {
  const res = await api.get(`/api/accounts/${id}/detail`, { params: { plugin } })
  return res.data
}

// backward-compatible aliases
export const fetchCredentialSchedule = (id: number, gameId: string) => fetchAccountSchedule(id, gameId, 'kuro')
export const updateCredentialSchedule = (id: number, gameId: string, cron: string, enabled: boolean) => updateAccountSchedule(id, gameId, cron, enabled, 'kuro')
export const fetchCredentialDetail = (id: number) => fetchAccountDetail(id, 'kuro')
