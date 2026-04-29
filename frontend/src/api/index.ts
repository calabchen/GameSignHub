import axios from 'axios'

export const api = axios.create({
  baseURL: '',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
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

export async function signCredential(credId: number) {
  const res = await api.post(`/api/sign/credential/${credId}`)
  return res.data
}

export async function signPlugin(pluginId: string) {
  const res = await api.post(`/api/sign/plugin/${pluginId}`)
  return res.data
}

export async function signAll() {
  const res = await api.post('/api/sign/all')
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
