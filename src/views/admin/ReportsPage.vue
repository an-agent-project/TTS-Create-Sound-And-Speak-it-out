<template>
  <div class="page">
    <h2>举报审核</h2>
    <div class="tabs">
      <button :class="{ active: statusTab === '' }" @click="statusTab = ''; load()">全部</button>
      <button :class="{ active: statusTab === 'pending' }" @click="statusTab = 'pending'; load()">待处理</button>
      <button :class="{ active: statusTab === 'reviewed' }" @click="statusTab = 'reviewed'; load()">已处理</button>
      <button :class="{ active: statusTab === 'dismissed' }" @click="statusTab = 'dismissed'; load()">已驳回</button>
    </div>
    <table v-if="reports.length" class="table">
      <thead><tr><th>素材</th><th>举报人</th><th>原因</th><th>详情</th><th>时间</th><th>操作</th></tr></thead>
      <tbody>
        <tr v-for="r in reports" :key="r.id">
          <td>{{ r.materialTitle }}</td>
          <td>{{ r.reporterName }}</td>
          <td><span class="reason-tag">{{ reasonLabel(r.reasonCategory) }}</span></td>
          <td class="detail">{{ r.reasonDetail || '-' }}</td>
          <td>{{ fmtDate(r.createdAt) }}</td>
          <td class="actions" v-if="r.status === 'pending'">
            <button @click="review(r.id, 'delete_material')" class="btn-sm danger">删除素材</button>
            <button @click="review(r.id, 'dismiss')" class="btn-sm">驳回</button>
          </td>
          <td v-else>
            <span :class="r.status === 'reviewed' ? 'badge ok' : 'badge dim'">{{ r.status === 'reviewed' ? '已处理' : '已驳回' }}</span>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else class="empty">暂无举报</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAppStore } from '../../stores/app.js'
const store = useAppStore()
const reports = ref([])
const statusTab = ref('pending')

const REASON_MAP = {
  pornography: '色情',
  violence: '暴力',
  political: '政治敏感',
  copyright: '侵权',
  other: '其他',
}

function reasonLabel(c) { return REASON_MAP[c] || c }

async function load() {
  const p = new URLSearchParams()
  p.set('pageSize', '50');
  if (statusTab.value) p.set('status', statusTab.value)
  const resp = await fetch(`/api/admin/reports?${p}`, { headers: store.authHeaders() })
  const data = await resp.json(); reports.value = data.items || []
}

async function review(id, action) {
  if (!confirm(action === 'delete_material' ? '确定删除该素材？' : '确定驳回该举报？')) return
  await fetch(`/api/admin/reports/${id}/review?action=${action}&note=`, { method: 'POST', headers: store.authHeaders() })
  await load()
}

function fmtDate(s) {
  if (!s) return ''
  return new Date(s).toLocaleString('zh-CN')
}

onMounted(load)
</script>

<style scoped>
.page h2{font-size:20px;margin-bottom:16px}
.tabs{display:flex;gap:4px;margin-bottom:16px}
.tabs button{padding:6px 16px;border:1px solid var(--border);border-radius:var(--radius-sm);font-size:13px;background:var(--bg-card);color:var(--text-secondary);cursor:pointer}
.tabs button.active{background:var(--primary);color:#fff;border-color:var(--primary)}
.table{width:100%;border-collapse:collapse;background:var(--bg-card);border-radius:var(--radius);overflow:hidden;border:1px solid var(--border)}
.table th,.table td{padding:10px 14px;text-align:left;font-size:13px;border-bottom:1px solid var(--border)}
.table th{background:var(--primary-light);color:var(--primary);font-weight:600}
.reason-tag{padding:2px 8px;border-radius:8px;font-size:12px;font-weight:600;background:#fed7d7;color:#9b2c2c}
.detail{max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.badge{padding:2px 10px;border-radius:10px;font-size:12px;font-weight:600}
.badge.ok{background:#c6f6d5;color:#22543d}
.badge.dim{background:var(--primary-light);color:var(--text-secondary)}
.actions{display:flex;gap:6px}
.btn-sm{padding:4px 12px;border-radius:var(--radius-sm);font-size:12px;border:none;cursor:pointer;background:var(--primary-light);color:var(--primary)}
.btn-sm.danger{background:#fed7d7;color:#9b2c2c}
.empty{color:var(--text-secondary);font-size:14px}
</style>
