<template>
  <div class="voice-preview-overlay" @click.self="closePreview">
    <div class="voice-preview-modal">
      <div class="modal-header">
        <h3>音色试听</h3>
        <button class="close-btn" @click="closePreview">×</button>
      </div>
      <div class="modal-body">
        <div class="preview-voice-info">
          <div class="preview-avatar" :class="voice.gender">
            <User v-if="voice.gender === 'male'" :size="30" />
            <User v-else-if="voice.gender === 'female'" :size="30" />
            <Baby v-else :size="30" />
          </div>
          <div>
            <strong>{{ voice.name }}</strong>
            <div class="voice-meta">
              <span class="tag tag-primary">{{ voice.style }}</span>
              <span class="tag tag-success">{{ voice.category }}</span>
            </div>
          </div>
        </div>
        <p class="preview-desc">{{ voice.description }}</p>
        <div class="preview-sample">
          <div class="sample-title">试听文本</div>
          <p class="sample-text">"{{ sampleText }}"</p>
        </div>
        <AudioPlayer
          :is-playing="isPlaying"
          :current-time="currentTime"
          :duration="duration"
          :volume="volume"
          :audio-url="audioUrl"
          :managed-externally="true"
          @toggle-play="togglePreview"
          @seek="seekPreview"
          @volume-change="setVolume"
        />
        <div v-if="isLoading || previewProgress > 0" class="generation-progress preview-generation-progress">
          <div class="progress-row">
            <span>{{ previewStage }}</span>
            <strong>{{ previewProgress }}%</strong>
          </div>
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: previewProgress + '%' }"></div>
          </div>
        </div>
        <p v-if="isLoading" class="preview-status">正在生成试听音频...</p>
        <p v-if="errorMessage" class="preview-error">{{ errorMessage }}</p>

        <div class="modal-actions">
          <button class="btn btn-secondary" @click="closePreview">关闭</button>
          <button class="btn btn-primary" @click="selectVoice">选择此音色</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, ref, watch } from "vue";
import AudioPlayer from "./AudioPlayer.vue";
import { User, Baby } from "lucide-vue-next";

const props = defineProps({
  voice: { type: Object, required: true },
});

const emit = defineEmits(["close", "select"]);

const isPlaying = ref(false);
const isLoading = ref(false);
const previewProgress = ref(0);
const previewStage = ref("等待生成");
const currentTime = ref(0);
const duration = ref(15);
const volume = ref(80);
const audioUrl = ref("");
const errorMessage = ref("");
let audio = null;
let previewProgressTimer = null;

const sampleText =
  "大家好，欢迎收听本期节目。今天我们要一起探索一个非常有趣的话题。让我们开始吧！";

function clearPreviewProgressTimer() {
  if (!previewProgressTimer) return;
  window.clearInterval(previewProgressTimer);
  previewProgressTimer = null;
}

function startPreviewProgress() {
  clearPreviewProgressTimer();
  previewProgress.value = 8;
  previewStage.value = "准备试听任务";
  previewProgressTimer = window.setInterval(() => {
    if (previewProgress.value < 35) {
      previewStage.value = "加载音色模型";
      previewProgress.value += 3;
    } else if (previewProgress.value < 72) {
      previewStage.value = "合成试听音频";
      previewProgress.value += 2;
    } else if (previewProgress.value < 92) {
      previewStage.value = "写入音频文件";
      previewProgress.value += 1;
    }
  }, 700);
}

function finishPreviewProgress() {
  clearPreviewProgressTimer();
  previewStage.value = "试听音频已就绪";
  previewProgress.value = 100;
  window.setTimeout(() => {
    if (!isLoading.value) previewProgress.value = 0;
  }, 700);
}

function resetPreviewProgress() {
  clearPreviewProgressTimer();
  previewProgress.value = 0;
  previewStage.value = "等待生成";
}

async function ensurePreviewAudio() {
  if (audioUrl.value) return;

  isLoading.value = true;
  errorMessage.value = "";
  startPreviewProgress();

  try {
    const response = await fetch("/api/tts/preview", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(localStorage.getItem("auth_token")
          ? { Authorization: `Bearer ${localStorage.getItem("auth_token")}` }
          : {}),
      },
      body: JSON.stringify({
        text: sampleText,
        voiceId: props.voice.providerVoiceId || props.voice.id,
      }),
    });

    if (!response.ok) {
      throw new Error("试听音频生成失败");
    }

    const data = await response.json();
    audioUrl.value = data.audioUrl;
    duration.value = data.duration || duration.value;
    finishPreviewProgress();
  } catch (error) {
    errorMessage.value = error.message || "试听音频生成失败";
    resetPreviewProgress();
    throw error;
  } finally {
    isLoading.value = false;
  }
}

function onAudioTimeUpdate() {
  currentTime.value = audio?.currentTime || 0;
}

function onAudioLoadedMetadata() {
  if (audio && Number.isFinite(audio.duration)) {
    duration.value = audio.duration;
  }
}

function onAudioEnded() {
  isPlaying.value = false;
  currentTime.value = 0;
}

function bindAudioEvents() {
  audio.addEventListener("timeupdate", onAudioTimeUpdate);
  audio.addEventListener("loadedmetadata", onAudioLoadedMetadata);
  audio.addEventListener("ended", onAudioEnded);
}

async function togglePreview() {
  if (isLoading.value) return;

  if (audio && isPlaying.value) {
    audio.pause();
    isPlaying.value = false;
    return;
  }

  try {
    await ensurePreviewAudio();

    if (!audio) {
      audio = new Audio(audioUrl.value);
      audio.volume = volume.value / 100;
      bindAudioEvents();
    }

    await audio.play();
    isPlaying.value = true;
  } catch {
    isPlaying.value = false;
  }
}

function seekPreview(nextTime) {
  if (!audio || !duration.value) return;
  const clampedTime = Math.max(0, Math.min(duration.value, nextTime));
  audio.currentTime = clampedTime;
  currentTime.value = clampedTime;
}

function setVolume(nextVolume) {
  volume.value = Number(nextVolume);
  if (audio) {
    audio.volume = volume.value / 100;
  }
}

function resetAudioState({ clearUrl = false } = {}) {
  if (audio) {
    audio.pause();
    audio.removeEventListener("timeupdate", onAudioTimeUpdate);
    audio.removeEventListener("loadedmetadata", onAudioLoadedMetadata);
    audio.removeEventListener("ended", onAudioEnded);
    audio = null;
  }
  isPlaying.value = false;
  currentTime.value = 0;
  if (clearUrl) audioUrl.value = "";
}

function stopPreview() {
  resetAudioState();
}

function closePreview() {
  stopPreview();
  resetPreviewProgress();
  emit("close");
}

function selectVoice() {
  stopPreview();
  resetPreviewProgress();
  emit("select");
  emit("close");
}

watch(
  () => props.voice.id,
  () => {
    resetAudioState({ clearUrl: true });
    errorMessage.value = "";
    duration.value = 15;
    resetPreviewProgress();
  }
);

onBeforeUnmount(() => {
  resetAudioState();
  resetPreviewProgress();
});
</script>

<style scoped>
.voice-preview-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.2s ease;
}

.voice-preview-modal {
  background: var(--bg-card);
  border-radius: var(--radius);
  width: 90%;
  max-width: 520px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--shadow-lg);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-light);
}

.modal-header h3 {
  font-size: 18px;
}

.close-btn {
  background: none;
  color: var(--text-muted);
  padding: 4px 8px;
  border-radius: var(--radius-xs);
  display: flex;
}

.close-btn:hover {
  background: var(--bg);
  color: var(--text);
}

.modal-body {
  padding: 24px;
}

.preview-voice-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.preview-avatar {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg);
  border-radius: 14px;
}

.preview-avatar.male {
  background: #dbeafe;
  color: #3b82f6;
}
.preview-avatar.female {
  background: #fce7f3;
  color: #ec4899;
}
.preview-avatar.child {
  background: #fef3c7;
  color: #f59e0b;
}

.voice-meta {
  display: flex;
  gap: 4px;
  margin-top: 4px;
}

.preview-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 20px;
}

.preview-sample {
  background: var(--bg);
  border-radius: var(--radius-sm);
  padding: 16px;
  margin-bottom: 20px;
}

.sample-title {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-secondary);
}

.sample-text {
  font-size: 15px;
  line-height: 1.7;
  color: var(--text);
}

.generation-progress {
  margin-top: 14px;
  padding: 12px;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-sm);
  background: var(--bg);
}

.progress-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
  font-size: 13px;
  color: var(--text-secondary);
}

.progress-row strong {
  color: var(--primary);
  font-variant-numeric: tabular-nums;
}

.progress-track {
  height: 7px;
  overflow: hidden;
  border-radius: 999px;
  background: var(--border);
}

.progress-fill {
  height: 100%;
  border-radius: inherit;
  background: var(--primary);
  transition: width 0.25s ease;
}

.preview-status,
.preview-error {
  margin-top: 10px;
  font-size: 13px;
}

.preview-status {
  color: var(--text-secondary);
}

.preview-error {
  color: var(--danger);
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
