<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { ElMessage } from 'element-plus'
import { api } from '@/api'

const route = useRoute()
const router = useRouter()
const store = useAppStore()

onMounted(async () => {
  await store.checkStatus()
  if (!store.isUnlocked && route.path !== '/') {
    router.replace('/')
  }
})

watch(() => store.isUnlocked, (unlocked) => {
  if (!unlocked && route.path !== '/') router.replace('/')
})
</script>

<template>
  <div v-if="!store.isReady" style="display:flex;align-items:center;justify-content:center;height:100%">
    <span style="color:#c0c4cc;font-size:14px">连接中...</span>
  </div>
  <router-view v-else />
</template>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body, #app { height: 100%; }
</style>
