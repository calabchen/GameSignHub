<script setup lang="ts">
import { useAppStore } from '@/stores/app'

const store = useAppStore()
</script>

<template>
  <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;color:#909399">
    <div style="font-size:48px;margin-bottom:16px;opacity:0.3">🎮</div>
    <h2 style="color:#606266;margin-bottom:8px">欢迎使用 GameSignHub</h2>
    <p style="font-size:14px;margin-bottom:4px">请从左侧选择一个游戏开始</p>
    <p style="font-size:12px;color:#c0c4cc;margin-top:16px">
      已加载 {{ store.plugins.length }} 个社区 | {{ store.plugins.reduce((s, p) => s + p.supported_games.length, 0) }} 个游戏
    </p>
  </div>
</template>
