<template>
  <div class="audio-player">
    <div class="player-controls">
      <button class="player-btn" @click="$emit('prev')" title="上一个">
        ⏮
      </button>
      <button class="player-btn play-btn" @click="$emit('toggle-play')" title="播放/暂停">
        {{ isPlaying ? '⏸' : '▶️' }}
      </button>
      <button class="player-btn" @click="$emit('next')" title="下一个">
        ⏭
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
        <span>🔊</span>
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
        ⬇ 下载
      </a>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  isPlaying: { type: Boolean, default: false },
  currentTime: { type: Number, default: 0 },
  duration: { type: Number, default: 0 },
  volume: { type: Number, default: 80 },
  audioUrl: { type: String, default: "" },
});

const emit = defineEmits([
  "togglePlay",
  "prev",
  "next",
  "seek",
  "volumeChange",
]);

function formatTime(s) {
  const m = Math.floor(s / 60);
  const sec = Math.floor(s % 60);
  return `${m}:${sec.toString().padStart(2, "0")}`;
}

const progressPercent = computed(() => {
  return props.duration > 0 ? (props.currentTime / props.duration) * 100 : 0;
});

function onSeek(e) {
  const rect = e.currentTarget.getBoundingClientRect();
  const ratio = (e.clientX - rect.left) / rect.width;
  emit("seek", ratio);
}
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
