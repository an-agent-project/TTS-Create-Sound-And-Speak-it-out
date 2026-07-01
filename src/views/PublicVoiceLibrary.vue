<template>
  <div class="voice-library-page">
    <div class="page-header">
      <div>
        <h1 class="page-title"><Library :size="28" class="title-icon" /> 公共音色库</h1>
        <p class="page-subtitle">浏览公共音色，试听并存入你的个人音色库</p>
      </div>
    </div>

    <div v-if="toastMessage" class="toast">{{ toastMessage }}</div>

    <div class="filter-bar card">
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
    </div>

    <div class="section">
      <div class="grid grid-4">
        <VoiceCard
          v-for="voice in filteredVoices"
          :key="voice.id"
          :voice="voice"
          :is-favorite="store.isFavorite(voice.id)"
          :show-preview="true"
          :show-clone="store.isLoggedIn"
          :clone-label="clonedIds.has(voice.id) ? '已存入' : '存入我的音色库'"
          :clone-disabled="clonedIds.has(voice.id)"
          @toggle-favorite="store.toggleFavoriteVoice(voice.id)"
          @preview="previewVoice = voice"
          @select="goToWorkspace(voice)"
          @clone="cloneVoice(voice)"
        />
      </div>

      <div v-if="loading" class="empty-state">
        <Library :size="56" class="empty-icon" />
        <h3>加载中...</h3>
      </div>

      <div v-if="loadError" class="load-error">
        {{ loadError }}
        <button class="btn btn-secondary btn-sm" @click="loading = true; loadVoices().then(() => loading = false)">重试</button>
      </div>

      <div v-if="!loading && !loadError && filteredVoices.length === 0" class="empty-state">
        <Search :size="56" class="empty-icon" />
        <h3>暂无匹配的音色</h3>
        <p>尝试调整筛选条件</p>
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
import { Baby, Library, Search, User } from "lucide-vue-next";
import VoiceCard from "../components/VoiceCard.vue";
import VoicePreview from "../components/VoicePreview.vue";
import { fetchPublicVoices, cloneVoiceToPersonal } from "../services/api.js";
import { useAppStore } from "../stores/app.js";

const router = useRouter();
const store = useAppStore();

const filterGender = ref("all");
const filterCategory = ref("all");
const previewVoice = ref(null);
const loadError = ref("");
const clonedIds = ref(new Set());
const toastMessage = ref("");

const categories = ["知识类", "播客类", "故事类", "情感类"];

const allVoices = ref([]);

async function loadVoices() {
  try {
    allVoices.value = (await fetchPublicVoices()).map((voice) => ({
      ...voice,
      tags: voice.tags || [voice.style, voice.category].filter(Boolean),
    }));
  } catch (error) {
    loadError.value = "加载公共音色失败：" + error.message;
  }
}

const loading = ref(true);
onMounted(async () => {
  await loadVoices();
  loading.value = false;
});

const filteredVoices = computed(() => {
  let voices = allVoices.value;
  if (filterGender.value !== "all") {
    voices = voices.filter((v) => v.gender === filterGender.value);
  }
  if (filterCategory.value !== "all") {
    voices = voices.filter((v) => v.category === filterCategory.value);
  }
  return voices;
});

async function cloneVoice(voice) {
  try {
    await cloneVoiceToPersonal(voice.dbId);
    clonedIds.value.add(voice.id);
    toastMessage.value = "已存入个人音色库";
    setTimeout(() => { toastMessage.value = ""; }, 2000);
  } catch (error) {
    alert("存入失败：" + error.message);
  }
}

function goToWorkspace(voice) {
  store.selectedVoice = voice;
  router.push("/workspace");
}
</script>

<style scoped>
.title-icon { color: var(--primary); flex-shrink: 0; }
.empty-icon { color: var(--text-muted); opacity: 0.4; margin-bottom: 16px; }
.filter-bar { display: flex; flex-wrap: wrap; gap: 20px; padding: 16px 20px; margin-bottom: 24px; }
.filter-group { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.filter-label { font-size: 13px; font-weight: 600; color: var(--text-secondary); white-space: nowrap; }
.filter-options { display: flex; gap: 4px; flex-wrap: wrap; }
.filter-btn { display: inline-flex; align-items: center; gap: 4px; padding: 6px 14px; border-radius: 20px; background: var(--bg); border: 1px solid var(--border); font-size: 13px; color: var(--text-secondary); transition: all var(--transition); white-space: nowrap; cursor: pointer; }
.filter-btn:hover { border-color: var(--primary); color: var(--primary); }
.filter-btn.active { background: var(--primary); color: #fff; border-color: var(--primary); }
.page-header { display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; margin-bottom: 24px; }
.load-error { margin-top: 16px; color: #b91c1c; font-size: 14px; }
.toast { position: fixed; top: 80px; left: 50%; transform: translateX(-50%); background: #059669; color: #fff; padding: 10px 24px; border-radius: 8px; font-size: 14px; z-index: 999; animation: fadeInOut 2s ease; }
@keyframes fadeInOut { 0% { opacity: 0; transform: translateX(-50%) translateY(-10px); } 15% { opacity: 1; transform: translateX(-50%) translateY(0); } 85% { opacity: 1; } 100% { opacity: 0; } }
</style>
