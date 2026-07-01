<template>
  <div class="voice-library-page">
    <div class="page-header">
      <div>
        <h1 class="page-title"><Drama :size="28" class="title-icon" /> 个人音色库</h1>
        <p class="page-subtitle">管理你的个人音色，从公共音色库存入的音色会标注来源</p>
      </div>
      <button class="btn btn-outline manage-toggle" @click="manageMode = !manageMode">
        <Settings2 :size="16" />
        {{ manageMode ? "正常浏览" : "管理模式" }}
      </button>
    </div>

    <div v-if="!manageMode" class="filter-bar card">
      <div class="filter-group">
        <label class="filter-label">性别</label>
        <div class="filter-options">
          <button class="filter-btn" :class="{ active: filterGender === 'all' }" @click="filterGender = 'all'">全部</button>
          <button class="filter-btn" :class="{ active: filterGender === 'female' }" @click="filterGender = 'female'"><User :size="14" /> 女声</button>
          <button class="filter-btn" :class="{ active: filterGender === 'male' }" @click="filterGender = 'male'"><User :size="14" /> 男声</button>
          <button class="filter-btn" :class="{ active: filterGender === 'child' }" @click="filterGender = 'child'"><Baby :size="14" /> 童声</button>
        </div>
      </div>
      <div class="filter-group">
        <label class="filter-label">类别</label>
        <div class="filter-options">
          <button class="filter-btn" :class="{ active: filterCategory === 'all' }" @click="filterCategory = 'all'">全部</button>
          <button
            v-for="cat in categories"
            :key="cat"
            class="filter-btn"
            :class="{ active: filterCategory === cat }"
            @click="filterCategory = cat"
          >
            {{ cat }}
          </button>
        </div>
      </div>
      <div class="filter-group">
        <button class="filter-btn fav-filter" :class="{ active: showFavoritesOnly }" @click="showFavoritesOnly = !showFavoritesOnly">
          <Star
            :size="14"
            :fill="showFavoritesOnly ? 'var(--warning)' : 'none'"
            :color="showFavoritesOnly ? 'var(--warning)' : undefined"
          />
          {{ showFavoritesOnly ? "显示全部" : "仅看收藏" }}
        </button>
      </div>
    </div>


    <div class="section">
      <div class="grid grid-4">
        <VoiceCard
          v-for="voice in filteredVoices"
          :key="voice.id"
          :voice="voice"
          :is-favorite="store.isFavorite(voice.id)"
          :show-preview="true"
          :show-select="!manageMode"
          :manage-mode="manageMode"
          :show-publish="manageMode && !voice.isSystemVoice"
          :publish-disabled="publishingVoiceIds.has(voice.dbId) || ['pending', 'approved'].includes(voice.publishStatus)"
          :publish-label="voice.publishStatus === 'approved' ? '\u5df2\u516c\u5f00' : voice.publishStatus === 'pending' ? '\u5ba1\u6838\u4e2d' : '\u4e0a\u4f20\u516c\u5171\u5e93'"
          @toggle-favorite="store.toggleFavoriteVoice(voice.id)"
          @preview="previewVoice = voice"
          @select="goToWorkspace(voice)"
          @delete-voice="deleteVoice(voice)"
          @update-tags="(tags) => updateVoiceTags(voice.id, tags)"
          @publish-voice="publishVoice(voice)"
        />
      </div>

      <div v-if="loadError" class="load-error">
        {{ loadError }}
      </div>

      <div v-if="filteredVoices.length === 0" class="empty-state">
        <Search :size="56" class="empty-icon" />
        <h3>暂无匹配的音色</h3>
        <p>试试调整筛选条件</p>
      </div>
    </div>

    <div v-if="pendingDeleteVoice" class="delete-confirm-backdrop" @click.self="cancelDeleteVoice">
      <div class="delete-confirm-dialog" role="dialog" aria-modal="true">
        <div class="delete-confirm-icon"><Trash2 :size="22" /></div>
        <div class="delete-confirm-copy">
          <h3>&#x5220;&#x9664;&#x97F3;&#x8272;</h3>
          <p>&#x786E;&#x5B9A;&#x5220;&#x9664;&#x97F3;&#x8272;&#x300C;{{ pendingDeleteVoice.name || pendingDeleteVoice.displayName || pendingDeleteVoice.voiceKey || pendingDeleteVoice.id }}&#x300D;&#x5417;&#xFF1F;&#x5220;&#x9664;&#x540E;&#x4E0D;&#x53EF;&#x6062;&#x590D;&#x3002;</p>
        </div>
        <div class="delete-confirm-actions">
          <button class="btn btn-secondary btn-sm" @click="cancelDeleteVoice">&#x53D6;&#x6D88;</button>
          <button class="btn btn-danger btn-sm" :disabled="deletingVoice" @click="confirmDeleteVoice">
            {{ deletingVoice ? "\u5220\u9664\u4e2d" : "\u786e\u8ba4\u5220\u9664" }}
          </button>
        </div>
      </div>
    </div>

    <VoicePreview
      v-if="previewVoice"
      :voice="previewVoice"
      @close="previewVoice = null"
      @select="goToWorkspace(previewVoice); previewVoice = null"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { Baby, Drama, Search, Settings2, Star, Trash2, User } from "lucide-vue-next";
import VoiceCard from "../components/VoiceCard.vue";
import VoicePreview from "../components/VoicePreview.vue";
import { deleteVoiceById, fetchPersonalVoices, requestVoicePublish } from "../services/api.js";
import { useAppStore } from "../stores/app.js";

const router = useRouter();
const store = useAppStore();

const filterGender = ref("all");
const filterCategory = ref("all");
const showFavoritesOnly = ref(false);
const previewVoice = ref(null);
const pendingDeleteVoice = ref(null);
const deletingVoice = ref(false);
const publishingVoiceIds = ref(new Set());
const manageMode = ref(false);
const loadError = ref("");

const categories = ["知识类", "播客类", "故事类", "情感类", "个人音色"];



const allVoices = ref([]);

async function loadVoices() {
  allVoices.value = (await fetchPersonalVoices()).map((voice) => ({
    ...voice,
    tags: voice.tags || [voice.style, voice.category].filter(Boolean),
    fromPublic: !!voice.sourceVoiceId,
    dbId: voice.id,
    isSystemVoice: voice.ownerId == null,
  }));
}

onMounted(async () => {
  try {
    await loadVoices();
  } catch (error) {
    loadError.value = `后端暂时不可用，当前展示本地示例音色：${error.message}`;
  }
});

const filteredVoices = computed(() => {
  let voices = allVoices.value;
  if (filterGender.value !== "all") {
    voices = voices.filter((v) => v.gender === filterGender.value);
  }
  if (filterCategory.value !== "all") {
    voices = voices.filter((v) => v.category === filterCategory.value);
  }
  if (showFavoritesOnly.value) {
    voices = voices.filter((v) => store.isFavorite(v.id));
  }
  return voices;
});

function deleteVoice(voice) {
  if (voice.isSystemVoice) {
    loadError.value = "\u7cfb\u7edf\u9ed8\u8ba4\u97f3\u8272\u4e0d\u53ef\u5220\u9664";
    return;
  }
  pendingDeleteVoice.value = voice;
}

function cancelDeleteVoice() {
  if (deletingVoice.value) return;
  pendingDeleteVoice.value = null;
}

async function confirmDeleteVoice() {
  const voice = pendingDeleteVoice.value;
  if (!voice || deletingVoice.value) return;
  deletingVoice.value = true;
  try {
    await deleteVoiceById(voice.dbId);
    allVoices.value = allVoices.value.filter((item) => item.dbId !== voice.dbId);
    pendingDeleteVoice.value = null;
    if (store.selectedVoice?.id === voice.id || store.selectedVoice?.dbId === voice.dbId) {
      store.selectedVoice = null;
    }
  } catch (error) {
    loadError.value = error.message || "\u5220\u9664\u97f3\u8272\u5931\u8d25";
  } finally {
    deletingVoice.value = false;
  }
}


async function publishVoice(voice) {
  if (!voice || voice.isSystemVoice || publishingVoiceIds.value.has(voice.dbId)) return;
  publishingVoiceIds.value = new Set([...publishingVoiceIds.value, voice.dbId]);
  try {
    await requestVoicePublish(voice.dbId);
    voice.publishStatus = "pending";
    loadError.value = "\u5df2\u63d0\u4ea4\u516c\u5171\u97f3\u8272\u5e93\u5ba1\u6838";
  } catch (error) {
    const message = error.message || "\u63d0\u4ea4\u5ba1\u6838\u5931\u8d25";
    loadError.value = message.includes("already pending") ? "\u8be5\u97f3\u8272\u5df2\u5728\u5ba1\u6838\u4e2d" : message;
  } finally {
    const next = new Set(publishingVoiceIds.value);
    next.delete(voice.dbId);
    publishingVoiceIds.value = next;
  }
}
function updateVoiceTags(id, tags) {
  const voice = allVoices.value.find((item) => item.id === id);
  if (voice) voice.tags = tags;
}

function goToWorkspace(voice) {
  store.selectedVoice = voice;
  router.push("/workspace");
}
</script>

<style scoped>
.title-icon {
  color: var(--primary);
  flex-shrink: 0;
}

.empty-icon {
  color: var(--text-muted);
  opacity: 0.4;
  margin-bottom: 16px;
}

.filter-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  padding: 16px 20px;
  margin-bottom: 24px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  white-space: nowrap;
}

.filter-options {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.filter-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 14px;
  border-radius: 20px;
  background: var(--bg);
  border: 1px solid var(--border);
  font-size: 13px;
  color: var(--text-secondary);
  transition: all var(--transition);
  white-space: nowrap;
}

.filter-btn:hover {
  border-color: var(--primary);
  color: var(--primary);
}

.filter-btn.active {
  background: var(--primary);
  color: #fff;
  border-color: var(--primary);
}

.fav-filter {
  border-style: dashed;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 24px;
}

.manage-toggle {
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 6px;
}

.load-error {
  margin-top: 16px;
  color: #b91c1c;
  font-size: 14px;
}



.delete-confirm-backdrop {
  position: fixed;
  inset: 0;
  z-index: 60;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: rgba(15, 23, 42, 0.42);
}

.delete-confirm-dialog {
  width: min(420px, 100%);
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 14px;
  padding: 20px;
  border-radius: 8px;
  background: var(--bg-card, #fff);
  border: 1px solid var(--border);
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.22);
}

.delete-confirm-icon {
  width: 42px;
  height: 42px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fee2e2;
  color: #dc2626;
}

.delete-confirm-copy h3 {
  margin: 0 0 8px;
  font-size: 18px;
  color: var(--text-primary);
}

.delete-confirm-copy p {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-secondary);
}

.delete-confirm-actions {
  grid-column: 1 / -1;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 4px;
}

.btn-danger {
  background: #fee2e2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.btn-danger:hover {
  background: #fecaca;
}

.btn-danger:disabled {
  opacity: .6;
  cursor: not-allowed;
}
</style>
