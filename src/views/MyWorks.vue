<template>
  <div class="my-works-page">
    <div class="page-header">
      <h1 class="page-title">📂 我的作品</h1>
      <p class="page-subtitle">
        已保存 {{ store.works.length }} 个配音作品
      </p>
      <p v-if="loadError" class="load-error">{{ loadError }}</p>
    </div>

    <!-- Works List -->
    <div v-if="store.works.length > 0">
      <div class="grid grid-2">
        <WorkCard
          v-for="work in store.works"
          :key="work.id"
          :work="work"
          @edit="editWork(work)"
          @delete="confirmDelete(work)"
          @preview="previewWork = work"
        />
      </div>
    </div>

    <!-- Empty -->
    <div v-else class="empty-state">
      <div class="icon">📭</div>
      <h3>还没有作品</h3>
      <p>前往创作工作台开始你的第一个配音吧</p>
      <router-link to="/workspace" class="btn btn-primary btn-lg" style="margin-top: 16px;">
        🚀 开始创作
      </router-link>
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
            :audio-url="previewWork.audioUrl"
            @toggle-play="isPlaying = !isPlaying"
          />
          <div class="modal-actions">
            <button class="btn btn-secondary" @click="previewWork = null">关闭</button>
            <button class="btn btn-primary" @click="editWork(previewWork); previewWork = null">编辑</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { useAppStore } from "../stores/app.js";
import WorkCard from "../components/WorkCard.vue";
import AudioPlayer from "../components/AudioPlayer.vue";

const router = useRouter();
const store = useAppStore();

const deleteTarget = ref(null);
const previewWork = ref(null);
const isPlaying = ref(false);
const loadError = ref("");

onMounted(async () => {
  try {
    await store.fetchWorks();
  } catch (error) {
    loadError.value = `后端暂时不可用：${error.message}`;
  }
});

function confirmDelete(work) {
  deleteTarget.value = work;
}

async function doDelete() {
  if (deleteTarget.value) {
    try {
      await store.deleteWork(deleteTarget.value.id);
      deleteTarget.value = null;
    } catch (error) {
      loadError.value = `删除失败：${error.message}`;
    }
  }
}

function editWork(work) {
  store.textContent = work.content;
  store.currentWork = work;
  router.push("/workspace");
}
</script>

<style scoped>
.confirm-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.2s ease;
}

.load-error {
  margin-top: 8px;
  color: #b91c1c;
  font-size: 14px;
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

.confirm-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
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
}

.close-btn:hover {
  background: var(--bg);
  color: var(--text);
}

.modal-body {
  /*  */
}

.preview-info {
  margin-bottom: 20px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>
