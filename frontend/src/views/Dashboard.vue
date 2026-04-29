<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchPlugins, fetchCredentials } from '@/api'

const router = useRouter()
const plugins = ref<any[]>([])
const credentials = ref<any[]>([])

onMounted(async () => {
  try { plugins.value = await fetchPlugins() } catch {}
  try { credentials.value = await fetchCredentials() } catch {}
})

function credCount(pluginId: string) {
  return credentials.value.filter((c: any) => c.plugin_id === pluginId).length
}

function goToCredentials(pluginId: string) {
  router.push({ name: 'credentials', query: { plugin: pluginId } })
}
</script>

<template>
  <div style="display:flex;flex-direction:column;height:100%">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px">
      <div>
        <h2 style="margin:0;font-size:20px">控制面板</h2>
        <p style="margin:4px 0 0;color:#909399;font-size:13px">{{ plugins.length }} 个游戏社区</p>
      </div>
    </div>

    <el-row :gutter="16" style="flex:1;align-content:start">
      <el-col v-for="p in plugins" :key="p.id" :xs="24" :sm="12" :lg="8" style="margin-bottom:16px">
        <el-card
          shadow="hover"
          @click="goToCredentials(p.id)"
          style="cursor:pointer;height:100%"
        >
          <template #header>
            <div style="display:flex;align-items:center;justify-content:space-between">
              <span style="font-weight:600;font-size:15px">{{ p.name }}</span>
              <el-tag size="small" type="primary" effect="plain">{{ credCount(p.id) }} 个账号</el-tag>
            </div>
          </template>
          <p style="font-size:13px;color:#606266;margin-bottom:16px;min-height:36px">{{ p.description }}</p>
          <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap">
            <div
              v-for="g in p.supported_games"
              :key="g.id"
              :title="g.name"
              style="display:flex;flex-direction:column;align-items:center;gap:6px"
            >
              <img
                :src="g.icon"
                :alt="g.name"
                style="width:52px;height:52px;border-radius:14px;object-fit:cover;box-shadow:0 2px 8px rgba(0,0,0,0.08);flex-shrink:0"
              />
              <span style="font-size:11px;color:#909399;text-align:center;max-width:96px;line-height:1.3;word-break:keep-all">{{ g.name }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
