<script setup lang="ts">
import { watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { Lock, Monitor, User, Document } from '@element-plus/icons-vue'

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
        <el-menu
          :default-active="route.path"
          router
          style="border-right:none"
        >
          <el-menu-item index="/dashboard">
            <el-icon><Monitor /></el-icon>
            <template #title>控制面板</template>
          </el-menu-item>
          <el-menu-item index="/credentials">
            <el-icon><User /></el-icon>
            <template #title>凭据管理</template>
          </el-menu-item>
          <el-menu-item index="/logs">
            <el-icon><Document /></el-icon>
            <template #title>签到日志</template>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header style="height:56px;display:flex;align-items:center;justify-content:flex-end;border-bottom:1px solid #e4e7ed;padding:0 20px">
          <span style="margin-right:16px;color:#909399;font-size:13px">已解锁</span>
          <el-button :icon="Lock" text @click="store.lock()">锁定</el-button>
        </el-header>
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
  <router-view v-else />
</template>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body, #app { height: 100%; }
</style>
