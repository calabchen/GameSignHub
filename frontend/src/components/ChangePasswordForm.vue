<script setup lang="ts">
import { reactive, ref } from 'vue'
import { api } from '@/api'
import { ElMessage } from 'element-plus'
import { useAppStore } from '@/stores/app'

const store = useAppStore()
const pwdForm = reactive({ old: '', new1: '', new2: '' })
const loading = ref(false)

async function changePassword() {
  if (pwdForm.new1 !== pwdForm.new2) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }
  try {
    await api.put('/api/unlock/password', { old_password: pwdForm.old, new_password: pwdForm.new1 })
    ElMessage.success('密码已修改')
    pwdForm.old = ''
    pwdForm.new1 = ''
    pwdForm.new2 = ''
    store.showChangePassword = false
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '修改失败')
  }
}

function handleCancel() {
  store.showChangePassword = false
}
</script>

<template>
  <div style="max-width:400px;margin:40px auto">
    <h3 style="margin-bottom:24px;font-size:18px;color:#303133">修改密码</h3>
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
        <div style="display:flex;gap:8px">
          <el-button type="primary" @click="changePassword">确认修改</el-button>
          <el-button @click="handleCancel">取消</el-button>
        </div>
      </el-form-item>
    </el-form>
  </div>
</template>
