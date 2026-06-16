<template>
  <div class="voice-preview-overlay" @click.self="$emit('close')">
    <div class="voice-preview-modal">
      <div class="modal-header">
        <h3>音色试听</h3>
        <button class="close-btn" @click="$emit('close')"><X :size="18" /></button>
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
          <div class="sample-title">试听文本示例：</div>
          <div class="sample-text">
            "你好，我是{{ voice.name }}。欢迎使用有声读物智能生成系统，让我为你的文字赋予动人的声音。"
          </div>
        </div>
        <AudioPlayer
          :is-playing="isPlaying"
          :current-time="0"
          :duration="8"
          :volume="80"
          audio-url="#"
          @toggle-play="isPlaying = !isPlaying"
        />
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="$emit('close')">关闭</button>
          <button class="btn btn-primary" @click="$emit('select')">
            <Check :size="16" /> 选择此音色
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import AudioPlayer from "./AudioPlayer.vue";
import { User, Baby, X, Check } from 'lucide-vue-next'

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
