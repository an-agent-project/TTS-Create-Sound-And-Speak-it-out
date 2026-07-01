<template>
  <div class="workspace-page">
    <div class="page-header">
      <h1 class="page-title"><Pen :size="28" class="title-icon" /> 创作工作台</h1>
      <p class="page-subtitle">选择场景 → 输入文本 → 调整参数 → 一键生成专业配音</p>
    </div>

    <div class="split-layout">
      <!-- Left: Input Area -->
      <div>
        <!-- Scene Selection -->
        <div class="section">
          <div class="section-title">
            <Clapperboard :size="22" class="section-icon" /> 选择场景模板
          </div>
          <div class="grid grid-4">
            <SceneCard
              v-for="scene in scenes"
              :key="scene.id"
              :scene="scene"
              @select="selectScene(scene)"
            />
          </div>
        </div>

        <!-- Text Input -->
        <div class="section">
          <div class="section-title">
            <FileText :size="22" class="section-icon" /> 文本内容
          </div>
          <TextEditor
            v-model="textContent"
            placeholder="请在此粘贴或输入您要配音的文本内容..." showLang v-model:outputLang="outputLang" />
          <div v-if="outputLang !== 'zh'" class="translation-panel">
            <div class="translation-header">
              <div>
                <strong>翻译预览</strong>
                <span>{{ targetLanguageLabel }} · 可编辑后再生成</span>
              </div>
              <button class="btn btn-secondary btn-sm" type="button" :disabled="isTranslating || !textContent.trim()" @click="previewTranslation">
                <Loader v-if="isTranslating" :size="14" class="spin" />
                <span>{{ isTranslating ? '翻译中...' : '翻译预览' }}</span>
              </button>
            </div>
            <textarea
              v-model="translatedContent"
              class="translation-textarea"
              rows="7"
              :placeholder="`点击翻译预览生成${targetLanguageLabel}译文，也可以直接在这里粘贴译文。`"
            ></textarea>
            <div class="translation-footer">
              <span :class="translationError ? 'translation-error' : 'translation-status'">{{ translationStatus }}</span>
              <span>{{ translatedContent.length }} 字符</span>
            </div>
          </div>
        </div>

        <!-- Voice Selection -->
        <div class="section">
          <div class="section-title">
            <Drama :size="22" class="section-icon" /> 选择音色
          </div>
          <div class="voice-selector grid grid-2">
            <div
              v-for="voice in availableVoices"
              :key="voice.id"
              class="card voice-option"
              :class="{ selected: selectedVoice?.id === voice.id }"
              @click="selectedVoice = voice"
            >
              <div class="voice-option-top">
                <span class="voice-option-icon">
                  <User v-if="voice.gender === 'male'" :size="28" />
                  <User v-else-if="voice.gender === 'female'" :size="28" />
                  <Baby v-else :size="28" />
                </span>
                <div>
                  <strong>{{ voice.name }}</strong>
                  <div class="voice-option-meta">
                    <span class="tag tag-primary">{{ voice.style }}</span>
                    <span class="tag tag-success">{{ voice.category }}</span>
                  </div>
                </div>
                <button class="btn btn-secondary btn-sm" @click.stop="previewVoice = voice">
                  <Play :size="14" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Controls & Preview -->
      <div>
        <!-- Parameter Settings -->
        <div class="section">
          <div class="section-title">
            <Settings :size="22" class="section-icon" /> 参数设置
          </div>
          <div class="card settings-card">
            <div class="form-group">
              <label class="form-label">语速</label>
              <div class="slider-container">
                <span style="font-size:13px;color:var(--text-muted);">慢</span>
                <input type="range" class="slider" min="0.5" max="2.0" step="0.1" v-model.number="settings.speed" />
                <span style="font-size:13px;color:var(--text-muted);">快</span>
                <span class="slider-value">{{ settings.speed }}x</span>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">音调</label>
              <div class="slider-container">
                <span style="font-size:13px;color:var(--text-muted);">低</span>
                <input type="range" class="slider" min="-50" max="50" step="5" v-model.number="settings.pitch" />
                <span style="font-size:13px;color:var(--text-muted);">高</span>
                <span class="slider-value">{{ formatPitch(settings.pitch) }}</span>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">人声音量</label>
              <div class="slider-container">
                <span style="font-size:13px;color:var(--text-muted);">静</span>
                <input type="range" class="slider" min="0" max="150" step="5" v-model.number="settings.voiceVolume" />
                <span style="font-size:13px;color:var(--text-muted);">强</span>
                <span class="slider-value">{{ settings.voiceVolume }}%</span>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">情感风格</label>
              <div class="emotion-grid">
                <button
                  v-for="em in emotions"
                  :key="em.value"
                  class="emotion-btn"
                  :class="{ active: settings.emotion === em.value }"
                  @click="settings.emotion = em.value"
                >
                  <component :is="em.lucideIcon" :size="22" />
                  <span>{{ em.label }}</span>
                </button>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">背景音乐</label>
              <select class="form-select" v-model="settings.bgmType">
                <option value="none">无背景音乐</option>
                <option v-for="material in bgmMaterials" :key="material.materialKey" :value="material.materialKey">
                  {{ material.title || material.filename }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">分段长度</label>
              <div class="slider-container">
                <span style="font-size:13px;color:var(--text-muted);">短</span>
                <input type="range" class="slider" min="40" max="300" step="10" v-model.number="settings.maxSegmentLength" />
                <span style="font-size:13px;color:var(--text-muted);">长</span>
                <span class="slider-value">{{ settings.maxSegmentLength }}字</span>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">停顿强度</label>
              <div class="slider-container">
                <span style="font-size:13px;color:var(--text-muted);">紧凑</span>
                <input type="range" class="slider" min="0.5" max="2" step="0.1" v-model.number="settings.pauseScale" />
                <span style="font-size:13px;color:var(--text-muted);">舒缓</span>
                <span class="slider-value">{{ settings.pauseScale.toFixed(1) }}x</span>
              </div>
            </div>

            <div class="form-group" v-if="settings.bgmType !== 'none'">
              <label class="form-label">BGM音量</label>
              <div class="slider-container">
                <input type="range" class="slider" min="0" max="100" v-model.number="settings.bgmVolume" />
                <span class="slider-value">{{ settings.bgmVolume }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Generate Button -->
        <button
          class="btn btn-primary btn-lg btn-block generate-btn"
          :disabled="!canGenerate"
          @click="generateAudio"
        >
          <Rocket v-if="!isGenerating" :size="20" />
          <Loader v-else :size="20" class="spin" />
          {{ isGenerating ? '正在生成...' : '一键生成配音' }}
        </button>
        <div v-if="isGenerating" class="job-progress-card">
          <div class="job-progress-header">
            <span>{{ generationMessage || "正在准备生成任务" }}</span>
            <strong>{{ generationProgress }}%</strong>
          </div>
          <div class="job-progress-track">
            <div class="job-progress-fill" :style="{ width: generationProgress + '%' }"></div>
          </div>
        </div>
        <div v-if="generationError" class="error-card">
          {{ generationError }}
        </div>

        <!-- Generated Result -->
        <div v-if="generatedWork" class="section preview-section">
          <div class="section-title">
            <CheckCircle :size="22" class="section-icon" /> 配音预览
          </div>
          <div class="card success-card">
            <div class="success-header">
              <CheckCircle :size="28" style="color: #10b981;" />
              <div>
                <strong style="font-size:16px;">配音生成成功!</strong>
                <div style="font-size:13px;color:var(--text-secondary);margin-top:2px;">
                  {{ generatedWork.sceneName }} · {{ generatedWork.voiceName }} · 时长约{{ generatedWork.duration }}秒
                </div>
              </div>
            </div>
            <AudioPlayer
              :is-playing="isPlaying"
              :current-time="0"
              :duration="generatedWork.duration || 0"
              :volume="80"
              :audio-url="generatedWork.audioUrl"
              @toggle-play="isPlaying = !isPlaying"
            />
            <div class="preview-actions">
              <button class="btn btn-secondary" @click="regenerate">重新生成</button>
              <button class="btn btn-primary" @click="saveWork">保存作品</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Preview Modal -->
    <VoicePreview
      v-if="previewVoice"
      :voice="previewVoice"
      @close="previewVoice = null"
      @select="selectVoiceFromPreview"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from "vue";
import { useAppStore } from "../stores/app.js";
import { createJobEventSource, fetchMaterials, fetchVoices, startGenerateTtsJob, translateText } from "../services/api.js";
import SceneCard from "../components/SceneCard.vue";
import TextEditor from "../components/TextEditor.vue";
import AudioPlayer from "../components/AudioPlayer.vue";
import VoicePreview from "../components/VoicePreview.vue";
import {
  Pen, Clapperboard, FileText, Drama, Settings, Rocket, Loader, CheckCircle,
  Play, User, Baby, Smile, Laugh, Frown, Zap, Mic, BookOpen, Library, Heart
} from 'lucide-vue-next'

const store = useAppStore();

const scenes = [
  { id: "podcast", name: "播客模式", iconComponent: Mic, description: "适合播客节目、脱口秀", color: "#6366f1", defaultSpeed: 1.0 },
  { id: "lecture", name: "知识讲解", iconComponent: BookOpen, description: "适合课程录制、知识分享", color: "#10b981", defaultSpeed: 0.9 },
  { id: "storytelling", name: "故事叙述", iconComponent: Library, description: "适合有声小说、儿童故事", color: "#f59e0b", defaultSpeed: 0.85 },
  { id: "emotional", name: "情感朗读", iconComponent: Heart, description: "适合散文诗歌、情感表达", color: "#ef4444", defaultSpeed: 0.8 },
];

const availableVoices = ref([]);
const bgmMaterials = ref([]);
const voiceLoadError = ref("");

const emotions = [
  { value: "calm", lucideIcon: Smile, label: "平静" },
  { value: "happy", lucideIcon: Laugh, label: "开心" },
  { value: "sad", lucideIcon: Frown, label: "悲伤" },
  { value: "excited", lucideIcon: Zap, label: "激动" },
];

const selectedScene = ref(store.selectedScene || null);
const selectedVoice = ref(store.selectedVoice || null);
const textContent = ref(store.textContent || "");
const settings = ref({
  ...store.settings,
  pitch: normalizePitch(store.settings.pitch),
});
const isGenerating = ref(false);
const generationProgress = ref(0);
const generationMessage = ref("");
const generationJobSource = ref(null);
const isPlaying = ref(false);
const generatedWork = ref(null);
const previewVoice = ref(null);
const generationError = ref("");
const outputLang = ref("zh");
const translatedContent = ref("");
const translationError = ref("");
const isTranslating = ref(false);
onMounted(async () => {
  try {
    availableVoices.value = (await fetchVoices()).map((voice) => ({
      ...voice,
      tags: voice.tags || [voice.style, voice.category].filter(Boolean),
    }));
    bgmMaterials.value = await fetchMaterials("bgm");
  } catch (error) {
    voiceLoadError.value = `音色列表加载失败：${error.message}`;
  }
});
const targetLanguageNames = {
  zh: "中文",
  en: "English",
  ja: "日本語",
  ko: "한국어",
  fr: "Français",
  de: "Deutsch",
  es: "Español",
  it: "Italiano",
  pt: "Português",
  ru: "Русский",
};

const canGenerate = computed(() => {
  return textContent.value.trim().length > 0 && selectedVoice.value !== null && !isGenerating.value && !isTranslating.value;
});

const targetLanguageLabel = computed(() => targetLanguageNames[outputLang.value] || outputLang.value);
const generateContent = computed(() => {
  if (outputLang.value !== "zh" && translatedContent.value.trim()) {
    return translatedContent.value;
  }
  return textContent.value;
});
const translationStatus = computed(() => {
  if (translationError.value) return translationError.value;
  if (isTranslating.value) return "正在生成译文...";
  if (translatedContent.value.trim()) return "译文已生成，可直接编辑后合成。";
  return "尚未生成译文。";
});

function normalizePitch(pitch) {
  if (typeof pitch === "number") return pitch;
  return { low: -20, normal: 0, high: 20 }[pitch] ?? 0;
}

function formatPitch(pitch) {
  const value = Number(pitch) || 0;
  return `${value > 0 ? "+" : ""}${value}Hz`;
}

function selectScene(scene) {
  selectedScene.value = scene;
  settings.value.speed = scene.defaultSpeed;
}

watch([textContent, outputLang], () => {
  translatedContent.value = "";
  translationError.value = "";
});

function selectVoiceFromPreview() {
  if (previewVoice.value) {
    selectedVoice.value = previewVoice.value;
    previewVoice.value = null;
  }
}

async function previewTranslation() {
  if (!textContent.value.trim() || outputLang.value === "zh") return;
  isTranslating.value = true;
  translationError.value = "";
  try {
    const result = await translateText({
      content: textContent.value,
      targetLang: outputLang.value,
    });
    translatedContent.value = result.translatedText || "";
  } catch (error) {
    translationError.value = error.message || "翻译失败，请稍后重试。";
  } finally {
    isTranslating.value = false;
  }
}

async function generateAudio() {
  if (!canGenerate.value) return;
  generationError.value = "";
  if (outputLang.value !== "zh" && !translatedContent.value.trim()) {
    await previewTranslation();
    if (!translatedContent.value.trim()) {
      generationError.value = translationError.value || "请先完成翻译预览。";
      return;
    }
  }
  isGenerating.value = true;

  try {
    generationProgress.value = 1;
    generationMessage.value = "正在提交生成任务";
    const { jobId } = await startGenerateTtsJob({
      content: textContent.value,
      sceneId: selectedScene.value?.id || "",
      voiceId: selectedVoice.value.providerVoiceId || selectedVoice.value.id,
      speed: settings.value.speed,
      pitch: settings.value.pitch,
      voiceVolume: settings.value.voiceVolume,
      emotion: settings.value.emotion,
      bgmType: settings.value.bgmType,
      bgmVolume: settings.value.bgmVolume,
      maxSegmentLength: settings.value.maxSegmentLength,
      pauseScale: settings.value.pauseScale,
      outputLang: outputLang.value,
      translatedContent: outputLang.value !== "zh" ? generateContent.value : undefined,
    });
    const work = await waitForGenerateJob(jobId);
    generatedWork.value = work;
    store.addWork(work);
  } catch (error) {
    generationError.value = error.message || "配音生成失败，请稍后重试。";
  } finally {
    isGenerating.value = false;
  }
}


function waitForGenerateJob(jobId) {
  closeGenerationJobSource();
  return new Promise((resolve, reject) => {
    const source = createJobEventSource(jobId);
    generationJobSource.value = source;

    source.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        generationProgress.value = Math.max(0, Math.min(100, Number(payload.progress || 0)));
        generationMessage.value = payload.message || "正在生成配音";
        if (payload.status === "completed") {
          closeGenerationJobSource();
          resolve(payload.result?.work);
        } else if (payload.status === "failed") {
          closeGenerationJobSource();
          reject(new Error(payload.error || payload.message || "配音生成失败"));
        }
      } catch (error) {
        closeGenerationJobSource();
        reject(error);
      }
    };

    source.onerror = () => {
      closeGenerationJobSource();
      reject(new Error("生成进度连接中断"));
    };
  });
}

function closeGenerationJobSource() {
  if (generationJobSource.value) {
    generationJobSource.value.close();
    generationJobSource.value = null;
  }
}
function regenerate() {
  generatedWork.value = null;
  generationError.value = "";
}

async function saveWork() {
  if (generatedWork.value) {
    store.addWork(generatedWork.value);
    await store.fetchWorks();
    alert("✅ 作品已保存！可在「我的作品」中查看。");
  }
}
onBeforeUnmount(() => {
  closeGenerationJobSource();
});
</script>

<style scoped>
.workspace-page {
  padding-bottom: 40px;
}


.job-progress-card {
  margin: -8px 0 18px;
  padding: 14px;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-sm);
  background: var(--bg-card);
}

.job-progress-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
  font-size: 13px;
  color: var(--text-secondary);
}

.job-progress-header strong {
  color: var(--primary);
}

.job-progress-track {
  height: 8px;
  overflow: hidden;
  border-radius: 999px;
  background: var(--bg);
}

.job-progress-fill {
  height: 100%;
  border-radius: inherit;
  background: var(--primary);
  transition: width .25s ease;
}
.error-card {
  margin: -8px 0 18px;
  padding: 12px 14px;
  border: 1px solid #fecaca;
  border-radius: var(--radius-sm);
  background: #fef2f2;
  color: #b91c1c;
  font-size: 14px;
}

.section-icon {
  color: var(--primary);
  flex-shrink: 0;
}

.title-icon {
  color: var(--primary);
  flex-shrink: 0;
}

.translation-panel {
  margin-top: 12px;
  padding: 14px;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-sm);
  background: var(--bg-card);
}

.translation-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.translation-header strong {
  display: block;
  font-size: 14px;
  color: var(--text);
}

.translation-header span {
  font-size: 12px;
  color: var(--text-muted);
}

.translation-textarea {
  width: 100%;
  min-height: 150px;
  resize: vertical;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 12px;
  background: var(--bg);
  color: var(--text);
  font-size: 14px;
  line-height: 1.7;
  outline: none;
}

.translation-textarea:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12);
}

.translation-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-muted);
}

.translation-error {
  color: #b91c1c;
}

.translation-status {
  color: var(--text-secondary);
}
.voice-option {
  cursor: pointer;
  padding: 14px 16px;
  transition: all var(--transition);
}

.voice-option.selected {
  border-color: var(--primary);
  background: var(--primary-light);
}

.voice-option-top {
  display: flex;
  align-items: center;
  gap: 10px;
}

.voice-option-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg);
  border-radius: 10px;
  flex-shrink: 0;
  color: var(--primary);
}

.voice-option-top > div {
  flex: 1;
  min-width: 0;
}

.voice-option-top strong {
  font-size: 14px;
  display: block;
  margin-bottom: 4px;
}

.voice-option-meta {
  display: flex;
  gap: 4px;
}

.settings-card {
  padding: 20px;
}

.emotion-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.emotion-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 8px;
  border-radius: var(--radius-sm);
  background: var(--bg);
  border: 1px solid var(--border);
  font-size: 12px;
  color: var(--text-secondary);
  transition: all var(--transition);
}

.emotion-btn:hover {
  border-color: var(--primary);
}

.emotion-btn.active {
  border-color: var(--primary);
  background: var(--primary-light);
  color: var(--primary);
  font-weight: 600;
}

.generate-btn {
  margin-bottom: 24px;
  font-size: 18px;
  padding: 16px;
  border-radius: var(--radius);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.preview-section {
  margin-top: 0;
}

.success-card {
  background: #f0fdf4;
  border-color: #bbf7d0;
}

.success-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.preview-actions {
  display: flex;
  gap: 10px;
  margin-top: 16px;
  flex-wrap: wrap;
}
</style>
