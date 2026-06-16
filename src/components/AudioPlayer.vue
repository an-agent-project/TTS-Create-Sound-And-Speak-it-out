<template>
  <div class="audio-player">
    <div class="player-controls">
      <button class="player-btn" @click="$emit('prev')" title="上一个">
        ⏮
      </button>
      <button class="player-btn play-btn" @click="togglePlay" title="播放/暂停">
        {{ playing ? '⏸' : '▶️' }}
      </button>
      <button class="player-btn" @click="$emit('next')" title="下一个">
        ⏭
      </button>
    </div>
    <div class="player-progress">
      <span class="player-time">{{ formatTime(displayCurrentTime) }}</span>
      <div class="progress-bar" @click="onSeek">
        <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
      </div>
      <span class="player-time">{{ formatTime(displayDuration) }}</span>
    </div>
    <div class="player-extra">
      <div class="volume-control">
        <span>🔊</span>
        <input
          type="range"
          class="slider"
          min="0"
          max="100"
          :value="currentVolume"
          @input="onVolumeChange"
        />
      </div>
      <a v-if="audioUrl" :href="audioUrl" download class="btn btn-secondary btn-sm">
        ⬇ 下载
      </a>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from "vue";

const props = defineProps({
  isPlaying: { type: Boolean, default: false },
  currentTime: { type: Number, default: 0 },
  duration: { type: Number, default: 0 },
  volume: { type: Number, default: 80 },
  audioUrl: { type: String, default: "" },
});

const emit = defineEmits([
  "toggle-play",
  "prev",
  "next",
  "seek",
  "volume-change",
]);

const audio = ref(null);
const playing = ref(false);
const internalCurrentTime = ref(0);
const internalDuration = ref(0);
const currentVolume = ref(props.volume);

watch(
  () => props.audioUrl,
  (url) => {
    cleanupAudio();
    internalCurrentTime.value = 0;
    internalDuration.value = props.duration || 0;
    if (!url || url === "#") return;

    audio.value = new Audio(url);
    audio.value.volume = currentVolume.value / 100;
    audio.value.addEventListener("timeupdate", updateProgress);
    audio.value.addEventListener("loadedmetadata", updateDuration);
    audio.value.addEventListener("ended", stopPlaying);
  },
  { immediate: true },
);

watch(
  () => props.volume,
  (volume) => {
    currentVolume.value = volume;
    if (audio.value) {
      audio.value.volume = volume / 100;
    }
  },
);

function formatTime(s) {
  const m = Math.floor(s / 60);
  const sec = Math.floor(s % 60);
  return `${m}:${sec.toString().padStart(2, "0")}`;
}

const displayCurrentTime = computed(() => {
  return audio.value ? internalCurrentTime.value : props.currentTime;
});

const displayDuration = computed(() => {
  return audio.value ? internalDuration.value : props.duration;
});

const progressPercent = computed(() => {
  return displayDuration.value > 0
    ? (displayCurrentTime.value / displayDuration.value) * 100
    : 0;
});

async function togglePlay() {
  emit("toggle-play");
  if (!audio.value) {
    playing.value = !playing.value;
    return;
  }

  if (playing.value) {
    audio.value.pause();
    playing.value = false;
    return;
  }

  await audio.value.play();
  playing.value = true;
}

function onSeek(event) {
  const rect = event.currentTarget.getBoundingClientRect();
  const ratio = (event.clientX - rect.left) / rect.width;
  if (audio.value && displayDuration.value > 0) {
    audio.value.currentTime = ratio * displayDuration.value;
  }
  emit("seek", ratio);
}

function onVolumeChange(event) {
  const volume = Number(event.target.value);
  currentVolume.value = volume;
  if (audio.value) {
    audio.value.volume = volume / 100;
  }
  emit("volume-change", volume);
}

function updateProgress() {
  internalCurrentTime.value = audio.value?.currentTime || 0;
}

function updateDuration() {
  internalDuration.value = audio.value?.duration || props.duration || 0;
}

function stopPlaying() {
  playing.value = false;
  internalCurrentTime.value = 0;
}

function cleanupAudio() {
  if (!audio.value) return;
  audio.value.pause();
  audio.value.removeEventListener("timeupdate", updateProgress);
  audio.value.removeEventListener("loadedmetadata", updateDuration);
  audio.value.removeEventListener("ended", stopPlaying);
  audio.value = null;
  playing.value = false;
}

onBeforeUnmount(cleanupAudio);
</script>

<style scoped>
.audio-player {
  background: var(--bg);
  border-radius: var(--radius);
  padding: 16px 20px;
  border: 1px solid var(--border);
}

.player-controls {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 12px;
}

.player-btn {
  background: none;
  font-size: 22px;
  padding: 4px;
  border-radius: 50%;
  transition: transform var(--transition);
}

.player-btn:hover {
  transform: scale(1.15);
}

.play-btn {
  font-size: 36px;
}

.player-progress {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.player-time {
  font-size: 12px;
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
  min-width: 36px;
  text-align: center;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: var(--border);
  border-radius: 3px;
  cursor: pointer;
  position: relative;
}

.progress-fill {
  height: 100%;
  background: var(--primary);
  border-radius: 3px;
  transition: width 0.1s linear;
}

.player-extra {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.volume-control {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.volume-control span {
  font-size: 16px;
}

.volume-control .slider {
  max-width: 100px;
}
</style>
