<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { fetchLogs, fetchTodaySummary, clearLogs, fetchPlugins } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete } from '@element-plus/icons-vue'

const logs = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(15)
const filterStatus = ref('')
const filterPlugin = ref('')
const filterDateRange = ref<[string, string] | null>(null)
const today = ref({ success: 0, already: 0, failed: 0, total: 0 })

const plugins = ref<any[]>([])

onMounted(refresh)
watch([page, filterStatus, filterPlugin, filterDateRange], refresh)

function formatDate(d: Date): string {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

async function refresh() {
  try {
    const [logsRes, todayRes] = await Promise.all([
      (async () => {
        const params: any = { page: page.value, page_size: pageSize.value }
        if (filterStatus.value) params.status = filterStatus.value
        if (filterPlugin.value) params.plugin_id = filterPlugin.value
        if (filterDateRange.value) {
          params.date_from = filterDateRange.value[0]
          params.date_to = filterDateRange.value[1]
        }
        return fetchLogs(params)
      })(),
      fetchTodaySummary(),
    ])
    logs.value = logsRes.items
    total.value = logsRes.total
    today.value = todayRes
    try { plugins.value = await fetchPlugins() } catch {}
  } catch {}
}

function pluginName(id: string) {
  return plugins.value.find((p: any) => p.id === id)?.name || id
}

function statusTag(s: string) {
  if (s === 'success') return 'success'
  if (s === 'already') return 'info'
  if (s === 'failed') return 'danger'
  return ''
}

function formatElapsed(sec: number): string {
  if (sec == null) return '-'
  if (sec < 1) return `${Math.round(sec * 1000)}ms`
  return `${sec.toFixed(1)}s`
}

async function handleClear() {
  try {
    await ElMessageBox.confirm('确定清除所有签到日志？此操作不可恢复。', '确认', { type: 'warning' })
    const res = await clearLogs()
    ElMessage.success(res.message)
    await refresh()
  } catch {}
}
</script>

<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <div>
        <h2 style="margin:0;font-size:20px">签到日志</h2>
        <p style="margin:4px 0 0;color:#909399;font-size:13px">共 {{ total }} 条记录</p>
      </div>
      <div style="display:flex;gap:8px">
        <el-select v-model="filterStatus" placeholder="状态" size="small" clearable style="width:110px">
          <el-option label="全部" value="" />
          <el-option label="成功" value="success" />
          <el-option label="已签到" value="already" />
          <el-option label="失败" value="failed" />
        </el-select>
        <el-select v-model="filterPlugin" placeholder="社区" size="small" clearable style="width:120px">
          <el-option label="全部" value="" />
          <el-option v-for="p in plugins" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
        <el-date-picker
          v-model="filterDateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          size="small"
          style="width:240px"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
        />
        <el-button size="small" type="danger" :icon="Delete" @click="handleClear">清除</el-button>
      </div>
    </div>

    <el-row :gutter="16" style="margin-bottom:16px">
      <el-col :span="6">
        <el-statistic title="成功" :value="today.success" />
      </el-col>
      <el-col :span="6">
        <el-statistic title="已签到" :value="today.already" />
      </el-col>
      <el-col :span="6">
        <el-statistic title="失败" :value="today.failed" />
      </el-col>
      <el-col :span="6">
        <el-statistic title="合计" :value="today.total" />
      </el-col>
    </el-row>

    <el-table :data="logs" stripe empty-text="暂无数据">
      <el-table-column label="时间" width="150">
        <template #default="{ row }">{{ row.signed_at?.slice(5,16)?.replace('T',' ') }}</template>
      </el-table-column>
      <el-table-column label="社区" width="100">
        <template #default="{ row }">
          <el-tag size="small" effect="dark">{{ pluginName(row.plugin_id) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="game_id" label="游戏" width="100" />
      <el-table-column label="账号" min-width="100">
        <template #default="{ row }">{{ row.credential_name || '#' + row.credential_id }}</template>
      </el-table-column>
      <el-table-column label="耗时" width="80" align="center">
        <template #default="{ row }">
          <span style="font-size:12px;color:#909399">{{ formatElapsed(row.elapsed) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="statusTag(row.status)" size="small" effect="dark">
            {{ row.status === 'success' ? '成功' : row.status === 'already' ? '已签到' : row.status === 'failed' ? '失败' : row.status.toUpperCase() }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="详情" min-width="160">
        <template #default="{ row }">{{ row.message || row.reward || '-' }}</template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-if="total > pageSize"
      v-model:current-page="page"
      :page-size="pageSize"
      :total="total"
      layout="prev, pager, next"
      size="small"
      style="margin-top:16px;justify-content:center"
    />
  </div>
</template>
