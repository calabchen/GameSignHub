<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import {
  fetchPlugins, fetchCredentials, createCredential, updateCredential, deleteCredential,
  signCredential,
  fetchCredentialSchedule, updateCredentialSchedule, fetchCredentialDetail,
} from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Timer, CopyDocument } from '@element-plus/icons-vue'

const props = withDefaults(defineProps<{ pluginId?: string }>(), { pluginId: '' })

const emit = defineEmits<{ refreshLogs: [] }>()

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

const accountPage = ref(1)
const accountPageSize = ref(5)

const filteredAccounts = computed(() => {
  if (!props.pluginId) return allAccounts.value
  return allAccounts.value.filter((a: any) => a.plugin_id === props.pluginId)
})

const pagedAccounts = computed(() => {
  const start = (accountPage.value - 1) * accountPageSize.value
  return filteredAccounts.value.slice(start, start + accountPageSize.value)
})

const scheduleDialog = ref(false)
const scheduleCredId = ref<number | null>(null)
const schedulePlugin = ref('')
const scheduleGames = reactive({
  wuwa: { cron: '', enabled: false },
  pgr: { cron: '', enabled: false },
})
const signingGame = ref<string | null>(null)

const schedulePresets = [
  { label: '每天 07:00', value: '0 7 * * *' },
  { label: '每天 08:00', value: '0 8 * * *' },
  { label: '每天 12:00', value: '0 12 * * *' },
  { label: '每天 18:00', value: '0 18 * * *' },
  { label: '每天 22:00', value: '0 22 * * *' },
]

onMounted(async () => {
  try { plugins.value = await fetchPlugins() } catch {}
  try { allAccounts.value = await fetchCredentials() } catch {}
  accountPage.value = 1
})

watch(() => props.pluginId, () => { accountPage.value = 1 })

function pluginName(id: string) { return plugins.value.find((p: any) => p.id === id)?.name || id }

function copyToClipboard(text: string) {
  navigator.clipboard.writeText(text)
  ElMessage.success('已复制')
}

function roleOptions(account: any) {
  const opts: { label: string; value: string }[] = []
  if (account.wuwa_role_id) opts.push({ label: '鸣潮', value: account.wuwa_role_id })
  if (account.pgr_role_id) opts.push({ label: '战双', value: account.pgr_role_id })
  return opts
}

function roleSelectModel(account: any) {
  const opts = roleOptions(account)
  return opts.length > 0 ? opts[0].value : ''
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

async function openSignSchedule(account: any) {
  scheduleCredId.value = account.id
  schedulePlugin.value = account.plugin_id
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

async function handleSignGame(game: string) {
  if (scheduleCredId.value == null || !schedulePlugin.value) return
  signingGame.value = game
  try {
    await signCredential(schedulePlugin.value, scheduleCredId.value, game)
    ElMessage.success(`${game === 'wuwa' ? '鸣潮' : '战双'} 签到完成`)
    emit('refreshLogs')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '签到失败')
  } finally { signingGame.value = null }
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
</script>

<template>
<div style="display:flex;flex-direction:column;height:100%">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;flex-shrink:0">
    <div style="display:flex;align-items:center;gap:8px">
      <h3 style="margin:0;font-size:15px;font-weight:600">账户管理</h3>
      <span style="color:#909399;font-size:12px">{{ filteredAccounts.length }} 个账户</span>
    </div>
    <el-button size="small" type="primary" :icon="Plus" @click="openAdd">添加账户</el-button>
  </div>
  <div style="flex:1;min-height:0;overflow-y:auto">
    <el-table :data="pagedAccounts" stripe empty-text="暂无数据" size="small" style="width:100%">
      <el-table-column label="社区" width="60">
        <template #default="{ row }"><el-tag size="small" effect="dark">{{ pluginName(row.plugin_id) }}</el-tag></template>
      </el-table-column>
      <el-table-column label="User ID" min-width="100">
        <template #default="{ row }">
          <span style="display:inline-flex;align-items:center;gap:4px">
            <span>{{ row.user_id || '未设置' }}</span>
            <el-button v-if="row.user_id" text size="small" :icon="CopyDocument" @click="copyToClipboard(row.user_id)" />
          </span>
        </template>
      </el-table-column>
      <el-table-column label="角色 ID" min-width="130">
        <template #default="{ row }">
          <span v-if="roleOptions(row).length > 0" style="display:inline-flex;align-items:center;gap:4px">
            <el-select :model-value="roleSelectModel(row)" size="small" style="width:100px" disabled>
              <el-option v-for="r in roleOptions(row)" :key="r.value" :label="r.label" :value="r.value" />
            </el-select>
            <el-button text size="small" :icon="CopyDocument" @click="copyToClipboard(roleSelectModel(row))" />
          </span>
          <span v-else style="color:#c0c4cc">未设置</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" min-width="150" fixed="right">
        <template #default="{ row }">
          <el-button size="small" text :icon="Timer" @click="openSignSchedule(row)">签到&定时</el-button>
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
  <el-pagination
    v-if="filteredAccounts.length > 0"
    v-model:current-page="accountPage"
    v-model:page-size="accountPageSize"
    :total="filteredAccounts.length"
    layout="prev, pager, next, jumper"
    background
    size="small"
    style="margin-top:4px;justify-content:center;flex-shrink:0"
  />

  <el-dialog v-model="dialogVisible" :title="dialogTitle" width="90%" style="max-width:500px">
    <el-form label-width="65px">
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

  <el-dialog v-model="scheduleDialog" title="签到 & 定时" width="90%" style="max-width:420px">
    <div style="margin-bottom:16px">
      <div style="font-weight:600;margin-bottom:8px;color:#303133">鸣潮</div>
      <div style="display:flex;gap:8px;align-items:center;margin-bottom:8px">
        <el-button size="small" type="primary" :loading="signingGame === 'wuwa'" @click="handleSignGame('wuwa')">立即签到鸣潮</el-button>
        <el-switch v-model="scheduleGames.wuwa.enabled" />
        <el-select v-model="scheduleGames.wuwa.cron" size="small" style="flex:1;min-width:0" :disabled="!scheduleGames.wuwa.enabled">
          <el-option v-for="p in schedulePresets" :key="p.value" :label="p.label" :value="p.value" />
        </el-select>
      </div>
      <el-input v-if="!schedulePresets.find(p => p.value === scheduleGames.wuwa.cron)" v-model="scheduleGames.wuwa.cron" placeholder="0 7 * * *" size="small" :disabled="!scheduleGames.wuwa.enabled" />
    </div>
    <el-divider />
    <div style="margin-bottom:16px">
      <div style="font-weight:600;margin-bottom:8px;color:#303133">战双</div>
      <div style="display:flex;gap:8px;align-items:center;margin-bottom:8px">
        <el-button size="small" type="primary" :loading="signingGame === 'pgr'" @click="handleSignGame('pgr')">立即签到战双</el-button>
        <el-switch v-model="scheduleGames.pgr.enabled" />
        <el-select v-model="scheduleGames.pgr.cron" size="small" style="flex:1;min-width:0" :disabled="!scheduleGames.pgr.enabled">
          <el-option v-for="p in schedulePresets" :key="p.value" :label="p.label" :value="p.value" />
        </el-select>
      </div>
      <el-input v-if="!schedulePresets.find(p => p.value === scheduleGames.pgr.cron)" v-model="scheduleGames.pgr.cron" placeholder="0 7 * * *" size="small" :disabled="!scheduleGames.pgr.enabled" />
    </div>
    <template #footer>
      <el-button @click="scheduleDialog = false">关闭</el-button>
      <el-button type="primary" @click="saveSchedule">保存定时</el-button>
    </template>
  </el-dialog>
</div>
</template>
