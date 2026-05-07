<script setup lang="ts">
  import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
  import { fetchPlugins, fetchLogs } from '@/api'

  const plugins = ref<any[]>([])
  const logs = ref<any[]>([])
  const logTotal = ref(0)
  const logPage = ref(1)
  const logPageSize = ref(100)
  const logFilterStatus = ref('')
  const logFilterPlugin = ref('')
  const logFilterDateFrom = ref('')
  const logFilterDateTo = ref('')
  const logContainer = ref<HTMLDivElement>()

  const terminalLog = ref<{ time: string; plugin: string; game: string; account: string; elapsed: string; status: string; msg: string }[]>([])
  let logTimer: ReturnType<typeof setInterval> | undefined

  onMounted(async () => {
    try { plugins.value = await fetchPlugins() } catch { }
    refreshLogs()
    logTimer = setInterval(refreshLogs, 15000)
  })

  onUnmounted(() => {
    if (logTimer) clearInterval(logTimer)
  })

  watch([logPage, logFilterStatus, logFilterPlugin, logFilterDateFrom, logFilterDateTo], refreshLogs)
  watch(terminalLog, async () => {
    await nextTick()
    if (logContainer.value) logContainer.value.scrollTop = logContainer.value.scrollHeight
  }, { deep: true })

  defineExpose({ refreshLogs })

  async function refreshLogs() {
    try {
      const params: any = { page: logPage.value, page_size: logPageSize.value }
      if (logFilterStatus.value) params.status = logFilterStatus.value
      if (logFilterPlugin.value) params.plugin_id = logFilterPlugin.value
      if (logFilterDateFrom.value) params.date_from = logFilterDateFrom.value
      if (logFilterDateTo.value) params.date_to = logFilterDateTo.value
      const logRes = await fetchLogs(params)
      logs.value = logRes.items; logTotal.value = logRes.total
      terminalLog.value = logRes.items.map((r: any) => ({
        time: r.signed_at?.slice(5, 16)?.replace('T', ' ') || '',
        plugin: r.plugin_id || '',
        game: r.game_id || '',
        account: r.credential_name || '#' + r.credential_id,
        elapsed: formatElapsed(r.elapsed),
        status: r.status || '',
        msg: r.message || r.reward || '',
      }))
    } catch { }
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

  function resetFilters() {
    logFilterStatus.value = ''
    logFilterPlugin.value = ''
    logFilterDateFrom.value = ''
    logFilterDateTo.value = ''
    logPage.value = 1
  }
</script>

<template>
  <div style="display:flex;flex-direction:column;height:100%">
    <div style="flex-shrink:0">
      <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px">
        <h3 style="margin:0;font-size:15px;font-weight:600">签到日志</h3>
        <span style="color:#909399;font-size:12px">共 {{ logTotal }} 条</span>
      </div>
      <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:6px">
        <el-select v-model="logFilterStatus" placeholder="状态" size="small" clearable style="flex:1;min-width:90px">
          <el-option label="全部" value="" /><el-option label="成功" value="success" />
          <el-option label="已签到" value="already" /><el-option label="失败" value="failed" />
        </el-select>
        <el-select v-model="logFilterPlugin" placeholder="社区" size="small" clearable style="flex:1;min-width:90px">
          <el-option label="全部" value="" />
          <el-option v-for="p in plugins" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
        <el-date-picker v-model="logFilterDateFrom" type="date" placeholder="开始日期" size="small"
          style="flex:1;min-width:100px" format="YYYY-MM-DD" value-format="YYYY-MM-DD" />
        <el-date-picker v-model="logFilterDateTo" type="date" placeholder="结束日期" size="small"
          style="flex:1;min-width:100px" format="YYYY-MM-DD" value-format="YYYY-MM-DD" />
        <el-button size="small" style="flex-shrink:0" @click="resetFilters">重置</el-button>
      </div>
    </div>
    <div ref="logContainer"
      style="flex:1;min-height:0;overflow-y:auto;background:#1e1e1e;border-radius:6px;padding:10px 14px;font-family:'Courier New',monospace;font-size:13px;line-height:1.7">
      <div v-for="(l, i) in terminalLog" :key="i" style="white-space:pre-wrap;word-break:break-all">
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
</template>
