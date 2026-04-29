<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { api } from '@/api'
import { ElMessage } from 'element-plus'
import { Lock, User, Monitor } from '@element-plus/icons-vue'
import DashboardView from '@/views/Dashboard.vue'
import CredentialsView from '@/views/Credentials.vue'

const router = useRouter()
const store = useAppStore()
const activeTab = ref('dashboard')

const pwdDialog = ref(false)
const pwdForm = reactive({ old: '', new1: '', new2: '' })

async function changePassword() {
  if (pwdForm.new1 !== pwdForm.new2) { ElMessage.warning('两次输入的新密码不一致'); return }
  try {
    await api.put('/api/unlock/password', { old_password: pwdForm.old, new_password: pwdForm.new1 })
    ElMessage.success('密码已修改')
    pwdDialog.value = false
    pwdForm.old = ''; pwdForm.new1 = ''; pwdForm.new2 = ''
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '修改失败')
  }
}

async function handleLock() {
  await store.lock()
  router.replace('/')
}
</script>

<template>
  <el-container style="flex-direction:column;height:100%">
    <el-header style="height:48px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #e4e7ed;padding:0 16px;flex-shrink:0">
      <span style="font-size:16px;font-weight:600;color:#303133">游戏签到中心</span>
      <div style="display:flex;align-items:center;gap:8px">
        <span style="color:#909399;font-size:13px">admin</span>
        <el-button text size="small" type="primary" @click="pwdDialog = true">改密</el-button>
        <el-button text size="small" @click="handleLock">锁定</el-button>
      </div>
    </el-header>

    <el-main style="flex:1;overflow-y:auto;padding:12px 16px">
      <DashboardView v-if="activeTab === 'dashboard'" />
      <CredentialsView v-if="activeTab === 'accounts'" />

      <div v-if="activeTab === 'password'" style="max-width:360px;margin:0 auto">
        <h3 style="margin-bottom:16px">修改密码</h3>
        <el-form label-width="80px">
          <el-form-item label="旧密码">
            <el-input v-model="pwdForm.old" type="password" show-password />
          </el-form-item>
          <el-form-item label="新密码">
            <el-input v-model="pwdForm.new1" type="password" show-password />
          </el-form-item>
          <el-form-item label="确认密码">
            <el-input v-model="pwdForm.new2" type="password" show-password />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="changePassword">确认修改</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-main>

    <el-footer style="height:auto;padding:0;border-top:1px solid #e4e7ed;flex-shrink:0">
      <div style="display:flex">
        <div
          v-for="tab in [
            { key: 'accounts', label: '账户管理', icon: User },
            { key: 'dashboard', label: '控制面板', icon: Monitor },
            { key: 'password', label: '修改密码', icon: Lock },
          ]"
          :key="tab.key"
          @click="activeTab = tab.key"
          style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:8px 0;cursor:pointer"
          :style="{ color: activeTab === tab.key ? '#409eff' : '#909399' }"
        >
          <el-icon :size="20"><component :is="tab.icon" /></el-icon>
          <span style="font-size:11px;margin-top:2px">{{ tab.label }}</span>
        </div>
      </div>
    </el-footer>
  </el-container>
</template>
