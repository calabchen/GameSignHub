<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { fetchPlugins } from '@/api'
import { pinyinSort, getInitial, ALPHABET } from '@/utils/pinyin'
import { gameColor, gameGradient } from '@/utils/color'
import AccountTable from '@/components/AccountTable.vue'
import LogTerminal from '@/components/LogTerminal.vue'
import WelcomePage from '@/components/WelcomePage.vue'
import ChangePasswordForm from '@/components/ChangePasswordForm.vue'

const router = useRouter()
const store = useAppStore()
const logRef = ref<InstanceType<typeof LogTerminal> | null>(null)
const highlightLetter = ref('')

const treeData = computed(() => {
  return pinyinSort(store.plugins, p => p.name).map(plugin => ({
    id: `plugin-${plugin.id}`,
    label: plugin.name,
    type: 'community',
    children: pinyinSort(plugin.supported_games, g => g.name).map(game => ({
      id: `game-${plugin.id}-${game.id}`,
      label: game.name,
      type: 'game',
      icon: game.icon,
      gameId: game.id,
      pluginId: plugin.id,
      pluginName: plugin.name,
    })),
  }))
})

function hasItem(letter: string): boolean {
  return treeData.value.some(c =>
    (c.children || []).some(g => getInitial(g.label) === letter)
  )
}

function isHighlighted(data: any): boolean {
  if (!highlightLetter.value || data.type !== 'game') return false
  return getInitial(data.label) === highlightLetter.value
}

function handleAZClick(letter: string) {
  highlightLetter.value = highlightLetter.value === letter ? '' : letter
}

function handleNodeClick(data: any) {
  if (data.type === 'community') {
    highlightLetter.value = ''
  } else {
    store.setSelectedGame({
      gameId: data.gameId,
      gameName: data.label,
      gameIcon: data.icon,
      pluginId: data.pluginId,
      pluginName: data.pluginName,
    })
  }
}

async function handleLock() {
  await store.lock()
  router.replace('/')
}

function showChangePwd() {
  store.showChangePassword = true
}

function refreshLogs() {
  logRef.value?.refreshLogs()
}

const headerGradient = computed(() => {
  if (store.showChangePassword || !store.selectedGame) return 'linear-gradient(90deg, #f5f7fa, #e4e7ed)'
  return gameGradient(store.selectedGame.gameId)
})

const headerLabel = computed(() => {
  if (store.showChangePassword) return '修改密码'
  if (store.selectedGame) return store.selectedGame.gameName
  return '游戏签到中心'
})

onMounted(async () => {
  try { store.plugins = await fetchPlugins() } catch {}
})
</script>

<template>
<el-container style="height:100vh">
  <el-aside width="300px" style="background:#fff;border-right:1px solid #e4e7ed;display:flex;flex-direction:column">
    <div style="height:48px;display:flex;align-items:center;justify-content:center">
      <div class="rainbow-title">GameSignHub</div>
    </div>
    <el-divider style="margin:0" />

    <div style="flex:1;overflow:hidden;position:relative;display:flex;min-height:0">
      <div style="flex:1;overflow-y:auto;padding:4px 8px 4px 8px">
        <el-tree
          :data="treeData"
          node-key="id"
          :highlight-current="false"
          :expand-on-click-node="true"
          default-expand-all
          @node-click="handleNodeClick"
        >
          <template #default="{ data }">
            <div v-if="data.type === 'community'" class="tree-community">
              <span>{{ data.label }}</span>
            </div>
            <div
              v-else
              class="tree-game"
              :class="{
                active: store.selectedGame?.gameId === data.gameId && store.selectedGame?.pluginId === data.pluginId,
                highlighted: isHighlighted(data),
              }"
            >
              <img :src="data.icon" class="tree-game-icon" />
              <span>{{ data.label }}</span>
            </div>
          </template>
        </el-tree>
      </div>

      <div style="width:28px;display:flex;flex-direction:column;align-items:flex-start;flex-shrink:0;user-select:none;gap:1px;padding:4px 2px;border-left:1px dashed var(--el-border-color-lighter);justify-content:center">
        <div
          class="az-letter all"
          :class="{ active: !highlightLetter }"
          @click="highlightLetter = ''"
        >All</div>
        <div
          v-for="letter in ALPHABET" :key="letter"
          class="az-letter"
          :class="{ disabled: !hasItem(letter), active: highlightLetter === letter }"
          @click="handleAZClick(letter)"
        >{{ letter }}</div>
      </div>
    </div>

    <el-divider style="margin:0" />
    <div style="padding:12px 14px;display:flex;flex-direction:column;gap:8px;align-items:center">
      <el-button type="warning" plain @click="showChangePwd">
        修改密码
      </el-button>
      <el-button type="danger" plain @click="handleLock">
        锁定屏幕
      </el-button>
    </div>
  </el-aside>

  <el-container>
    <el-header
      style="height:48px;display:flex;align-items:center;padding:0 16px;border-bottom:1px solid #e4e7ed;flex-shrink:0"
      :style="{ background: headerGradient }"
    >
      <div v-if="store.selectedGame && !store.showChangePassword" style="display:flex;align-items:center;gap:8px">
        <img :src="store.selectedGame.gameIcon" style="width:24px;height:24px;border-radius:6px;object-fit:cover" />
        <span style="font-size:16px;font-weight:600" :style="{ color: gameColor(store.selectedGame.gameId) }">
          {{ headerLabel }}
        </span>
      </div>
      <span v-else style="font-size:16px;font-weight:600;color:#303133">{{ headerLabel }}</span>
    </el-header>

    <el-main style="padding:12px 16px;display:flex;flex-direction:column;overflow:hidden">
      <WelcomePage v-if="!store.selectedGame && !store.showChangePassword" />
      <ChangePasswordForm v-else-if="store.showChangePassword" />
      <template v-else>
        <div style="height:50%;padding-bottom:8px;display:flex;flex-direction:column;min-height:0">
          <AccountTable :plugin-id="store.selectedGame?.pluginId || ''" @refresh-logs="refreshLogs" />
        </div>
        <div style="height:1px;background:#e4e7ed;flex-shrink:0;margin:0" />
        <div style="height:50%;padding-top:8px;display:flex;flex-direction:column;min-height:0">
          <LogTerminal ref="logRef" />
        </div>
      </template>
    </el-main>
  </el-container>
</el-container>
</template>

<style>
.rainbow-title {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 1px;
  background: linear-gradient(90deg,
    #FF0000, #FF7F00, #FFFF00, #00FF00,
    #00E5FF, #0000FF, #8B00FF, #FF0000);
  background-size: 200% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: rainbow-shift 4s linear infinite;
}

@keyframes rainbow-shift {
  to { background-position: 200% center; }
}

.el-tree-node:not(:last-child) {
  margin-bottom: 12px;
}

.el-tree-node__children {
  padding-top: 8px;
}
</style>

<style scoped>
.tree-community {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  padding: 2px 0;
}

.tree-game {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 6px;
  border-radius: 6px;
  font-size: 16px;
  color: #606266;
  cursor: pointer;
  transition: all 0.15s;
  word-break: break-word;
}
.tree-game:hover {
  background: #f0f5ff;
  color: #409eff;
}
.tree-game.active {
  background: #ecf5ff;
  color: #409eff;
  font-weight: 600;
}
.tree-game.highlighted {
  background: linear-gradient(135deg, #fff8e1, #fff3cd);
  border: 2px solid #f0ad4e;
  border-radius: 8px;
}

.tree-game-icon {
  width: 22px;
  height: 22px;
  border-radius: 6px;
  object-fit: cover;
  flex-shrink: 0;
}

.az-letter.all {
  font-weight: 700;
  padding-bottom: 4px;
  margin-bottom: 4px;
  border-bottom: 1px solid #dcdfe6;
}

.az-letter {
  font-size: 12px;
  line-height: 1.2;
  color: #909399;
  cursor: pointer;
  padding: 1px 2px;
  border-radius: 3px;
  transition: all 0.15s;
}
.az-letter:hover:not(.disabled) {
  color: #409eff;
  background: #ecf5ff;
}
.az-letter.disabled {
  color: #dcdfe6;
  cursor: default;
}
.az-letter.active {
  color: #fff;
  background: #409eff;
  font-weight: 700;
}

</style>
