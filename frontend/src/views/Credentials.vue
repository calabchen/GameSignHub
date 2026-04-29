<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  fetchPlugins, fetchCredentials,
  createCredential, updateCredential, deleteCredential, validateCredential,
  signCredential, signAll,
} from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, VideoPlay } from '@element-plus/icons-vue'

const route = useRoute()
const plugins = ref<any[]>([])
const allCredentials = ref<any[]>([])
const filterPlugin = ref('')
const dialogVisible = ref(false)
const dialogTitle = ref('添加凭据')

const form = reactive({
  id: null as number | null,
  plugin_id: 'kuro',
  display_name: '',
  credentials_json: '',
  enabled_games: [] as string[],
  is_enabled: true,
})

const signLoading = ref<number | null>(null)
const signAllLoading = ref(false)

async function handleSign(credId: number) {
  signLoading.value = credId
  try {
    await signCredential(credId)
    ElMessage.success('签到完成')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '签到失败')
  } finally {
    signLoading.value = null
  }
}

async function handleSignAll() {
  signAllLoading.value = true
  try {
    await signAll()
    ElMessage.success('全部签到完成')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '签到失败')
  } finally {
    signAllLoading.value = false
  }
}

onMounted(async () => {
  try { plugins.value = await fetchPlugins() } catch {}
  try { allCredentials.value = await fetchCredentials() } catch {}
  filterPlugin.value = (route.query.plugin as string) || ''
})

const filteredCredentials = () => {
  if (!filterPlugin.value) return allCredentials.value
  return allCredentials.value.filter((c: any) => c.plugin_id === filterPlugin.value)
}

watch(() => route.query.plugin, (v) => {
  filterPlugin.value = (v as string) || ''
})

function pluginName(id: string) {
  return plugins.value.find((p: any) => p.id === id)?.name || id
}

function openAdd() {
  dialogTitle.value = '添加凭据'
  form.id = null
  form.plugin_id = filterPlugin.value || 'kuro'
  form.display_name = ''
  form.credentials_json = ''
  form.enabled_games = []
  form.is_enabled = true
  dialogVisible.value = true
}

function openEdit(cred: any) {
  dialogTitle.value = '编辑凭据'
  form.id = cred.id
  form.plugin_id = cred.plugin_id
  form.display_name = cred.display_name
  form.credentials_json = ''
  form.enabled_games = [...(cred.enabled_games || [])]
  form.is_enabled = cred.is_enabled
  dialogVisible.value = true
}

async function handleSave() {
  let raw = {}
  try {
    if (form.credentials_json.trim()) raw = JSON.parse(form.credentials_json)
  } catch { ElMessage.error('JSON 格式错误'); return }

  const payload: any = {
    plugin_id: form.plugin_id,
    display_name: form.display_name,
    credentials: raw,
    enabled_games: form.enabled_games,
    is_enabled: form.is_enabled,
  }

  try {
    if (form.id) {
      await updateCredential(form.id, payload)
      ElMessage.success('已更新')
    } else {
      await createCredential(payload)
      ElMessage.success('已创建')
    }
    dialogVisible.value = false
    try { allCredentials.value = await fetchCredentials() } catch {}
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  }
}

async function handleDelete(cred: any) {
  try {
    await ElMessageBox.confirm('确定删除此凭据？', '确认', { type: 'warning' })
    await deleteCredential(cred.id)
    ElMessage.success('已删除')
    try { allCredentials.value = await fetchCredentials() } catch {}
  } catch {}
}

async function handleValidate(cred: any) {
  try {
    const res = await validateCredential(cred.id)
    if (res.valid) ElMessage.success('凭据有效')
    else ElMessage.warning('无效: ' + res.message)
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '验证失败')
  }
}
</script>

<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <div style="display:flex;align-items:center;gap:16px">
        <h2 style="margin:0;font-size:20px">凭据管理</h2>
        <el-select v-model="filterPlugin" placeholder="全部社区" size="small" clearable style="width:150px">
          <el-option v-for="p in plugins" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
        <span style="color:#909399;font-size:13px">{{ filteredCredentials().length }} 个凭据</span>
      </div>
      <div style="display:flex;gap:8px">
        <el-button type="primary" :icon="VideoPlay" :loading="signAllLoading" @click="handleSignAll" :disabled="filteredCredentials().length === 0">
          全部签到
        </el-button>
        <el-button type="primary" :icon="Plus" @click="openAdd">添加凭据</el-button>
      </div>
    </div>

    <el-table :data="filteredCredentials()" stripe empty-text="暂无数据">
      <el-table-column label="社区" width="120">
        <template #default="{ row }">
          <el-tag size="small" effect="dark">{{ pluginName(row.plugin_id) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="名称" min-width="120">
        <template #default="{ row }">{{ row.display_name || '#' + row.id }}</template>
      </el-table-column>
      <el-table-column label="游戏" min-width="160">
        <template #default="{ row }">
          <el-tag v-for="g in row.enabled_games" :key="g" size="small" style="margin-right:4px">{{ g }}</el-tag>
          <span v-if="!row.enabled_games?.length" style="color:#c0c4cc">全部</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-switch :model-value="row.is_enabled" size="small" disabled />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="290" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" :loading="signLoading === row.id" @click="handleSign(row.id)">签到</el-button>
          <el-button size="small" @click="handleValidate(row)">验证</el-button>
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form label-width="80px">
        <el-form-item label="社区">
          <el-select v-model="form.plugin_id" style="width:100%">
            <el-option v-for="p in plugins" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="名称">
          <el-input v-model="form.display_name" placeholder="例如：大号" />
        </el-form-item>
        <el-form-item label="凭据内容">
          <el-input
            v-model="form.credentials_json"
            type="textarea"
            :rows="4"
            placeholder='{"token":"你的token"}'
          />
          <span style="color:#909399;font-size:11px;margin-top:4px;display:block">
            库街区: {"token":"..."} &nbsp;|&nbsp; 米游社: {"cookie":"...","stoken":"..."}
          </span>
        </el-form-item>
        <el-form-item label="游戏">
          <el-checkbox-group v-model="form.enabled_games">
            <el-checkbox
              v-for="g in (plugins.find(p=>p.id===form.plugin_id)?.supported_games || [])"
              :key="g.id"
              :label="g.id"
              :value="g.id"
            >{{ g.name || g.id }}</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.is_enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
