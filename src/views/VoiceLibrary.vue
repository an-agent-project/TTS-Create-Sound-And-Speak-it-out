<template>
  <div class="voice-library-page">
    <div class="page-header">
      <div>
        <h1 class="page-title"><Drama :size="28" class="title-icon" /> 个人音色库</h1>
        <p class="page-subtitle">浏览全部音色，试听并收藏你喜欢的声音</p>
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
          @delete-voice="deleteVoice(voice.id)"
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
import { fetchVoices } from "../services/api.js";
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

const fallbackVoices = [
  { id: "zh-CN-XiaoxiaoNeural", name: "晓晓", gender: "female", style: "温柔", category: "知识类", description: "温柔自然的女声，适合知识讲解、课程录制和散文朗读", isRecommended: true, tags: ["温柔", "知识"] },
  { id: "zh-CN-YunxiNeural", name: "云希", gender: "male", style: "磁性", category: "故事类", description: "自然有表现力的男声，适合故事叙述和播客节目", isRecommended: true, tags: ["磁性", "故事"] },
  { id: "zh-CN-XiaoyiNeural", name: "晓伊", gender: "female", style: "活泼", category: "情感类", description: "活泼清亮的女声，适合轻松内容、情感表达和儿童故事", isRecommended: true, tags: ["活泼", "情感"] },
  { id: "zh-CN-YunjianNeural", name: "云健", gender: "male", style: "活力", category: "播客类", description: "充满力量感的男声，适合运动、户外和热血叙事", isRecommended: true, tags: ["活力", "播客"] },
  { id: "zh-CN-YunyangNeural", name: "云扬", gender: "male", style: "专业", category: "知识类", description: "稳定可靠的新闻播报感男声，适合正式内容和知识科普", tags: ["专业", "知识"] },
  { id: "zh-CN-YunxiaNeural", name: "云夏", gender: "male", style: "童趣", category: "故事类", description: "偏童真可爱的男声，适合儿童绘本和轻松故事", tags: ["童趣", "故事"] },
  { id: "zh-CN-liaoning-XiaobeiNeural", name: "辽宁小北", gender: "female", style: "方言", category: "播客类", description: "辽宁方言女声，适合地域特色播客和轻松内容", tags: ["方言", "播客"] },
  { id: "zh-CN-shaanxi-XiaoniNeural", name: "陕西小妮", gender: "female", style: "方言", category: "故事类", description: "陕西方言女声，适合方言故事和地方文化内容", tags: ["方言", "故事"] },
];

const allVoices = ref(fallbackVoices);

async function loadVoices() {
  allVoices.value = (await fetchVoices()).map((voice) => ({
    ...voice,
    tags: voice.tags || [voice.style, voice.category].filter(Boolean),
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

function deleteVoice(id) {
  allVoices.value = allVoices.value.filter((voice) => voice.id !== id);
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
