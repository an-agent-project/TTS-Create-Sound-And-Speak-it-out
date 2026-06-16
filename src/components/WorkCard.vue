<template>
  <div class="card work-card">
    <div class="work-top">
      <div class="work-icon">{{ work.icon || '🎧' }}</div>
      <div class="work-info">
        <h4 class="work-title">{{ work.title }}</h4>
        <div class="work-meta">
          <span class="work-date">{{ formatDate(work.createdAt) }}</span>
          <span class="tag tag-primary">{{ work.sceneName || '通用' }}</span>
          <span class="tag tag-success">{{ work.voiceName || '默认音色' }}</span>
        </div>
      </div>
    </div>
    <p class="work-excerpt">{{ excerpt }}</p>
    <div class="work-bottom">
      <span class="work-duration">⏱ {{ work.duration || 0 }} 秒</span>
      <div class="work-actions">
        <button class="btn btn-secondary btn-sm" @click="$emit('preview')">▶ 试听</button>
        <button class="btn btn-primary btn-sm" @click="$emit('edit')">编辑</button>
        <button class="btn btn-danger btn-sm" @click="$emit('delete')">🗑</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  work: { type: Object, required: true },
});

defineEmits(["preview", "edit", "delete"]);

const excerpt = computed(() => {
  const content = props.work.content || "";
  return content.length > 100 ? content.slice(0, 100) + "..." : content;
});

function formatDate(dateStr) {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}
</script>

<style scoped>
.work-card {
  padding: 20px;
}

.work-top {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.work-icon {
  font-size: 32px;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg);
  border-radius: 12px;
  flex-shrink: 0;
}

.work-info {
  flex: 1;
  min-width: 0;
}

.work-title {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.work-meta {
  display: flex;
  gap: 6px;
  align-items: center;
  flex-wrap: wrap;
}

.work-date {
  font-size: 12px;
  color: var(--text-muted);
}

.work-excerpt {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.work-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.work-duration {
  font-size: 12px;
  color: var(--text-muted);
}

.work-actions {
  display: flex;
  gap: 6px;
}
</style>
