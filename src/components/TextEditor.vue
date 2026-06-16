<template>
  <div class="text-editor">
    <div class="editor-toolbar">
      <span class="toolbar-info">
        字数：<strong>{{ charCount }}</strong>
        {{ charCount > 500 ? '| 预估时长：~' + estimatedDuration + ' 分钟' : '' }}
      </span>
      <div class="toolbar-actions">
        <button class="btn btn-secondary btn-sm" @click="$emit('upload')">📁 上传文件</button>
        <button class="btn btn-secondary btn-sm" @click="$emit('clear')" :disabled="!modelValue">清空</button>
      </div>
    </div>
    <textarea
      class="editor-textarea"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      :placeholder="placeholder"
      rows="14"
    ></textarea>
    <div class="editor-hint" v-if="showHint && charCount > 0">
      💡 提示：系统将自动为您的文本进行智能分段，生成自然流畅的语音
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  modelValue: { type: String, default: "" },
  placeholder: { type: String, default: "请在此粘贴或输入您要配音的文本内容..." },
  showHint: { type: Boolean, default: true },
});

defineEmits(["update:modelValue", "upload", "clear"]);

const charCount = computed(() => props.modelValue.length);
const estimatedDuration = computed(() => Math.ceil(props.modelValue.length / 300));
</script>

<style scoped>
.text-editor {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
}

.editor-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: var(--bg);
  border-bottom: 1px solid var(--border-light);
}

.toolbar-info {
  font-size: 13px;
  color: var(--text-muted);
}

.toolbar-info strong {
  color: var(--primary);
}

.toolbar-actions {
  display: flex;
  gap: 8px;
}

.editor-textarea {
  width: 100%;
  border: none;
  outline: none;
  resize: vertical;
  padding: 16px;
  font-size: 15px;
  line-height: 1.8;
  color: var(--text);
  background: transparent;
  min-height: 300px;
}

.editor-textarea::placeholder {
  color: var(--text-muted);
}

.editor-hint {
  padding: 10px 16px;
  font-size: 13px;
  color: var(--text-muted);
  background: #fffbeb;
  border-top: 1px solid #fef3c7;
}
</style>
