<template>
  <div class="voice-preview-overlay" @click.self="closePreview">
    <div class="voice-preview-modal">
      <div class="modal-header">
        <h3>🎙️ 音色试听</h3>
        <button class="close-btn" @click="closePreview">✕</button>
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
        <div class="preview-sample">
          <div class="sample-title">📝 试听文本</div>
          <p class="sample-text">"{{ sampleText }}"</p>
        </div>
        <AudioPlayer
          :is-playing="isPlaying"
          :current-time="currentTime"
          :duration="duration"
          :volume="volume"
          :audio-url="audioUrl"
          @toggle-play="togglePreview"
          @seek="seekPreview"
          @volume-change="setVolume"
        />
        <p v-if="isLoading" class="preview-status">正在生成试听音频...</p>
        <p v-if="errorMessage" class="preview-error">{{ errorMessage }}</p>

        <div class="modal-actions">
          <button class="btn btn-secondary" @click="closePreview">关闭</button>
          <button class="btn btn-primary" @click="selectVoice">
            ✅ 选择此音色
          </button>
        </div>
      </div>
    </div>
  </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, ref, watch } from "vue";
import AudioPlayer from "./AudioPlayer.vue";
import { User, Baby, X, Check } from 'lucide-vue-next'

const props = defineProps({
  voice: { type: Object, required: true },
});

const emit = defineEmits(["close", "select"]);

const isPlaying = ref(false);
const isLoading = ref(false);
const currentTime = ref(0);
const duration = ref(15);
const volume = ref(80);
const audioUrl = ref("");
const errorMessage = ref("");
let audio = null;

const sampleText =
  "大家好，欢迎收听本期节目。今天我们要一起探索一个非常有趣的话题。让我们开始吧！";

async function ensurePreviewAudio() {
  if (audioUrl.value) return;

  isLoading.value = true;
  errorMessage.value = "";

  try {
    const response = await fetch("/api/tts/preview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: sampleText,
        voiceId: props.voice.id,
      }),
    });

    if (!response.ok) {
      throw new Error("试听音频生成失败");
    }

    const data = await response.json();
    audioUrl.value = data.audioUrl;
    duration.value = data.duration || duration.value;
  } catch (error) {
    errorMessage.value = error.message || "试听音频生成失败";
    throw error;
  } finally {
    isLoading.value = false;
  }
}

function bindAudioEvents() {
  audio.addEventListener("timeupdate", () => {
    currentTime.value = audio.currentTime || 0;
  });
  audio.addEventListener("loadedmetadata", () => {
    if (Number.isFinite(audio.duration)) {
      duration.value = audio.duration;
    }
  });
  audio.addEventListener("ended", () => {
    isPlaying.value = false;
    currentTime.value = 0;
  });
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

function seekPreview(ratio) {
  if (!audio || !duration.value) return;
  const nextTime = Math.max(0, Math.min(1, ratio)) * duration.value;
  audio.currentTime = nextTime;
  currentTime.value = nextTime;
}

function setVolume(nextVolume) {
  volume.value = Number(nextVolume);
  if (audio) {
    audio.volume = volume.value / 100;
  }
}

function stopPreview() {
  if (!audio) return;
  audio.pause();
  audio.currentTime = 0;
  isPlaying.value = false;
  currentTime.value = 0;
}

function closePreview() {
  stopPreview();
  emit("close");
}

function selectVoice() {
  stopPreview();
  emit("select");
  emit("close");
}

watch(
  () => props.voice.id,
  () => {
    stopPreview();
    audio = null;
    audioUrl.value = "";
    errorMessage.value = "";
    duration.value = 15;
  }
);

onBeforeUnmount(() => {
  stopPreview();
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
