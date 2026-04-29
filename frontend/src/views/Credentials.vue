<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import {
  fetchPlugins, fetchCredentials, createCredential, updateCredential, deleteCredential,
  validateCredential, signCredential, signAll,
  fetchCredentialSchedule, updateCredentialSchedule, fetchCredentialDetail,
  fetchLogs, fetchTodaySummary, clearLogs,
} from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, VideoPlay, Timer, Delete } from '@element-plus/icons-vue'

const plugins = ref<any[]>([])
const allAccounts = ref<any[]>([])
const dialogVisible = ref(false)
const dialogTitle = ref('添加账户')

const kuroFields = reactive({
  token: '', user_id: '', devcode: '', distinct_id: '',
  wuwa: { role_id: '', enabled: true },
  pgr: { role_id: '', enabled: false },
})

const form = reactive({
  id: null as number | null, plugin_id: 'kuro', is_enabled: true,
})

const signLoading = ref<number | null>(null)

const accountPage = ref(1)
const accountPageSize = ref(5)
const pagedAccounts = computed(() => {
  const start = (accountPage.value - 1) * accountPageSize.value
  return allAccounts.value.slice(start, start + accountPageSize.value)
})

const scheduleDialog = ref(false)
const scheduleCredId = ref<number | null>(null)
const scheduleGames = reactive({
  wuwa: { cron: '', enabled: false },
  pgr: { cron: '', enabled: false },
})

const schedulePresets = [
  { label: '每天 07:00', value: '0 7 * * *' },
  { label: '每天 08:00', value: '0 8 * * *' },
  { label: '每天 12:00', value: '0 12 * * *' },
  { label: '每天 18:00', value: '0 18 * * *' },
  { label: '每天 22:00', value: '0 22 * * *' },
]

const logs = ref<any[]>([])
const logTotal = ref(0)
const logPage = ref(1)
const logPageSize = ref(100)
const logFilterStatus = ref('')
const logFilterPlugin = ref('')
const logFilterDateRange = ref<[string, string] | null>(null)
const todaySummary = ref({ total: 0, success: 0, already: 0, failed: 0 })
const logContainer = ref<HTMLDivElement>()

const logLevels = ['debug', 'info', 'warn', 'error'] as const
const terminalLog = ref<{ time: string; plugin: string; game: string; account: string; elapsed: string; status: string; msg: string }[]>([])

onMounted(async () => {
  try { plugins.value = await fetchPlugins() } catch {}
  try { allAccounts.value = await fetchCredentials() } catch {}
  accountPage.value = 1
  refreshLogs()
})

watch([logPage, logFilterStatus, logFilterPlugin, logFilterDateRange], refreshLogs)
watch(terminalLog, async () => { await nextTick(); if (logContainer.value) logContainer.value.scrollTop = logContainer.value.scrollHeight }, { deep: true })

async function refreshLogs() {
  try {
    const [logRes, todayRes] = await Promise.all([
      (async () => {
        const params: any = { page: logPage.value, page_size: logPageSize.value }
        if (logFilterStatus.value) params.status = logFilterStatus.value
        if (logFilterPlugin.value) params.plugin_id = logFilterPlugin.value
        if (logFilterDateRange.value) {
          params.date_from = logFilterDateRange.value[0]
          params.date_to = logFilterDateRange.value[1]
        }
        return fetchLogs(params)
      })(),
      fetchTodaySummary(),
    ])
    logs.value = logRes.items; logTotal.value = logRes.total; todaySummary.value = todayRes
    terminalLog.value = logRes.items.map((r: any) => ({
      time: r.signed_at?.slice(5, 16)?.replace('T', ' ') || '',
      plugin: r.plugin_id || '',
      game: r.game_id || '',
      account: r.credential_name || '#' + r.credential_id,
      elapsed: formatElapsed(r.elapsed),
      status: r.status || '',
      msg: r.message || r.reward || '',
    }))
  } catch {}
}

function pluginName(id: string) { return plugins.value.find((p: any) => p.id === id)?.name || id }

function statusTag(s: string) {
  if (s === 'success') return 'success'
  if (s === 'already') return 'info'
  if (s === 'failed') return 'danger'
  return ''
}

function statusColor(s: string) {
  if (s === 'success') return '#67c23a'
  if (s === 'already') return '#909399'
  if (s === 'failed') return '#f56c6c'
  return '#e6a23c'
}

function formatElapsed(sec: number): string {
  if (sec == null) return '-'
  if (sec < 1) return `${Math.round(sec * 1000)}ms`
  return `${sec.toFixed(1)}s`
}

function cronLabel(cron: string) {
  if (!cron) return '—'
  const m: Record<string, string> = {
    '0 7 * * *': '每天 07:00', '0 8 * * *': '每天 08:00',
    '0 12 * * *': '每天 12:00', '0 18 * * *': '每天 18:00', '0 22 * * *': '每天 22:00',
  }
  return m[cron] || cron
}

async function handleSign(account: any) {
  signLoading.value = account.id
  try {
    await signCredential(account.plugin_id, account.id, 'wuwa')
    ElMessage.success('签到完成')
    await refreshLogs()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '签到失败')
  } finally { signLoading.value = null }
}

function kuroFieldsFromDetail(detail: any) {
  kuroFields.token = detail.token || ''; kuroFields.user_id = detail.user_id || ''
  kuroFields.devcode = detail.devcode || ''; kuroFields.distinct_id = detail.distinct_id || ''
  const w = detail.wuwa || {}
  kuroFields.wuwa.role_id = w.role_id || ''; kuroFields.wuwa.enabled = w.enabled !== false
  const p = detail.pgr || {}
  kuroFields.pgr.role_id = p.role_id || ''; kuroFields.pgr.enabled = p.enabled === true
}

function resetKuroFields() {
  kuroFields.token = ''; kuroFields.user_id = ''; kuroFields.devcode = ''; kuroFields.distinct_id = ''
  kuroFields.wuwa = { role_id: '', enabled: true }; kuroFields.pgr = { role_id: '', enabled: false }
}

function kuroFieldsToBody() {
  return {
    token: kuroFields.token, user_id: kuroFields.user_id,
    devcode: kuroFields.devcode, distinct_id: kuroFields.distinct_id,
    wuwa_role_id: kuroFields.wuwa.role_id, pgr_role_id: kuroFields.pgr.role_id,
  }
}

function openAdd() {
  dialogTitle.value = '添加账户'; form.id = null
  form.plugin_id = 'kuro'; form.is_enabled = true
  resetKuroFields(); dialogVisible.value = true
}

async function openEdit(account: any) {
  dialogTitle.value = '编辑账户'; form.id = account.id
  form.plugin_id = account.plugin_id; form.is_enabled = account.is_enabled
  if (account.plugin_id === 'kuro') {
    try { const detail = await fetchCredentialDetail(account.id); kuroFieldsFromDetail(detail) } catch { resetKuroFields() }
  }
  dialogVisible.value = true
}

async function handleSave() {
  const k = kuroFieldsToBody()
  const payload: any = {
    plugin_id: form.plugin_id, is_enabled: form.is_enabled,
    token: k.token, user_id: k.user_id, devcode: k.devcode, distinct_id: k.distinct_id,
    wuwa_role_id: k.wuwa_role_id, pgr_role_id: k.pgr_role_id,
  }
  try {
    if (form.id) { await updateCredential(form.id, payload); ElMessage.success('已更新') }
    else { await createCredential(payload); ElMessage.success('已创建') }
    dialogVisible.value = false
    try { allAccounts.value = await fetchCredentials(); accountPage.value = 1 } catch {}
  } catch (e: any) { ElMessage.error(e.response?.data?.detail || '操作失败') }
}

async function handleDelete(account: any) {
  try {
    await ElMessageBox.confirm('确定删除此账户？', '确认', { type: 'warning' })
    await deleteCredential(account.id)
    ElMessage.success('已删除')
    try { allAccounts.value = await fetchCredentials(); accountPage.value = 1 } catch {}
  } catch {}
}

async function handleValidate(account: any) {
  try {
    const res = await validateCredential(account.id)
    if (res.valid) ElMessage.success('账户有效')
    else ElMessage.warning('无效: ' + res.message)
  } catch (e: any) { ElMessage.error(e.response?.data?.detail || '验证失败') }
}

async function openSchedule(account: any) {
  scheduleCredId.value = account.id
  scheduleGames.wuwa = { cron: '', enabled: false }; scheduleGames.pgr = { cron: '', enabled: false }
  try {
    const [w, p] = await Promise.all([
      fetchCredentialSchedule(account.id, 'wuwa'),
      fetchCredentialSchedule(account.id, 'pgr'),
    ])
    scheduleGames.wuwa = { cron: w.cron || '', enabled: w.enabled || false }
    scheduleGames.pgr = { cron: p.cron || '', enabled: p.enabled || false }
  } catch {}
  scheduleDialog.value = true
}

async function saveSchedule() {
  if (scheduleCredId.value == null) return
  try {
    await Promise.all([
      updateCredentialSchedule(scheduleCredId.value, 'wuwa', scheduleGames.wuwa.cron, scheduleGames.wuwa.enabled),
      updateCredentialSchedule(scheduleCredId.value, 'pgr', scheduleGames.pgr.cron, scheduleGames.pgr.enabled),
    ])
    ElMessage.success('定时设置已更新'); scheduleDialog.value = false
    try { allAccounts.value = await fetchCredentials(); accountPage.value = 1 } catch {}
  } catch (e: any) { ElMessage.error(e.response?.data?.detail || '更新失败') }
}

async function handleClearLogs() {
  try {
    await ElMessageBox.confirm('确定清除所有签到日志？', '确认', { type: 'warning' })
    const res = await clearLogs()
    ElMessage.success(res.message)
    await refreshLogs()
  } catch {}
}
</script>

<template>
  <div style="display:flex;flex-direction:column;height:100%">
    <div style="flex:1;min-height:0;display:flex;flex-direction:column">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-shrink:0">
        <div style="display:flex;align-items:center;gap:12px">
          <h2 style="margin:0;font-size:18px">账户管理</h2>
          <span style="color:#909399;font-size:13px">{{ allAccounts.length }} 个账户</span>
        </div>
        <div style="display:flex;gap:8px">
          <el-button type="primary" :icon="Plus" @click="openAdd">添加账户</el-button>
        </div>
      </div>
      <div style="flex:1;min-height:0;overflow-y:auto">
        <el-table :data="pagedAccounts" stripe empty-text="暂无数据" size="small">
          <el-table-column label="社区" width="70">
            <template #default="{ row }"><el-tag size="small" effect="dark">{{ pluginName(row.plugin_id) }}</el-tag></template>
          </el-table-column>
          <el-table-column label="User ID" min-width="120">
            <template #default="{ row }">{{ row.user_id || '未设置' }}</template>
          </el-table-column>
          <el-table-column label="角色 ID" min-width="150">
            <template #default="{ row }">
              <span v-if="row.wuwa_role_id" style="margin-right:6px">鸣潮: {{ row.wuwa_role_id }}</span>
              <span v-if="row.pgr_role_id">战双: {{ row.pgr_role_id }}</span>
              <span v-if="!row.wuwa_role_id && !row.pgr_role_id" style="color:#c0c4cc">未设置</span>
            </template>
          </el-table-column>
          <el-table-column label="定时" width="70">
            <template #default="{ row }">
              <el-button size="small" text :icon="Timer" @click="openSchedule(row)">设置</el-button>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="240" fixed="right">
            <template #default="{ row }">
              <el-button size="small" type="primary" :loading="signLoading === row.id" @click="handleSign(row)">签到</el-button>
              <el-button size="small" @click="handleValidate(row)">验证</el-button>
              <el-button size="small" @click="openEdit(row)">编辑</el-button>
              <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <el-pagination
        v-if="allAccounts.length > 0"
        v-model:current-page="accountPage"
        v-model:page-size="accountPageSize"
        :total="allAccounts.length"
        layout="prev, pager, next, jumper"
        background
        size="small"
        style="margin-top:8px;justify-content:center;flex-shrink:0"
        @size-change="accountPage = 1"
      />
    </div>

    <div style="height:1px;background:#e4e7ed;margin:8px 0;flex-shrink:0" />

    <div style="flex:1;min-height:0;display:flex;flex-direction:column">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;flex-shrink:0">
        <div style="display:flex;align-items:center;gap:6px">
          <h3 style="margin:0;font-size:16px">签到日志</h3>
          <span style="color:#909399;font-size:12px">共 {{ logTotal }} 条</span>
        </div>
        <div style="display:flex;gap:6px">
          <el-select v-model="logFilterStatus" placeholder="状态" size="small" clearable style="width:90px">
            <el-option label="全部" value="" /><el-option label="成功" value="success" />
            <el-option label="已签到" value="already" /><el-option label="失败" value="failed" />
          </el-select>
          <el-select v-model="logFilterPlugin" placeholder="社区" size="small" clearable style="width:90px">
            <el-option label="全部" value="" />
            <el-option v-for="p in plugins" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
          <el-date-picker v-model="logFilterDateRange" type="daterange" range-separator="~"
            start-placeholder="开始" end-placeholder="结束" size="small" style="width:200px"
            format="YYYY-MM-DD" value-format="YYYY-MM-DD" />
          <el-button size="small" type="danger" :icon="Delete" @click="handleClearLogs">清除</el-button>
        </div>
      </div>

      <div style="display:flex;gap:20px;margin-bottom:12px;flex-shrink:0">
        <div style="font-size:16px;font-weight:600;color:#67c23a">成功: {{ todaySummary.success }}</div>
        <div style="font-size:16px;font-weight:600;color:#909399">已签到: {{ todaySummary.already }}</div>
        <div style="font-size:16px;font-weight:600;color:#f56c6c">失败: {{ todaySummary.failed }}</div>
        <div style="font-size:16px;font-weight:600;color:#303133">合计: {{ todaySummary.total }}</div>
      </div>

      <div ref="logContainer" style="flex:1;min-height:0;overflow-y:auto;background:#1e1e1e;border-radius:6px;padding:12px 16px;font-family:'Courier New',monospace;font-size:14px;line-height:1.8">
        <div v-for="(l, i) in terminalLog" :key="i" style="white-space:nowrap">
          <span style="color:#569cd6">[{{ l.time }}]</span>
          <span style="color:#4ec9b0;margin-left:6px">{{ l.plugin }}</span>
          <span style="color:#909399">|</span>
          <span style="color:#ce9178">{{ l.game }}</span>
          <span style="color:#909399">|</span>
          <span style="color:#dcdcaa">{{ l.account }}</span>
          <span style="color:#909399">|</span>
          <span style="color:#6a9955">{{ l.elapsed }}</span>
          <span style="color:#909399">|</span>
          <span :style="{ color: statusColor(l.status) }">{{ l.status }}</span>
          <span style="color:#909399"> | </span>
          <span style="color:#c0c4cc">{{ l.msg }}</span>
        </div>
        <div v-if="terminalLog.length === 0" style="color:#6a9955">暂无签到记录</div>
      </div>
    </div>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form label-width="80px">
        <el-form-item label="社区">
          <el-select v-model="form.plugin_id" style="width:100%">
            <el-option v-for="p in plugins" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <template v-if="form.plugin_id === 'kuro'">
          <el-form-item label="Token"><el-input v-model="kuroFields.token" placeholder="eyJhbGci..." /></el-form-item>
          <el-form-item label="User ID"><el-input v-model="kuroFields.user_id" placeholder="15340540" /></el-form-item>
          <el-form-item label="Device"><el-input v-model="kuroFields.devcode" placeholder="a167a07d-..." /></el-form-item>
          <el-form-item label="设备指纹"><el-input v-model="kuroFields.distinct_id" placeholder="d5fafc6b-..." /></el-form-item>
          <el-divider content-position="left">鸣潮</el-divider>
          <el-form-item label="Role ID"><el-input v-model="kuroFields.wuwa.role_id" placeholder="110716118" /></el-form-item>
          <el-divider content-position="left">战双</el-divider>
          <el-form-item label="Role ID"><el-input v-model="kuroFields.pgr.role_id" placeholder="角色ID" /></el-form-item>
        </template>
        <el-form-item label="启用"><el-switch v-model="form.is_enabled" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="scheduleDialog" title="定时签到" width="400px">
      <el-form label-width="60px">
        <el-divider content-position="left">鸣潮</el-divider>
        <el-form-item label="启用"><el-switch v-model="scheduleGames.wuwa.enabled" /></el-form-item>
        <el-form-item label="时间">
          <el-select v-model="scheduleGames.wuwa.cron" style="width:100%" :disabled="!scheduleGames.wuwa.enabled">
            <el-option v-for="p in schedulePresets" :key="p.value" :label="p.label" :value="p.value" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="!schedulePresets.find(p => p.value === scheduleGames.wuwa.cron)" label="自定义">
          <el-input v-model="scheduleGames.wuwa.cron" placeholder="0 7 * * *" :disabled="!scheduleGames.wuwa.enabled" />
        </el-form-item>
        <el-divider content-position="left">战双</el-divider>
        <el-form-item label="启用"><el-switch v-model="scheduleGames.pgr.enabled" /></el-form-item>
        <el-form-item label="时间">
          <el-select v-model="scheduleGames.pgr.cron" style="width:100%" :disabled="!scheduleGames.pgr.enabled">
            <el-option v-for="p in schedulePresets" :key="p.value" :label="p.label" :value="p.value" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="!schedulePresets.find(p => p.value === scheduleGames.pgr.cron)" label="自定义">
          <el-input v-model="scheduleGames.pgr.cron" placeholder="0 7 * * *" :disabled="!scheduleGames.pgr.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="scheduleDialog = false">取消</el-button>
        <el-button type="primary" @click="saveSchedule">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
