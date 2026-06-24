<template>
  <div class="voice-library-page">
    <div class="page-header">
      <div>
        <h1 class="page-title"><Drama :size="28" class="title-icon" /> 个人音色库</h1>
        <p class="page-subtitle">浏览全部音色，试听并收藏你喜欢的声音</p>
      </div>
      <button class="btn btn-primary manage-toggle" @click="openImportDialog">
        <Upload :size="16" />
        导入音色
      </button>
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

    <div v-if="showImportDialog" class="modal-backdrop" @click.self="showImportDialog = false">
      <form class="import-dialog" @submit.prevent="importQwenVoice">
        <div class="dialog-header">
          <div>
            <h2>导入 Qwen3-TTS 音色</h2>
            <p>导入已训练好的本地模型，生成一个可在创作工作台选择的个人音色。</p>
          </div>
          <button type="button" class="icon-button" @click="showImportDialog = false">
            <X :size="18" />
          </button>
        </div>

        <div class="import-summary">
          <div class="summary-icon">
            <Upload :size="18" />
          </div>
          <div>
            <strong>本地模型导入</strong>
            <span>登记模型路径和音色元数据，导入后会出现在个人音色库。</span>
          </div>
        </div>
        <div class="form-grid">
          <label>
            <span>音色名称</span>
            <input v-model.trim="importForm.displayName" required maxlength="50" placeholder="例如：我的旁白音色" />
          </label>
          <label>
            <span>音色标识</span>
            <input v-model.trim="importForm.voiceKey" required maxlength="100" placeholder="例如：my-qwen-voice" />
          </label>
          <label>
            <span>性别</span>
            <select v-model="importForm.gender">
              <option value="female">female</option>
              <option value="male">male</option>
              <option value="neutral">neutral</option>
            </select>
          </label>
          <label>
            <span>分类</span>
            <input v-model.trim="importForm.category" maxlength="50" placeholder="personal" />
          </label>
          <label>
            <span>风格</span>
            <input v-model.trim="importForm.style" maxlength="50" placeholder="custom" />
          </label>
          <label>
            <span>模型版本</span>
            <input v-model.trim="importForm.modelVersion" maxlength="120" placeholder="qwen3-tts-1.7b" />
          </label>
          <label class="full-row">
            <span>模型目录</span>
            <input v-model.trim="importForm.artifactPath" required maxlength="500" placeholder="D:/models/my-qwen-voice" />
          </label>
          <label class="full-row">
            <span>运行配置 JSON</span>
            <textarea v-model.trim="importForm.runtimeConfigJson" rows="3" placeholder='{"speaker":"default"}'></textarea>
          </label>
        </div>

        <p v-if="importError" class="form-error">{{ importError }}</p>

        <div class="dialog-actions">
          <button type="button" class="btn btn-outline" @click="showImportDialog = false">取消</button>
          <button type="submit" class="btn btn-primary" :disabled="isImporting">
            {{ isImporting ? "导入中..." : "导入" }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { Baby, Drama, Search, Settings2, Star, Upload, User, X } from "lucide-vue-next";
import VoiceCard from "../components/VoiceCard.vue";
import VoicePreview from "../components/VoicePreview.vue";
import { createModelArtifact, createVoice, deleteVoiceById, fetchVoices } from "../services/api.js";
import { useAppStore } from "../stores/app.js";

const router = useRouter();
const store = useAppStore();

const filterGender = ref("all");
const filterCategory = ref("all");
const showFavoritesOnly = ref(false);
const previewVoice = ref(null);
const manageMode = ref(false);
const loadError = ref("");
const showImportDialog = ref(false);
const isImporting = ref(false);
const importError = ref("");
const importForm = ref(defaultImportForm());

const categories = ["知识类", "播客类", "故事类", "情感类"];

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

onMounted(loadVoices);

async function loadVoices() {
  try {
    allVoices.value = (await fetchVoices()).map((voice) => ({
      ...voice,
      tags: voice.tags || [voice.style, voice.category].filter(Boolean),
    }));
  } catch (error) {
    loadError.value = `后端暂时不可用，当前展示本地示例音色：${error.message}`;
  }
}

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
  if (voice.ownerId && voice.dbId) {
    try {
      await deleteVoiceById(voice.dbId);
    } catch (error) {
      loadError.value = error.message;
      return;
    }
  }
  allVoices.value = allVoices.value.filter((item) => item.id !== voice.id);
}

function updateVoiceTags(id, tags) {
  const voice = allVoices.value.find((item) => item.id === id);
  if (voice) voice.tags = tags;
}

function goToWorkspace(voice) {
  store.selectedVoice = voice;
  router.push("/workspace");
}

function defaultImportForm() {
  return {
    displayName: "",
    voiceKey: "",
    gender: "female",
    category: "personal",
    style: "custom",
    modelVersion: "qwen3-tts-1.7b",
    artifactPath: "",
    runtimeConfigJson: "",
  };
}

function openImportDialog() {
  importError.value = "";
  importForm.value = defaultImportForm();
  showImportDialog.value = true;
}

async function importQwenVoice() {
  if (!store.isLoggedIn) {
    importError.value = "请先登录后再导入个人音色。";
    return;
  }
  const form = importForm.value;
  if (!form.displayName || !form.voiceKey || !form.artifactPath) {
    importError.value = "请填写音色名称、音色标识和模型目录。";
    return;
  }
  isImporting.value = true;
  importError.value = "";
  try {
    const artifact = await createModelArtifact({
      displayName: form.displayName,
      provider: "qwen3_tts",
      modelVersion: form.modelVersion,
      artifactPath: form.artifactPath,
      runtimeConfigJson: form.runtimeConfigJson || undefined,
      status: "ready",
    });
    await createVoice({
      voiceKey: form.voiceKey,
      displayName: form.displayName,
      gender: form.gender,
      style: form.style || "custom",
      category: form.category || "personal",
      description: "Imported Qwen3-TTS voice model",
      providers: [
        {
          provider: "qwen3_tts",
          providerVoiceId: `qwen3:${form.voiceKey}`,
          providerKind: "local_model",
          modelArtifactId: artifact.id,
          runtimeConfigJson: form.runtimeConfigJson || undefined,
          supportsWav: true,
          supportsMp3: true,
          isDefault: true,
        },
      ],
    });
    showImportDialog.value = false;
    await loadVoices();
  } catch (error) {
    importError.value = error.message;
  } finally {
    isImporting.value = false;
  }
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

.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: grid;
  place-items: center;
  padding: 24px;
  background: rgba(15, 23, 42, 0.54);
  backdrop-filter: blur(6px);
}

.import-dialog {
  width: min(760px, 100%);
  max-height: calc(100vh - 40px);
  overflow: auto;
  padding: 0;
  border-radius: 8px;
  background: var(--bg-card);
  border: 1px solid rgba(226, 232, 240, 0.92);
  box-shadow: 0 28px 90px rgba(15, 23, 42, 0.32);
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  padding: 22px 24px 18px;
  border-bottom: 1px solid var(--border-light);
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
}

.dialog-header > div {
  min-width: 0;
}

.dialog-header h2 {
  margin: 0 0 6px;
  color: var(--text);
  font-size: 21px;
  line-height: 1.25;
}

.dialog-header p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.55;
  max-width: 560px;
}

.icon-button {
  width: 36px;
  height: 36px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: #fff;
  color: var(--text-secondary);
  flex-shrink: 0;
  transition: all var(--transition);
}

.icon-button:hover {
  border-color: #cbd5e1;
  color: var(--text);
  background: var(--bg);
}

.import-summary {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 18px 24px 0;
  padding: 14px 16px;
  border: 1px solid #c7d2fe;
  border-radius: 8px;
  background: #eef2ff;
}

.summary-icon {
  width: 36px;
  height: 36px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: var(--primary);
  background: #fff;
  box-shadow: 0 1px 3px rgba(79, 70, 229, 0.16);
  flex-shrink: 0;
}

.import-summary strong {
  display: block;
  color: var(--text);
  font-size: 14px;
  line-height: 1.3;
}

.import-summary span {
  display: block;
  margin-top: 3px;
  color: var(--text-secondary);
  font-size: 13px;
  line-height: 1.45;
}

.preset-import {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  margin: 14px 24px 0;
  padding: 14px 16px;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  background: #f0fdf4;
}

.preset-import strong {
  display: block;
  color: var(--text);
  font-size: 14px;
  line-height: 1.3;
}

.preset-import span {
  display: block;
  margin-top: 4px;
  color: var(--text-secondary);
  font-size: 13px;
  line-height: 1.45;
}

.preset-import .btn {
  flex-shrink: 0;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  padding: 20px 24px 4px;
}

.form-grid label {
  display: grid;
  gap: 7px;
  min-width: 0;
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
}

.form-grid label:nth-child(1),
.form-grid label:nth-child(2),
.form-grid label:nth-child(7),
.form-grid label:nth-child(8) {
  position: relative;
}

.form-grid label:nth-child(1)::after,
.form-grid label:nth-child(2)::after,
.form-grid label:nth-child(7)::after {
  content: "必填";
  position: absolute;
  top: 0;
  right: 0;
  padding: 2px 6px;
  border-radius: 999px;
  color: var(--primary);
  background: var(--primary-light);
  font-size: 11px;
  font-weight: 600;
}

.form-grid input,
.form-grid select,
.form-grid textarea {
  width: 100%;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 11px 12px;
  color: var(--text);
  background: #fff;
  font: inherit;
  font-size: 14px;
  line-height: 1.4;
  transition: border-color var(--transition), box-shadow var(--transition), background var(--transition);
}

.form-grid input,
.form-grid select {
  height: 42px;
}

.form-grid textarea {
  min-height: 96px;
  resize: vertical;
}

.form-grid input:hover,
.form-grid select:hover,
.form-grid textarea:hover {
  border-color: #cbd5e1;
}

.form-grid input:focus,
.form-grid select:focus,
.form-grid textarea:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-light);
  background: #fff;
}

.form-grid input::placeholder,
.form-grid textarea::placeholder {
  color: var(--text-muted);
}

.full-row {
  grid-column: 1 / -1;
}

.form-error {
  margin: 16px 24px 0;
  padding: 10px 12px;
  border: 1px solid #fecaca;
  border-radius: 8px;
  background: #fef2f2;
  color: #b91c1c;
  font-size: 14px;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
  padding: 16px 24px 22px;
  border-top: 1px solid var(--border-light);
  background: #f8fafc;
}

.dialog-actions .btn {
  min-width: 92px;
}

@media (max-width: 640px) {
  .modal-backdrop {
    padding: 12px;
    align-items: end;
  }

  .import-dialog {
    width: 100%;
    max-height: calc(100vh - 24px);
  }

  .dialog-header,
  .form-grid,
  .dialog-actions {
    padding-left: 16px;
    padding-right: 16px;
  }

  .import-summary {
    margin-left: 16px;
    margin-right: 16px;
  }

  .preset-import {
    align-items: stretch;
    flex-direction: column;
    margin-left: 16px;
    margin-right: 16px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .dialog-actions {
    flex-direction: column-reverse;
  }

  .dialog-actions .btn {
    width: 100%;
  }
}
</style>
