<template>
  <div class="voice-preview-overlay" @click.self="$emit('close')">
    <div class="voice-preview-modal">
      <div class="modal-header">
        <h3>🎙️ 音色试听</h3>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </div>
      <div class="modal-body">
        <div class="preview-voice-info">
          <div class="preview-avatar">{{ voice.gender === 'male' ? '👨' : voice.gender === 'female' ? '👩' : '👶' }}</div>
          <div>
            <h4>{{ voice.name }}</h4>
            <div class="voice-meta">
              <span class="tag tag-primary">{{ voice.style }}</span>
              <span class="tag tag-success">{{ voice.category }}</span>
            </div>
          </div>
        </div>
        <p class="preview-desc">{{ voice.description }}</p>

        <div class="preview-sample">
          <div class="sample-title">📝 试听文本</div>
          <p class="sample-text">"大家好，欢迎收听本期节目。今天我们要一起探索一个非常有趣的话题。让我们开始吧！"</p>
        </div>

        <AudioPlayer
          :is-playing="isPlaying"
          :current-time="0"
          :duration="15"
          :volume="80"
          @toggle-play="isPlaying = !isPlaying"
        />

        <div class="modal-actions">
          <button class="btn btn-secondary" @click="$emit('close')">关闭</button>
          <button class="btn btn-primary" @click="$emit('select'); $emit('close')">
            ✅ 选择此音色
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import AudioPlayer from "./AudioPlayer.vue";

defineProps({
  voice: { type: Object, required: true },
});

defineEmits(["close", "select"]);

const isPlaying = ref(false);
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
  font-size: 18px;
  color: var(--text-muted);
  padding: 4px 8px;
  border-radius: var(--radius-xs);
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
  font-size: 36px;
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg);
  border-radius: 14px;
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

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>
