<template>
  <div class="page">
    <h2>素材管理</h2>
    <div class="filters">
      <select v-model="category" @change="load">
        <option value="">全部分类</option>
        <option value="bgm">BGM</option>
        <option value="sfx">音效</option>
      </select>
      <input v-model="uploader" placeholder="按上传者筛选..." @keyup.enter="load" class="filter-input" />
      <label class="inactive-toggle"><input type="checkbox" v-model="includeInactive" @change="load" /> 含已删除</label>
    </div>
    <p v-if="loadError" class="load-error">{{ loadError }}</p>
    <table v-else-if="materials.length" class="table">
      <thead><tr><th>ID</th><th>标题</th><th>分类</th><th>上传者</th><th>时间</th><th>状态</th><th>操作</th></tr></thead>
      <tbody>
        <tr v-for="m in materials" :key="m.id" :class="{ inactive: !m.isActive }">
          <td>{{ m.id }}</td>
          <td>{{ m.title }}</td>
          <td>{{ m.category }}</td>
          <td>{{ m.uploader }}</td>
          <td>{{ fmtDate(m.createdAt) }}</td>
          <td><span :class="m.isActive ? 'badge ok' : 'badge del'">{{ m.isActive ? '正常' : '已删' }}</span></td>
          <td class="actions">
            <button v-if="m.isActive" @click="removeMaterial(m.id)" class="btn-sm warn">删除</button>
            <button @click="hardRemove(m.id)" class="btn-sm danger">彻底删除</button>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else class="empty">暂无素材</p>
  <div class="pagination" v-if="totalItems > 0">
    <button @click="prevPage" :disabled="pageNum <= 1">上一页</button>
    <span>{{ pageNum }} / {{ totalPages }}（共 {{ totalItems }} 条）</span>
    <button @click="nextPage" :disabled="pageNum >= totalPages">下一页</button>
  </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { computed } from 'vue'
import { useAppStore } from '../../stores/app.js'
const store = useAppStore()
const materials = ref([])
const category = ref('')
const uploader = ref('')
const includeInactive = ref(false)
const pageNum = ref(1)
const pageSize = ref(15)
const totalItems = ref(0)
const loadError = ref('')
const totalPages = computed(() => Math.ceil(totalItems.value / pageSize.value))

async function load() {
  loadError.value = ''
  const p = new URLSearchParams()
  if (category.value) p.set('category', category.value)
  if (uploader.value) p.set('uploader', uploader.value)
  p.set('page', String(pageNum.value)); p.set('pageSize', String(pageSize.value));
  if (includeInactive.value) p.set('include_inactive', 'true')
  const resp = await fetch(`/api/admin/materials?${p}`, { headers: store.authHeaders() })
  const data = await resp.json().catch(() => ({}))
  if (!resp.ok) {
    materials.value = []
    totalItems.value = 0
    loadError.value = data.detail || data.message || `加载失败：${resp.status}`
    return
  }
  materials.value = data.items || []
  totalItems.value = data.total || 0
}

async function removeMaterial(id) {
  if (!confirm('确定删除该素材？')) return
  await fetch(`/api/admin/materials/${id}`, { method: 'DELETE', headers: store.authHeaders() })
  await load()
}

async function hardRemove(id) {
  if (!confirm('彻底删除不可恢复，确定？')) return
  await fetch(`/api/admin/materials/${id}/permanent`, { method: 'DELETE', headers: store.authHeaders() })
  await load()
}

function fmtDate(s) {
  if (!s) return ''
  return new Date(s).toLocaleString('zh-CN')
}

function prevPage() { if (pageNum.value > 1) { pageNum.value--; load() } }
function nextPage() { if (pageNum.value < totalPages.value) { pageNum.value++; load() } }
onMounted(load)
</script>

<style scoped>
.page h2{font-size:20px;margin-bottom:16px}
.filters{display:flex;gap:10px;margin-bottom:16px;align-items:center}
.filters select,.filter-input{padding:6px 12px;border:1px solid var(--border);border-radius:var(--radius-sm);font-size:13px;background:var(--bg-card);color:var(--text)}
.inactive-toggle{font-size:13px;display:flex;align-items:center;gap:4px;color:var(--text-secondary)}
.table{width:100%;border-collapse:collapse;background:var(--bg-card);border-radius:var(--radius);overflow:hidden;border:1px solid var(--border)}
.table th,.table td{padding:10px 14px;text-align:left;font-size:13px;border-bottom:1px solid var(--border)}
.table th{background:var(--primary-light);color:var(--primary);font-weight:600}
tr.inactive{opacity:.45}
.badge{padding:2px 10px;border-radius:10px;font-size:12px;font-weight:600}
.badge.ok{background:#c6f6d5;color:#22543d}
.badge.del{background:#fed7d7;color:#9b2c2c}
.actions{display:flex;gap:6px}
.btn-sm{padding:4px 12px;border-radius:var(--radius-sm);font-size:12px;border:none;cursor:pointer}
.btn-sm.warn{background:#fefcbf;color:#975a16}
.btn-sm.danger{background:#fed7d7;color:#9b2c2c}
.empty{color:var(--text-secondary);font-size:14px}
.load-error{padding:12px 14px;border:1px solid #feb2b2;border-radius:var(--radius-sm);background:#fff5f5;color:#c53030;font-size:13px}
.pagination{display:flex;align-items:center;gap:12px;margin-top:16px;font-size:13px;color:var(--text-secondary)}
.pagination button{padding:6px 14px;border:1px solid var(--border);border-radius:var(--radius-sm);background:var(--bg-card);cursor:pointer}
.pagination button:disabled{opacity:.4;cursor:default}
</style>
