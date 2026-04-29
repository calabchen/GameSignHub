import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api'

export const useAppStore = defineStore('app', () => {
  const isUnlocked = ref(false)
  const isPasswordSet = ref(false)
  const pluginsLoaded = ref(0)
  const token = ref('')
  const loading = ref(false)

  const axiosHeaders = computed(() => {
    if (token.value) {
      return { Authorization: `Bearer ${token.value}` }
    }
    return {}
  })

  const isReady = ref(false)

  async function checkStatus() {
    try {
      const res = await api.get('/api/status')
      isUnlocked.value = res.data.is_unlocked
      isPasswordSet.value = res.data.is_password_set
      pluginsLoaded.value = res.data.plugins_loaded
    } catch { /* server not ready */ }
    isReady.value = true
  }

  async function unlock(password: string): Promise<{ ok: boolean; firstTime?: boolean }> {
    try {
      const res = await api.post('/api/unlock', { password })
      token.value = res.data.token
      localStorage.setItem('token', res.data.token)
      isUnlocked.value = true
      await checkStatus()
      return { ok: true, firstTime: res.data.is_first_time }
    } catch (e: any) {
      if (e.response?.status === 401) return { ok: false }
      throw e
    }
  }

  async function lock() {
    await api.post('/api/lock')
    token.value = ''
    localStorage.removeItem('token')
    isUnlocked.value = false
  }

  return { isReady, isUnlocked, isPasswordSet, pluginsLoaded, token, loading, axiosHeaders, checkStatus, unlock, lock }
})
