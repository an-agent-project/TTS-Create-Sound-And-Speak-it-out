<template>
  <div class="audio-player">
    <div class="player-controls">
      <button class="player-btn" @click="$emit('prev')" title="上一个">
        <SkipBack :size="20" />
      </button>
      <button class="player-btn play-btn" @click="$emit('toggle-play')" title="播放/暂停">
        <Pause v-if="isPlaying" :size="24" />
        <Play v-else :size="24" />
      </button>
      <button class="player-btn" @click="$emit('next')" title="下一个">
        <SkipForward :size="20" />
      </button>
    </div>
    <div class="player-progress">
      <span class="player-time">{{ formatTime(currentTime) }}</span>
      <div class="progress-bar" @click="onSeek">
        <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
      </div>
      <span class="player-time">{{ formatTime(duration) }}</span>
    </div>
    <div class="player-extra">
      <div class="volume-control">
        <Volume2 :size="18" />
        <input
          type="range"
          class="slider"
          min="0"
          max="100"
          :value="volume"
          @input="$emit('volumeChange', $event.target.value)"
        />
      </div>
      <a v-if="audioUrl" :href="audioUrl" download class="btn btn-secondary btn-sm">
        <Download :size="14" /> 下载
      </a>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { SkipBack, SkipForward, Play, Pause, Volume2, Download } from 'lucide-vue-next'

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
  "volumeChange",
]);

function formatTime(seconds) {
  if (!seconds || isNaN(seconds) || seconds < 0) return "0:00";
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${String(s).padStart(2, "0")}`;
}

const progressPercent = computed(() => {
  if (!props.duration || props.duration === 0) return 0;
  return Math.min((props.currentTime / props.duration) * 100, 100);
});

function onSeek(e) {
  const rect = e.currentTarget.getBoundingClientRect();
  const ratio = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
  emit("seek", ratio * props.duration);
}
</script>

<style scoped>
.audio-player {
  padding: 8px 0;
}

.player-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 12px;
}

.player-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  padding: 6px;
  border-radius: 50%;
  transition: all var(--transition);
  display: flex;
  align-items: center;
  justify-content: center;
}

.player-btn:hover {
  color: var(--primary);
  background: var(--primary-light);
}

.play-btn {
  width: 48px;
  height: 48px;
  background: var(--primary);
  color: #fff;
  border-radius: 50%;
}

.play-btn:hover {
  background: var(--primary-hover);
  color: #fff;
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
  min-width: 36px;
  font-variant-numeric: tabular-nums;
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
}

.volume-control {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  color: var(--text-muted);
}

.volume-control .slider {
  flex: 1;
  -webkit-appearance: none;
  height: 4px;
  border-radius: 2px;
  background: var(--border);
  outline: none;
}

.volume-control .slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--primary);
  cursor: pointer;
}
</style>
