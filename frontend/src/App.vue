<script setup lang="ts">
  import { watch, onMounted, ref } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { useAppStore } from '@/stores/app'
  import { Lock, Monitor, User, Document, Key } from '@element-plus/icons-vue'
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

  // ------ 修改密码 ------
  const passwordDialog = ref(false)
  const pwdForm = ref({ old: '', new1: '', new2: '' })

  async function changePassword() {
    if (pwdForm.value.new1 !== pwdForm.value.new2) {
      ElMessage.warning('两次输入的新密码不一致')
      return
    }
    try {
      await api.put('/api/unlock/password', {
        old_password: pwdForm.value.old,
        new_password: pwdForm.value.new1,
      })
      ElMessage.success('密码已修改')
      passwordDialog.value = false
      pwdForm.value = { old: '', new1: '', new2: '' }
    } catch (e: any) {
      ElMessage.error(e.response?.data?.detail || '修改失败')
    }
  }
</script>

<template>
  <div v-if="!store.isReady" style="display:flex;align-items:center;justify-content:center;height:100%">
    <span style="color:#c0c4cc;font-size:14px">连接中...</span>
  </div>
  <div v-else-if="store.isUnlocked" style="height:100%">
    <el-container style="height:100%">
      <el-aside width="200px">
        <div style="height:56px;display:flex;align-items:center;padding:0 20px;border-bottom:1px solid #e4e7ed">
          <span style="font-size:16px;font-weight:600;color:#303133">游戏签到中心</span>
        </div>
        <el-menu :default-active="route.path" router style="border-right:none">
          <el-menu-item index="/dashboard">
            <el-icon>
              <Monitor />
            </el-icon>
            <template #title>控制面板</template>
          </el-menu-item>
          <el-menu-item index="/credentials">
            <el-icon>
              <User />
            </el-icon>
            <template #title>账户管理</template>
          </el-menu-item>
          <el-menu-item index="/logs">
            <el-icon>
              <Document />
            </el-icon>
            <template #title>签到日志</template>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header
          style="height:56px;display:flex;align-items:center;justify-content:flex-end;border-bottom:1px solid #e4e7ed;padding:0 20px">
          <span style="margin-right:16px;color:#909399;font-size:13px">已解锁</span>
          <el-button :icon="Key" text @click="passwordDialog = true" style="margin-right:8px">改密</el-button>
          <el-button :icon="Lock" text @click="store.lock()">锁定</el-button>
        </el-header>
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>

    <el-dialog v-model="passwordDialog" title="修改密码" width="360px">
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
      </el-form>
      <template #footer>
        <el-button @click="passwordDialog = false">取消</el-button>
        <el-button type="primary" @click="changePassword">确认修改</el-button>
      </template>
    </el-dialog>
  </div>
  <router-view v-else />
</template>

<style>
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  html,
  body,
  #app {
    height: 100%;
  }
</style>
