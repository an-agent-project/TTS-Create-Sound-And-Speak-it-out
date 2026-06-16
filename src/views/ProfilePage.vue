<template>
  <div class="profile-page">
    <!-- Account Info Card -->
    <div class="page-header">
      <h1 class="page-title">👤 个人中心</h1>
    </div>

    <div class="card account-card">
      <div class="account-top">
        <div class="avatar-section">
          <div class="avatar-wrapper" @click="triggerFileInput" title="点击更换头像">
            <img v-if="store.user.avatar" :src="store.user.avatar" class="avatar-img" />
            <span v-else class="avatar-placeholder">
              {{ store.user.username ? store.user.username[0] : '?' }}
            </span>
            <div class="avatar-overlay">
              <span>📷</span>
            </div>
          </div>
          <input
            ref="fileInput"
            type="file"
            accept="image/*"
            style="display:none"
            @change="handleFileChange"
          />
          <div class="avatar-label">点击更换头像</div>
        </div>
        <div class="account-info">
          <h2 class="account-name">{{ store.user.username || '用户' }}</h2>
          <div class="account-meta">
            <div class="meta-item">
              <span class="meta-icon">📧</span>
              <span>{{ store.user.email || '未设置邮箱' }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-icon">📅</span>
              <span>注册时间：{{ formattedDate }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-icon">🎧</span>
              <span>作品数量：{{ store.works.length }}</span>
            </div>
          </div>
          <button class="btn btn-danger btn-sm" @click="handleLogout" style="margin-top:12px;">
            退出登录
          </button>
        </div>
      </div>
    </div>

    <!-- My Works Section -->
    <div class="section works-section">
      <div class="section-title">
        <span class="icon">📂</span> 我的作品
        <span class="work-count-badge">{{ store.works.length }}</span>
      </div>

      <div v-if="store.works.length === 0" class="empty-state">
        <div class="icon">📭</div>
        <h3>还没有作品</h3>
        <p>前往创作工作台开始你的第一个配音吧</p>
        <router-link to="/workspace" class="btn btn-primary btn-lg" style="margin-top: 16px;">
          🚀 开始创作
        </router-link>
      </div>

      <div v-else class="works-list">
        <div
          v-for="work in store.works"
          :key="work.id"
          class="work-row"
          @click="previewWork = work"
        >
          <div class="work-row-icon">📄</div>
          <div class="work-row-info">
            <div class="work-row-title">{{ work.title }}</div>
            <div class="work-row-meta">
              <span>{{ formatDate(work.createdAt) }}</span>
              <span class="tag tag-primary">{{ work.sceneName || '通用' }}</span>
              <span class="tag tag-success">{{ work.voiceName || '默认' }}</span>
              <span>⏱ {{ work.duration || 0 }}秒</span>
            </div>
          </div>
          <div class="work-row-actions" @click.stop>
            <button class="btn btn-secondary btn-sm" @click="previewWork = work">▶ 播放</button>
            <button class="btn btn-primary btn-sm" @click="editWork(work)">编辑</button>
            <button class="btn btn-danger btn-sm" @click="confirmDelete(work)">🗑</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Preview Modal -->
    <div v-if="previewWork" class="confirm-overlay" @click.self="previewWork = null">
      <div class="preview-modal">
        <div class="modal-header">
          <h3>🎧 试听作品</h3>
          <button class="close-btn" @click="previewWork = null">✕</button>
        </div>
        <div class="modal-body">
          <div class="preview-info">
            <strong>{{ previewWork.title }}</strong>
            <p style="font-size:13px;color:var(--text-secondary);margin-top:4px;">
              {{ previewWork.sceneName }} · {{ previewWork.voiceName }} · 时长约 {{ previewWork.duration }} 秒
            </p>
          </div>
          <AudioPlayer
            :is-playing="isPlaying"
            :current-time="0"
            :duration="previewWork.duration || 0"
            :volume="80"
            audio-url="#"
            @toggle-play="isPlaying = !isPlaying"
          />
          <div class="modal-actions">
            <button class="btn btn-secondary" @click="previewWork = null">关闭</button>
            <button class="btn btn-primary" @click="editWork(previewWork); previewWork = null">编辑</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirm -->
    <div v-if="deleteTarget" class="confirm-overlay" @click.self="deleteTarget = null">
      <div class="confirm-modal">
        <h3>确认删除</h3>
        <p>确定要删除作品「{{ deleteTarget.title }}」吗？此操作不可撤销。</p>
        <div class="confirm-actions">
          <button class="btn btn-secondary" @click="deleteTarget = null">取消</button>
          <button class="btn btn-danger" @click="doDelete">确认删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { useAppStore } from "../stores/app.js";
import AudioPlayer from "../components/AudioPlayer.vue";

const router = useRouter();
const store = useAppStore();

const fileInput = ref(null);
const isPlaying = ref(false);
const previewWork = ref(null);
const deleteTarget = ref(null);

const formattedDate = computed(() => {
  const d = store.user.registeredAt;
  if (!d) return "未知";
  return new Date(d).toLocaleDateString("zh-CN", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
});

function triggerFileInput() {
  fileInput.value?.click();
}

function handleFileChange(e) {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (ev) => {
    store.updateAvatar(ev.target.result);
  };
  reader.readAsDataURL(file);
}

function handleLogout() {
  store.logout();
  router.push("/");
}

function formatDate(dateStr) {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function editWork(work) {
  store.textContent = work.content;
  store.currentWork = work;
  router.push("/workspace");
}

function confirmDelete(work) {
  deleteTarget.value = work;
}

function doDelete() {
  if (deleteTarget.value) {
    store.deleteWork(deleteTarget.value.id);
    deleteTarget.value = null;
  }
}
</script>

<style scoped>
.profile-page {
  padding-bottom: 40px;
}

.account-card {
  padding: 32px;
  margin-bottom: 32px;
}

.account-top {
  display: flex;
  gap: 32px;
  align-items: flex-start;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.avatar-wrapper {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  overflow: hidden;
  cursor: pointer;
  position: relative;
  background: var(--primary-light);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  font-size: 40px;
  font-weight: 700;
  color: var(--primary);
}

.avatar-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.avatar-wrapper:hover .avatar-overlay {
  opacity: 1;
}

.avatar-overlay span {
  font-size: 28px;
}

.avatar-label {
  font-size: 12px;
  color: var(--text-muted);
}

.account-info {
  flex: 1;
}

.account-name {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 16px;
}

.account-meta {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--text-secondary);
}

.meta-icon {
  font-size: 18px;
  width: 28px;
  text-align: center;
}

/* Works */
.works-section {
  margin-top: 0;
}

.work-count-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: var(--primary);
  color: #fff;
  font-size: 12px;
  font-weight: 700;
}

.works-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.work-row {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  background: var(--bg-card);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  cursor: pointer;
  transition: all var(--transition);
}

.work-row:hover {
  border-color: var(--primary);
  box-shadow: var(--shadow-md);
}

.work-row-icon {
  font-size: 28px;
  flex-shrink: 0;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg);
  border-radius: 10px;
}

.work-row-info {
  flex: 1;
  min-width: 0;
}

.work-row-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.work-row-meta {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
  font-size: 12px;
  color: var(--text-muted);
}

.work-row-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

/* Modal styles */
.confirm-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.confirm-modal,
.preview-modal {
  background: var(--bg-card);
  border-radius: var(--radius);
  width: 90%;
  max-width: 440px;
  box-shadow: var(--shadow-lg);
  padding: 28px;
}

.preview-modal {
  max-width: 560px;
}

.confirm-modal h3,
.preview-modal h3 {
  font-size: 18px;
  margin-bottom: 12px;
}

.confirm-modal p {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 20px;
}

.confirm-actions,
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.modal-actions {
  margin-top: 20px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.close-btn {
  background: none;
  font-size: 18px;
  color: var(--text-muted);
  padding: 4px 8px;
  border-radius: var(--radius-xs);
  cursor: pointer;
}

.close-btn:hover {
  background: var(--bg);
  color: var(--text);
}

.preview-info {
  margin-bottom: 20px;
}

@media (max-width: 640px) {
  .account-top {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  .work-row-actions {
    flex-direction: column;
  }
}
</style>