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
            placeholder="请在此粘贴或输入您要配音的文本内容..."
          />
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
              <select class="form-select" v-model="settings.pitch">
                <option value="low">低沉</option>
                <option value="normal">正常</option>
                <option value="high">高昂</option>
              </select>
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
                <option value="relax">轻松舒缓</option>
                <option value="warm">温暖治愈</option>
                <option value="tense">紧张悬念</option>
                <option value="formal">正式大气</option>
              </select>
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
              audio-url="#"
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
import { ref, computed } from "vue";
import { useAppStore } from "../stores/app.js";
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

const availableVoices = [
  { id: "zh-CN-XiaoxiaoNeural", name: "晓晓", gender: "female", style: "温柔", category: "知识类", description: "温柔知性的女声，适合知识讲解、课程录制" },
  { id: "zh-CN-YunxiNeural", name: "云希", gender: "male", style: "磁性", category: "故事类", description: "磁性的男声，适合故事叙述、播客节目" },
  { id: "zh-CN-XiaoyiNeural", name: "晓伊", gender: "female", style: "活泼", category: "情感类", description: "活泼可爱的女声，适合轻松内容" },
  { id: "zh-CN-YunjianNeural", name: "云健", gender: "male", style: "活力", category: "播客类", description: "充满活力的男声，适合运动、户外类内容" },
  { id: "zh-CN-XiaochenNeural", name: "晓辰", gender: "female", style: "沉稳", category: "知识类", description: "沉稳大气的女声，适合正式场合配音" },
  { id: "zh-CN-YunyangNeural", name: "云扬", gender: "male", style: "阳光", category: "播客类", description: "阳光开朗的男声，适合轻松内容" },
];

const emotions = [
  { value: "calm", lucideIcon: Smile, label: "平静" },
  { value: "happy", lucideIcon: Laugh, label: "开心" },
  { value: "sad", lucideIcon: Frown, label: "悲伤" },
  { value: "excited", lucideIcon: Zap, label: "激动" },
];

const selectedScene = ref(null);
const selectedVoice = ref(null);
const textContent = ref("");
const settings = ref({
  speed: 1.0,
  pitch: "normal",
  emotion: "calm",
  bgmType: "none",
  bgmVolume: 30,
});
const isGenerating = ref(false);
const isPlaying = ref(false);
const generatedWork = ref(null);
const previewVoice = ref(null);

const canGenerate = computed(() => {
  return textContent.value.trim().length > 0 && selectedVoice.value !== null && !isGenerating.value;
});

function selectScene(scene) {
  selectedScene.value = scene;
  settings.value.speed = scene.defaultSpeed;
}

function selectVoiceFromPreview() {
  if (previewVoice.value) {
    selectedVoice.value = previewVoice.value;
    previewVoice.value = null;
  }
}

async function generateAudio() {
  if (!canGenerate.value) return;
  isGenerating.value = true;

  await new Promise((r) => setTimeout(r, 1500));

  generatedWork.value = {
    title: selectedScene.value
      ? `【${selectedScene.value.name}】${textContent.value.slice(0, 20)}...`
      : textContent.value.slice(0, 30) + "...",
    content: textContent.value,
    sceneId: selectedScene.value?.id || "",
    sceneName: selectedScene.value?.name || "通用",
    voiceId: selectedVoice.value.id,
    voiceName: selectedVoice.value.name,
    speed: settings.value.speed,
    pitch: settings.value.pitch,
    emotion: settings.value.emotion,
    bgmType: settings.value.bgmType,
    bgmVolume: settings.value.bgmVolume,
    duration: Math.ceil(textContent.value.length / 4),
  };

  isGenerating.value = false;
}

function regenerate() {
  generatedWork.value = null;
}

function saveWork() {
  if (generatedWork.value) {
    store.addWork(generatedWork.value);
    alert("✅ 作品已保存！可在「我的作品」中查看。");
  }
}
</script>

<style scoped>
.workspace-page {
  padding-bottom: 40px;
}

.section-icon {
  color: var(--primary);
  flex-shrink: 0;
}

.title-icon {
  color: var(--primary);
  flex-shrink: 0;
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

