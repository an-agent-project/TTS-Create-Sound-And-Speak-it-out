<template>
  <div class="page admin-voices-page">
    <section class="review-panel">
      <div class="section-head">
        <div>
          <h2>公共音色审核</h2>
          <p>用户从个人音色库提交后，会先进入这里，由管理员决定是否展示到公共音色库。</p>
        </div>
        <button class="btn-sm" @click="loadPublishRequests">刷新</button>
      </div>

      <div v-if="publishError" class="notice danger">{{ publishError }}</div>
      <table v-if="publishRequests.length" class="table review-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>音色</th>
            <th>提交用户</th>
            <th>分类</th>
            <th>Provider</th>
            <th>提交时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in publishRequests" :key="item.id">
            <td>{{ item.id }}</td>
            <td>
              <strong>{{ item.voiceName }}</strong>
              <span class="muted">#{{ item.sourceVoiceId }}</span>
            </td>
            <td>{{ item.requesterName }}</td>
            <td>{{ item.category || "-" }}</td>
            <td>{{ (item.providers || []).map((p) => p.provider).join(", ") || "-" }}</td>
            <td>{{ formatTime(item.createdAt) }}</td>
            <td class="actions">
              <button class="btn-sm ok" :disabled="reviewingId === item.id" @click="reviewRequest(item, 'approve')">通过</button>
              <button class="btn-sm danger" :disabled="reviewingId === item.id" @click="reviewRequest(item, 'reject')">拒绝</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else class="empty">暂无待审核音色</p>
    </section>

    <section class="voice-panel">
      <h2>音色管理</h2>
      <p v-if="loadError" class="notice danger">{{ loadError }}</p>
      <table v-else-if="voices.length" class="table">
        <thead>
          <tr><th>ID</th><th>音色名</th><th>性别</th><th>分类</th><th>供应商</th><th>归属</th><th>状态</th><th>操作</th></tr>
        </thead>
        <tbody>
          <tr v-for="v in voices" :key="v.id" :class="{ inactive: !v.isActive }">
            <td>{{ v.id }}</td>
            <td>
              <input v-if="editingId === v.id" v-model="editName" class="inline-input" @keyup.enter="saveEdit(v.id)" />
              <span v-else>{{ v.displayName }}</span>
            </td>
            <td>{{ v.gender === "female" ? "女声" : v.gender === "male" ? "男声" : v.gender }}</td>
            <td>
              <input v-if="editingId === v.id" v-model="editCat" class="inline-input" @keyup.enter="saveEdit(v.id)" />
              <span v-else>{{ v.category }}</span>
            </td>
            <td>{{ v.providers.map((p) => p.provider).join(", ") }}</td>
            <td>{{ v.ownerId ? "用户#" + v.ownerId : "公共" }}</td>
            <td>
              <span :class="v.isActive ? 'badge ok' : 'badge del'">{{ v.isActive ? "启用" : "禁用" }}</span>
            </td>
            <td class="actions">
              <template v-if="editingId === v.id">
                <button class="btn-sm ok" @click="saveEdit(v.id)">保存</button>
                <button class="btn-sm" @click="editingId = null">取消</button>
              </template>
              <template v-else>
                <button class="btn-sm" @click="startEdit(v)">编辑</button>
                <button class="btn-sm warn" @click="toggleVoice(v)">{{ v.isActive ? "禁用" : "启用" }}</button>
                <button class="btn-sm danger" @click="removeVoice(v)">删除</button>
              </template>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else class="empty">暂无音色</p>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { fetchVoicePublishRequests, reviewVoicePublishRequest } from "../../services/api.js";
import { useAppStore } from "../../stores/app.js";

const store = useAppStore();
const voices = ref([]);
const publishRequests = ref([]);
const publishError = ref("");
const reviewingId = ref(null);
const editingId = ref(null);
const editName = ref("");
const editCat = ref("");
const loadError = ref("");

async function load() {
  loadError.value = "";
  const resp = await fetch("/api/admin/voices?pageSize=100", { headers: store.authHeaders() });
  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    voices.value = [];
    loadError.value = data.detail || data.message || `加载失败：${resp.status}`;
    return;
  }
  voices.value = data.items || [];
}

async function loadPublishRequests() {
  try {
    publishError.value = "";
    const data = await fetchVoicePublishRequests("pending");
    publishRequests.value = data.items || [];
  } catch (error) {
    publishError.value = error.message || "加载审核列表失败";
  }
}

function startEdit(v) {
  editingId.value = v.id;
  editName.value = v.displayName;
  editCat.value = v.category || "";
}

async function saveEdit(id) {
  const p = new URLSearchParams();
  if (editName.value) p.set('displayName', editName.value);
  if (editCat.value) p.set('category', editCat.value);
  await fetch(`/api/admin/voices/${id}?${p}`, { method: "PUT", headers: store.authHeaders() });
  editingId.value = null;
  await load();
}

async function toggleVoice(v) {
  const p = new URLSearchParams();
  p.set('isActive', String(!v.isActive));
  await fetch(`/api/admin/voices/${v.id}?${p}`, { method: "PUT", headers: store.authHeaders() });
  await load();
}

async function removeVoice(v) {
  const url = `/api/admin/voices/${v.id}${v.ownerId ? "" : "?permanent=true"}`;
  await fetch(url, { method: "DELETE", headers: store.authHeaders() });
  await load();
}

async function reviewRequest(item, action) {
  reviewingId.value = item.id;
  try {
    await reviewVoicePublishRequest(item.id, action);
    publishRequests.value = publishRequests.value.filter((entry) => entry.id !== item.id);
    if (action === "approve") await load();
  } catch (error) {
    publishError.value = error.message || "审核操作失败";
  } finally {
    reviewingId.value = null;
  }
}

function formatTime(value) {
  if (!value) return "-";
  return new Date(value).toLocaleString();
}

onMounted(async () => {
  await Promise.all([load(), loadPublishRequests()]);
});
</script>

<style scoped>
.page h2{font-size:20px;margin-bottom:8px}
.admin-voices-page{display:flex;flex-direction:column;gap:24px}
.review-panel,.voice-panel{display:flex;flex-direction:column;gap:12px}
.section-head{display:flex;justify-content:space-between;gap:16px;align-items:flex-start}
.section-head p{margin:0;color:var(--text-secondary);font-size:13px;line-height:1.6}
.table{width:100%;border-collapse:collapse;background:var(--bg-card);border-radius:var(--radius);overflow:hidden;border:1px solid var(--border)}
.table th,.table td{padding:10px 14px;text-align:left;font-size:13px;border-bottom:1px solid var(--border);vertical-align:middle}
.table th{background:var(--primary-light);color:var(--primary);font-weight:600}
.review-table strong{display:block;margin-bottom:2px}
.muted{color:var(--text-muted);font-size:12px}
tr.inactive{opacity:.45}
.inline-input{padding:4px 8px;border:1px solid var(--primary);border-radius:4px;font-size:13px;width:120px;background:var(--bg-card);color:var(--text)}
.badge{padding:2px 10px;border-radius:10px;font-size:12px;font-weight:600}
.badge.ok{background:#c6f6d5;color:#22543d}
.badge.del{background:#fed7d7;color:#9b2c2c}
.actions{display:flex;gap:6px;flex-wrap:wrap}
.btn-sm{padding:4px 12px;border-radius:var(--radius-sm);font-size:12px;border:none;cursor:pointer;background:var(--primary-light);color:var(--primary)}
.btn-sm:disabled{opacity:.55;cursor:not-allowed}
.btn-sm.warn{background:#fefcbf;color:#975a16}
.btn-sm.ok{background:#c6f6d5;color:#22543d}
.btn-sm.danger{background:#fed7d7;color:#9b2c2c}
.empty{color:var(--text-secondary);font-size:14px}
.notice{padding:10px 12px;border-radius:6px;font-size:13px}
.notice.danger{background:#fee2e2;color:#991b1b}
</style>
