<template>
  <div class="page">
    <h2>音色管理</h2>
    <table v-if="voices.length" class="table">
      <thead><tr><th>ID</th><th>音色名</th><th>性别</th><th>分类</th><th>供应商</th><th>归属</th><th>状态</th><th>操作</th></tr></thead>
      <tbody>
        <tr v-for="v in voices" :key="v.id" :class="{ inactive: !v.isActive }">
          <td>{{ v.id }}</td>
          <td>
            <input v-if="editingId === v.id" v-model="editName" class="inline-input" @keyup.enter="saveEdit(v.id)" />
            <span v-else>{{ v.displayName }}</span>
          </td>
          <td>{{ v.gender === 'female' ? '女' : '男' }}</td>
          <td>
            <input v-if="editingId === v.id" v-model="editCat" class="inline-input" @keyup.enter="saveEdit(v.id)" />
            <span v-else>{{ v.category }}</span>
          </td>
          <td>{{ v.providers.map(p => p.provider).join(', ') }}</td>
          <td>{{ v.ownerId ? '用户#' + v.ownerId : '公共' }}</td>
          <td>
            <span :class="v.isActive ? 'badge ok' : 'badge del'">{{ v.isActive ? '启用' : '禁用' }}</span>
          </td>
          <td class="actions">
            <template v-if="editingId === v.id">
              <button @click="saveEdit(v.id)" class="btn-sm ok">保存</button>
              <button @click="editingId = null" class="btn-sm">取消</button>
            </template>
            <template v-else>
              <button @click="startEdit(v)" class="btn-sm">编辑</button>
              <button @click="toggleVoice(v)" class="btn-sm warn">{{ v.isActive ? '禁用' : '启用' }}</button>
              <button @click="removeVoice(v)" class="btn-sm danger">删除</button>
            </template>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else class="empty">暂无音色</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAppStore } from '../../stores/app.js'
const store = useAppStore()
const voices = ref([])
const editingId = ref(null)
const editName = ref('')
const editCat = ref('')

async function load() {
  const resp = await fetch('/api/admin/voices?pageSize=100', { headers: store.authHeaders() })
  const data = await resp.json(); voices.value = data.items || []
}

function startEdit(v) {
  editingId.value = v.id
  editName.value = v.displayName
  editCat.value = v.category || ''
}

async function saveEdit(id) {
  const p = new URLSearchParams()
  if (editName.value) p.set('displayName', editName.value)
  if (editCat.value) p.set('category', editCat.value)
  await fetch('/api/admin/voices/' + id + '?' + p, { method: 'PUT', headers: store.authHeaders() })
  editingId.value = null
  await load()
}

async function toggleVoice(v) {
  const p = new URLSearchParams()
  p.set('isActive', String(!v.isActive))
  await fetch('/api/admin/voices/' + v.id + '?' + p, { method: 'PUT', headers: store.authHeaders() })
  await load()
}

async function removeVoice(v) {
  if (v.ownerId) {
    if (!confirm('确定删除该音色？')) return
  } else {
    if (!confirm('该音色为公共音色，删除后将同时删除所有用户的个人副本。\n\n确定删除？')) return
  }
  const url = '/api/admin/voices/' + v.id + (v.ownerId ? '' : '?permanent=true')
  await fetch(url, { method: 'DELETE', headers: store.authHeaders() })
  await load()
}

onMounted(load)
</script>

<style scoped>
.page h2{font-size:20px;margin-bottom:16px}
.table{width:100%;border-collapse:collapse;background:var(--bg-card);border-radius:var(--radius);overflow:hidden;border:1px solid var(--border)}
.table th,.table td{padding:10px 14px;text-align:left;font-size:13px;border-bottom:1px solid var(--border)}
.table th{background:var(--primary-light);color:var(--primary);font-weight:600}
tr.inactive{opacity:.45}
.inline-input{padding:4px 8px;border:1px solid var(--primary);border-radius:4px;font-size:13px;width:100px;background:var(--bg-card);color:var(--text)}
.badge{padding:2px 10px;border-radius:10px;font-size:12px;font-weight:600}
.badge.ok{background:#c6f6d5;color:#22543d}
.badge.del{background:#fed7d7;color:#9b2c2c}
.actions{display:flex;gap:6px}
.btn-sm{padding:4px 12px;border-radius:var(--radius-sm);font-size:12px;border:none;cursor:pointer;background:var(--primary-light);color:var(--primary)}
.btn-sm.warn{background:#fefcbf;color:#975a16}
.btn-sm.ok{background:#c6f6d5;color:#22543d}
.btn-sm.danger{background:#fed7d7;color:#9b2c2c}
.empty{color:var(--text-secondary);font-size:14px}
</style>
