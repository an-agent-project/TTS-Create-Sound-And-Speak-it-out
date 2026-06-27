<template>
  <div class="page">
    <h2>作品管理</h2>
    <p v-if="loadError" class="load-error">{{ loadError }}</p>
    <div class="card-grid" v-else-if="works.length">
      <div v-for="w in works" :key="w.id" class="work-card">
        <div class="work-title">{{ w.title }}</div>
        <div class="work-meta">{{ w.voiceName }} · {{ fmtDuration(w.duration) }} · {{ fmtDate(w.createdAt) }}</div>
        <audio v-if="w.audioUrl" :src="w.audioUrl" controls class="work-audio"></audio>
        <button @click="removeWork(w.id)" class="btn-sm danger">删除</button>
      </div>
    </div>
    <p v-else class="empty">暂无作品</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAppStore } from '../../stores/app.js'
const store = useAppStore()
const works = ref([])
const loadError = ref('')

async function load() {
  loadError.value = ''
  const resp = await fetch(`/api/admin/works?pageSize=100`, { headers: store.authHeaders() })
  const data = await resp.json().catch(() => ({}))
  if (!resp.ok) {
    works.value = []
    loadError.value = data.detail || data.message || `加载失败：${resp.status}`
    return
  }
  works.value = data.items || []
}

async function removeWork(id) {
  if (!confirm('确定删除该作品？')) return
  await fetch(`/api/admin/works/${id}`, { method: 'DELETE', headers: store.authHeaders() })
  await load()
}

function fmtDuration(s) {
  if (!s) return '0:00'
  const m = Math.floor(s / 60)
  const sec = Math.floor(s % 60)
  return `${m}:${String(sec).padStart(2, '0')}`
}

function fmtDate(s) {
  if (!s) return ''
  return new Date(s).toLocaleString('zh-CN')
}

onMounted(load)
</script>

<style scoped>
.page h2{font-size:20px;margin-bottom:16px}
.card-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px}
.work-card{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);padding:16px}
.work-title{font-weight:600;font-size:15px;margin-bottom:4px}
.work-meta{font-size:12px;color:var(--text-secondary);margin-bottom:10px}
.work-audio{width:100%;height:36px;margin-bottom:10px}
.btn-sm{padding:4px 16px;border-radius:var(--radius-sm);font-size:12px;border:none;cursor:pointer}
.btn-sm.danger{background:#fed7d7;color:#9b2c2c}
.empty{color:var(--text-secondary);font-size:14px}
.load-error{padding:12px 14px;border:1px solid #feb2b2;border-radius:var(--radius-sm);background:#fff5f5;color:#c53030;font-size:13px}
</style>
