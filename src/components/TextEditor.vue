<template>
  <div class="text-editor">
    <div class="editor-toolbar">
      <span class="toolbar-info">
        字数：<strong>{{ charCount }}</strong>
        <span v-if="showLang" style="margin-left:12px;">
          输出语言：
          <select :value="outputLang" class="lang-select" @input="emit('update:outputLang', $event.target.value)">
            <option value="zh">中文</option>
            <option value="en">English</option>
            <option value="ja">日本語</option>
            <option value="ko">한국어</option>
            <option value="fr">Français</option>
            <option value="de">Deutsch</option>
          </select>
        </span>
        {{ charCount > 500 ? '| 预计时长：约' + estimatedDuration + ' 分钟' : '' }}
      </span>
      <div class="toolbar-actions">
        <button class="btn btn-secondary btn-sm" @click="triggerFileInput">
          <FileUp :size="14" /> 本地文件
        </button>
        <input
          ref="fileInput"
          type="file"
          accept=".txt,.md,.html,.json,.csv"
          style="display:none"
          @change="handleFileUpload"
        />
        <button class="btn btn-secondary btn-sm" type="button" @click="clearText" :disabled="!modelValue">清空</button>
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
      <Lightbulb :size="14" /> 提示：系统将自动为您的文本进行智能分段，生成自然流畅的语音
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { FileUp, Lightbulb } from 'lucide-vue-next'

const props = defineProps({
  modelValue: { type: String, default: "" },
  showLang: { type: Boolean, default: false },
  outputLang: { type: String, default: "zh" },
  placeholder: { type: String, default: "请在此粘贴或输入您要配音的文本内容..." },
  showHint: { type: Boolean, default: true },
});

const emit = defineEmits(["update:modelValue", "upload", "clear"]);

const fileInput = ref(null);

const charCount = computed(() => props.modelValue.length);
const estimatedDuration = computed(() => Math.ceil(props.modelValue.length / 300));

function triggerFileInput() {
  fileInput.value?.click();
}

function clearText() {
  emit("update:modelValue", "");
  emit("clear");
}

function handleFileUpload(e) {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (ev) => {
    emit("update:modelValue", ev.target.result);
  };
  reader.onerror = () => {
    alert("文件读取失败，请重试。");
  };
  reader.readAsText(file, "UTF-8");
  e.target.value = "";
}
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

.lang-select { padding: 2px 6px; border: 1px solid var(--border); border-radius: 4px; font-size: 12px; background: var(--bg-card); color: var(--text); cursor: pointer; outline: none; }
.lang-select:focus { border-color: var(--primary); }
.editor-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  font-size: 13px;
  color: var(--text-muted);
  background: #fffbeb;
  border-top: 1px solid #fef3c7;
}
</style>
