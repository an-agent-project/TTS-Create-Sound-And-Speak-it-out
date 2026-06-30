<template>
  <div class="profile-page">
    <div class="page-header">
      <h1 class="page-title"><User :size="28" class="title-icon" /> 个人中心</h1>
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
              <Camera :size="28" />
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
          <div v-if="avatarError" class="avatar-error">{{ avatarError }}</div>
        </div>
        <div class="account-info">
          <h2 class="account-name">{{ store.user.username || '用户' }}</h2>
          <div class="account-meta">
            <!-- Email — inline editable -->
            <div class="meta-item editable" @click="startEdit('email')">
              <Mail :size="18" class="meta-icon" />
              <template v-if="editingField === 'email'">
                <input
                  ref="editInput"
                  v-model="editValue"
                  type="email"
                  class="inline-input"
                  placeholder="请输入邮箱"
                  @keydown.enter="saveEdit"
                  @keydown.escape="cancelEdit"
                  @click.stop
                />
                <button class="icon-btn save" @click.stop="saveEdit" title="保存"><Check :size="16" /></button>
                <button class="icon-btn cancel" @click.stop="cancelEdit" title="取消"><X :size="16" /></button>
              </template>
              <span v-else class="meta-value">{{ store.user.email || '未设置邮箱' }} <Pencil :size="12" class="edit-hint" /></span>
            </div>
            <!-- Phone — inline editable -->
            <div class="meta-item editable" @click="startEdit('phone')">
              <Smartphone :size="18" class="meta-icon" />
              <template v-if="editingField === 'phone'">
                <input
                  ref="editInput"
                  v-model="editValue"
                  type="tel"
                  class="inline-input"
                  placeholder="请输入手机号"
                  maxlength="11"
                  @keydown.enter="saveEdit"
                  @keydown.escape="cancelEdit"
                  @click.stop
                />
                <button class="icon-btn save" @click.stop="saveEdit" title="保存"><Check :size="16" /></button>
                <button class="icon-btn cancel" @click.stop="cancelEdit" title="取消"><X :size="16" /></button>
              </template>
              <span v-else class="meta-value">{{ store.user.phone || '未设置手机号' }} <Pencil :size="12" class="edit-hint" /></span>
            </div>
            <div class="meta-item">
              <Calendar :size="18" class="meta-icon" />
              <span>注册时间：{{ formattedDate }}</span>
            </div>
            <div class="meta-item">
              <Layers :size="18" class="meta-icon" />
              <span>作品数量：{{ store.works.length }}</span>
            </div>
          </div>
          <div class="account-actions">
            <button class="btn btn-secondary btn-sm" @click="openPasswordModal">
              <Lock :size="14" /> 修改密码
            </button>
            <button class="btn btn-danger btn-sm" @click="handleLogout">
              退出登录
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- My Works Section -->
    <div class="section works-section">
      <div class="section-title">
        <BarChart3 :size="22" class="section-icon" /> 我的作品
        <span class="work-count-badge">{{ store.works.length }}</span>
      </div>

      <div v-if="store.works.length === 0" class="empty-state">
        <FolderOpen :size="56" class="empty-icon" />
        <h3>还没有作品</h3>
        <p>前往创作工作台开始你的第一个配音吧</p>
        <router-link to="/workspace" class="btn btn-primary btn-lg" style="margin-top: 16px;">
          <Rocket :size="18" /> 开始创作
        </router-link>
      </div>

      <div v-else class="works-list">
        <div
          v-for="work in store.works"
          :key="work.id"
          class="work-row"
          @click="previewWork = work"
        >
          <div class="work-row-icon"><Music :size="28" /></div>
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
            <button class="btn btn-secondary btn-sm" @click="previewWork = work"><Play :size="14" /> 播放</button>
            <button class="btn btn-primary btn-sm" @click="editWork(work)">编辑</button>
            <button class="btn btn-danger btn-sm" @click="confirmDelete(work)"><Trash2 :size="14" /></button>
          </div>
        </div>
      </div>
    </div>

    <!-- Preview Modal -->
    <div v-if="previewWork" class="confirm-overlay" @click.self="previewWork = null">
      <div class="preview-modal">
        <div class="modal-header">
          <h3><PlayCircle :size="22" class="section-icon" /> 试听作品</h3>
          <button class="close-btn" @click="previewWork = null"><X :size="18" /></button>
        </div>
        <div class="modal-body">
          <div class="preview-info">
            <strong>{{ previewWork.title }}</strong>
            <p style="font-size:13px;color:var(--text-secondary);margin-top:4px;">
              {{ previewWork.sceneName }} · {{ previewWork.voiceName }} · 时长约{{ previewWork.duration }} 秒
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

    <!-- Delete Confirm Modal -->
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

    <!-- Change Password Modal -->
    <div v-if="showPasswordModal" class="confirm-overlay" @click.self="showPasswordModal = false">
      <div class="confirm-modal">
        <h3>修改密码</h3>
        <div class="form-group">
          <label class="form-label">当前密码</label>
          <div class="pwd-wrap">
            <input
              :type="showPwdInModal ? 'text' : 'password'"
              v-model="passwordForm.oldPassword"
              class="form-input"
              placeholder="请输入当前密码"
            />
            <span class="toggle-pwd" @click="showPwdInModal = !showPwdInModal">
              <EyeOff v-if="showPwdInModal" :size="18" />
              <Eye v-else :size="18" />
            </span>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">新密码</label>
          <div class="pwd-wrap">
            <input
              :type="showPwdInModal ? 'text' : 'password'"
              v-model="passwordForm.newPassword"
              class="form-input"
              placeholder="请设置新密码（至少4位）"
            />
            <span class="toggle-pwd" @click="showPwdInModal = !showPwdInModal">
              <EyeOff v-if="showPwdInModal" :size="18" />
              <Eye v-else :size="18" />
            </span>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">确认新密码</label>
          <div class="pwd-wrap">
            <input
              :type="showPwdInModal ? 'text' : 'password'"
              v-model="passwordForm.confirmPassword"
              class="form-input"
              placeholder="请再次输入新密码"
            />
            <span class="toggle-pwd" @click="showPwdInModal = !showPwdInModal">
              <EyeOff v-if="showPwdInModal" :size="18" />
              <Eye v-else :size="18" />
            </span>
          </div>
        </div>
        <div v-if="passwordError" class="err-msg">{{ passwordError }}</div>
        <div v-if="passwordSuccess" class="success-msg">{{ passwordSuccess }}</div>
        <div class="confirm-actions">
          <button class="btn btn-secondary" @click="showPasswordModal = false">取消</button>
          <button class="btn btn-primary" @click="handleChangePassword" :disabled="passwordLoading">
            {{ passwordLoading ? '修改中...' : '确认修改' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, reactive } from "vue";
import { useRouter } from "vue-router";
import { useAppStore } from "../stores/app.js";
import AudioPlayer from "../components/AudioPlayer.vue";
import {
  User, Camera, Mail, Calendar, Layers, BarChart3, FolderOpen,
  Rocket, Music, Play, PlayCircle, Trash2, X, Pencil, Check, Smartphone, Lock, Eye, EyeOff
} from 'lucide-vue-next'

const router = useRouter();
const store = useAppStore();

const fileInput = ref(null);
const editInput = ref(null);
const deleteTarget = ref(null);
const previewWork = ref(null);
const isPlaying = ref(false);
const avatarError = ref("");

const editingField = ref(null);   // null | 'email' | 'phone'
const editValue = ref("");

const showPasswordModal = ref(false);
const showPwdInModal = ref(false);
const passwordLoading = ref(false);
const passwordError = ref("");
const passwordSuccess = ref("");
const passwordForm = reactive({
  oldPassword: "",
  newPassword: "",
  confirmPassword: "",
});

const formattedDate = computed(() => {
  const d = store.user.created_at;
  if (!d) return "";
  const date = new Date(d);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
});

function triggerFileInput() {
  fileInput.value?.click();
}

function compressAvatarFile(file) {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => {
      const maxSize = 256;
      const scale = Math.min(1, maxSize / Math.max(image.width, image.height));
      const canvas = document.createElement("canvas");
      canvas.width = Math.max(1, Math.round(image.width * scale));
      canvas.height = Math.max(1, Math.round(image.height * scale));
      const ctx = canvas.getContext("2d");
      if (!ctx) {
        URL.revokeObjectURL(image.src);
        reject(new Error("头像处理失败"));
        return;
      }
      ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
      const avatar = canvas.toDataURL("image/jpeg", 0.82);
      URL.revokeObjectURL(image.src);
      resolve(avatar);
    };
    image.onerror = () => {
      URL.revokeObjectURL(image.src);
      reject(new Error("头像文件读取失败"));
    };
    image.src = URL.createObjectURL(file);
  });
}

async function handleFileChange(e) {
  const file = e.target.files?.[0];
  if (!file) return;
  avatarError.value = "";
  try {
    const avatar = await compressAvatarFile(file);
    await store.updateMe({ avatar });
  } catch (error) {
    avatarError.value = error.message || "头像保存失败";
  } finally {
    e.target.value = "";
  }
}
async function startEdit(field) {
  editingField.value = field;
  editValue.value = store.user[field] || "";
  await nextTick();
  editInput.value?.focus();
}

function cancelEdit() {
  editingField.value = null;
  editValue.value = "";
}

async function saveEdit() {
  const field = editingField.value;
  if (!field) return;
  const value = editValue.value.trim();
  await store.updateMe({ [field]: value || null });
  editingField.value = null;
  editValue.value = "";
}

function openPasswordModal() {
  passwordForm.oldPassword = "";
  passwordForm.newPassword = "";
  passwordForm.confirmPassword = "";
  passwordError.value = "";
  passwordSuccess.value = "";
  passwordLoading.value = false;
  showPwdInModal.value = false;
  showPasswordModal.value = true;
}

async function handleChangePassword() {
  passwordError.value = "";
  passwordSuccess.value = "";
  if (!passwordForm.oldPassword) {
    passwordError.value = "请输入当前密码";
    return;
  }
  if (passwordForm.newPassword.length < 4) {
    passwordError.value = "新密码长度不能少于4位";
    return;
  }
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    passwordError.value = "两次新密码输入不一致";
    return;
  }
  passwordLoading.value = true;
  const result = await store.changePassword(passwordForm.oldPassword, passwordForm.newPassword);
  passwordLoading.value = false;
  if (!result.success) {
    passwordError.value = result.message;
    return;
  }
  passwordSuccess.value = "密码修改成功！";
  setTimeout(() => { showPasswordModal.value = false; }, 1500);
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

.title-icon {
  color: var(--primary);
  flex-shrink: 0;
}

.section-icon {
  color: var(--primary);
  flex-shrink: 0;
}

.empty-icon {
  color: var(--text-muted);
  opacity: 0.4;
  margin-bottom: 16px;
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
  color: #fff;
}

.avatar-wrapper:hover .avatar-overlay {
  opacity: 1;
}

.avatar-label {
  font-size: 12px;
  color: var(--text-muted);
}

.avatar-error {
  margin-top: 6px;
  color: #c53030;
  font-size: 12px;
  max-width: 140px;
  text-align: center;
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

.meta-item.editable {
  cursor: pointer;
  border-radius: var(--radius-xs);
  padding: 4px 6px;
  margin: -4px -6px;
  transition: background 0.15s;
}

.meta-item.editable:hover {
  background: var(--primary-light);
}

.meta-value {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.edit-hint {
  opacity: 0;
  color: var(--text-muted);
  transition: opacity 0.15s;
}

.meta-item.editable:hover .edit-hint {
  opacity: 1;
}

.inline-input {
  padding: 4px 8px;
  border: 1px solid var(--primary);
  border-radius: var(--radius-xs);
  font-size: 14px;
  outline: none;
  width: 180px;
}

.icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  flex-shrink: 0;
}

.icon-btn.save {
  background: var(--success);
  color: #fff;
}

.icon-btn.cancel {
  background: var(--border);
  color: var(--text-secondary);
}

.meta-icon {
  width: 28px;
  text-align: center;
  color: var(--text-muted);
  flex-shrink: 0;
}

.account-actions {
  display: flex;
  gap: 8px;
  margin-top: 16px;
  flex-wrap: wrap;
}

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
  flex-shrink: 0;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg);
  border-radius: 10px;
  color: var(--primary);
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
  display: flex;
  align-items: center;
  gap: 8px;
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
  color: var(--text-muted);
  padding: 4px 8px;
  border-radius: var(--radius-xs);
  cursor: pointer;
  display: flex;
}

.close-btn:hover {
  background: var(--bg);
  color: var(--text);
}

.preview-info {
  margin-bottom: 20px;
}

.err-msg {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 13px;
  margin-bottom: 16px;
}

.success-msg {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #16a34a;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 13px;
  margin-bottom: 16px;
}

/* Password visibility toggle inside modal */
.pwd-wrap {
  position: relative;
}

.pwd-wrap .form-input {
  padding-right: 40px;
}

.pwd-wrap .toggle-pwd {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  color: #9ca3af;
  display: flex;
  align-items: center;
  user-select: none;
}

.pwd-wrap .toggle-pwd:hover {
  color: var(--primary);
}

@media (max-width: 640px) {
  .account-top {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  .account-actions {
    justify-content: center;
  }
  .work-row-actions {
    flex-direction: column;
  }
  .inline-input {
    width: 130px;
  }
}
</style>
