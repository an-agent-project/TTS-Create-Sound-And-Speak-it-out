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
          @toggle-favorite="store.toggleFavoriteVoice(voice.id)"
          @preview="previewVoice = voice"
          @select="goToWorkspace(voice)"
          @delete-voice="deleteVoice(voice)"
          @update-tags="(tags) => updateVoiceTags(voice.id, tags)"
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
import { Baby, Drama, Search, Settings2, Star, User } from "lucide-vue-next";
import VoiceCard from "../components/VoiceCard.vue";
import VoicePreview from "../components/VoicePreview.vue";
import { fetchPersonalVoices, deleteVoiceById } from "../services/api.js";
import { useAppStore } from "../stores/app.js";

const router = useRouter();
const store = useAppStore();

const filterGender = ref("all");
const filterCategory = ref("all");
const showFavoritesOnly = ref(false);
const previewVoice = ref(null);
const manageMode = ref(false);
const loadError = ref("");

const categories = ["知识类", "播客类", "故事类", "情感类", "个人音色"];



const allVoices = ref([]);

async function loadVoices() {
  allVoices.value = (await fetchPersonalVoices()).map((voice) => ({
    ...voice,
    tags: voice.tags || [voice.style, voice.category].filter(Boolean),
    fromPublic: !!voice.sourceVoiceId,
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

async function deleteVoice(voice) {
  try {
    await deleteVoiceById(voice.dbId);
    allVoices.value = allVoices.value.filter((item) => item.id !== voice.id);
    if (store.selectedVoice?.id === voice.id || store.selectedVoice?.dbId === voice.dbId) {
      store.selectedVoice = null;
    }
  } catch (error) {
    alert("Failed to delete: " + error.message);
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


</style>
