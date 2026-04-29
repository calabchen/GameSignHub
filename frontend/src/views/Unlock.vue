<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { ElMessage } from 'element-plus'

const router = useRouter()
const store = useAppStore()
const password = ref('')
const loading = ref(false)

async function handleUnlock() {
  if (!password.value) return
  loading.value = true
  try {
    const result = await store.unlock(password.value)
    if (result.ok) {
      router.push('/dashboard')
    } else {
      ElMessage.error('密码错误')
      password.value = ''
    }
  } catch {
    ElMessage.error('无法连接后端服务')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div style="display:flex;align-items:center;justify-content:center;height:100%;background:#f5f7fa">
    <el-card style="width:420px">
      <template #header>
        <div style="text-align:center">
          <h2 style="margin:0;color:#303133">游戏签到中心</h2>
          <p style="margin:4px 0 0;color:#909399;font-size:13px">GameSignHub v0.3</p>
        </div>
      </template>

      <el-alert
        v-if="!store.isPasswordSet"
        title="初始设置 — 创建主密码"
        type="info"
        :closable="false"
        style="margin-bottom:16px"
      />
      <el-alert
        v-else
        title="系统已锁定 — 请输入密码"
        type="warning"
        :closable="false"
        style="margin-bottom:16px"
      />

      <el-input
        v-model="password"
        type="password"
        :placeholder="store.isPasswordSet ? '主密码' : '设置主密码'"
        show-password
        size="large"
        @keyup.enter="handleUnlock"
      />

      <el-button
        type="primary"
        size="large"
        :loading="loading"
        style="width:100%;margin-top:16px"
        @click="handleUnlock"
      >
        {{ store.isPasswordSet ? '解锁' : '初始化' }}
      </el-button>

      <p style="text-align:center;margin-top:20px;color:#c0c4cc;font-size:12px">
        默认密码: abcdefgh &nbsp;|&nbsp; 本地服务 · 127.0.0.1:18000
      </p>
    </el-card>
  </div>
</template>
