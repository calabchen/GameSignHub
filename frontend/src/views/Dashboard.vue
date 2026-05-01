<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { fetchPlugins, fetchCredentials } from '@/api'

const plugins = ref<any[]>([])
const credentials = ref<any[]>([])

onMounted(async () => {
  try { plugins.value = await fetchPlugins() } catch {}
  try { credentials.value = await fetchCredentials() } catch {}
})

function credCount(pluginId: string) {
  return credentials.value.filter((c: any) => c.plugin_id === pluginId).length
}
</script>

<template>
  <div>
    <h2 style="margin:0 0 16px;font-size:18px">控制面板</h2>

    <el-row :gutter="12">
      <el-col v-for="p in plugins" :key="p.id" :xs="24" :sm="12" :lg="8" style="margin-bottom:12px">
        <el-card shadow="hover">
          <template #header>
            <div style="display:flex;align-items:center;justify-content:space-between">
              <span style="font-weight:600;font-size:14px">{{ p.name }}</span>
              <el-tag size="small" type="primary" effect="plain">{{ credCount(p.id) }} 个账号</el-tag>
            </div>
          </template>
          <p style="font-size:12px;color:#606266;margin-bottom:12px;min-height:28px">{{ p.description }}</p>
          <div style="display:flex;gap:10px;flex-wrap:wrap">
            <div v-for="g in p.supported_games" :key="g.id" :title="g.name" style="display:flex;flex-direction:column;align-items:center;gap:4px">
              <img :src="g.icon" :alt="g.name" style="width:44px;height:44px;border-radius:10px;object-fit:cover;box-shadow:0 1px 4px rgba(0,0,0,0.08)" />
              <span style="font-size:12px;color:#909399">{{ g.name }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
