<template>
  <div class="page">
    <h2>服务状态</h2>
    <div class="status-grid" v-if="data">
      <div class="status-card" v-for="(check, key) in data.checks" :key="key">
        <div class="card-header">
          <span class="card-label">{{ labelOf(key) }}</span>
          <span :class="statusClass(check.status)">{{ statusText(check.status) }}</span>
        </div>
        <div class="card-body">
          <template v-if="key === 'disk' && check.free_gb">
            <p>可用: {{ check.free_gb }} GB / {{ check.total_gb }} GB</p>
          </template>
          <template v-if="check.detail">
            <p class="detail">{{ check.detail }}</p>
          </template>
        </div>
      </div>
    </div>
    <div v-if="data" class="overall" :class="data.status === 'ok' ? 'green' : 'yellow'">
      系统整体状态: {{ data.status === 'ok' ? '正常' : '部分异常' }}
    </div>
    <p v-else class="empty">加载中...</p>
    <button @click="load" class="refresh-btn">刷新</button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAppStore } from '../../stores/app.js'
const store = useAppStore()
const data = ref(null)

const LABELS = {
  database: '数据库',
  disk: '磁盘存储',
  edge_tts: 'Edge-TTS',
  bailian_tts: '百炼 TTS',
}

function labelOf(k) { return LABELS[k] || k }

function statusClass(s) {
  if (s === 'ok' || s === 'configured') return 'badge ok'
  if (s === 'degraded') return 'badge warn'
  return 'badge err'
}

function statusText(s) {
  if (s === 'ok') return '正常'
  if (s === 'configured') return '已配置'
  if (s === 'not_configured') return '未配置'
  if (s === 'not_installed') return '未安装'
  return '异常'
}

async function load() {
  const resp = await fetch('/api/admin/health', { headers: store.authHeaders() })
  data.value = await resp.json()
}

onMounted(load)
</script>

<style scoped>
.page h2{font-size:20px;margin-bottom:16px}
.status-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:16px;margin-bottom:20px}
.status-card{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);padding:16px}
.card-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.card-label{font-weight:600;font-size:14px}
.card-body p{font-size:13px;color:var(--text-secondary);margin:0}
.card-body .detail{font-size:12px;color:#c53030}
.badge{padding:2px 10px;border-radius:10px;font-size:12px;font-weight:600}
.badge.ok{background:#c6f6d5;color:#22543d}
.badge.warn{background:#fefcbf;color:#975a16}
.badge.err{background:#fed7d7;color:#9b2c2c}
.overall{padding:12px 18px;border-radius:var(--radius);font-weight:600;font-size:14px;margin-bottom:12px}
.overall.green{background:#c6f6d5;color:#22543d}
.overall.yellow{background:#fefcbf;color:#975a16}
.refresh-btn{padding:8px 20px;background:var(--primary);color:#fff;border:none;border-radius:var(--radius-sm);cursor:pointer;font-size:14px}
.empty{color:var(--text-secondary);font-size:14px}
</style>
