<template>
  <div class="card voice-card" :class="{ featured: voice.isRecommended }">
    <div class="voice-top">
      <div class="voice-avatar" :class="voice.gender">
        <User v-if="voice.gender === 'male'" :size="24" />
        <User v-else-if="voice.gender === 'female'" :size="24" />
        <Baby v-else :size="24" />
      </div>
      <div class="voice-info">
        <h4 class="voice-name">{{ voice.name }}</h4>
        <div class="voice-meta">
          <span class="tag tag-primary">{{ voice.style }}</span>
          <span class="tag tag-success">{{ voice.category }}</span>
        </div>
      </div>
      <button class="fav-btn" :class="{ active: isFavorite }" @click.stop="$emit('toggleFavorite')">
        <Star v-if="isFavorite" :size="20" fill="var(--warning)" color="var(--warning)" />
        <Heart v-else :size="20" />
      </button>
    </div>
    <p class="voice-desc">{{ voice.description }}</p>
    <div class="voice-actions">
      <button v-if="showPreview" class="btn btn-secondary btn-sm btn-block" @click.stop="$emit('preview')">
        <Play :size="14" /> 试听
      </button>
      <button v-if="showSelect" class="btn btn-primary btn-sm btn-block" @click.stop="$emit('select')">
        选择此音色
      </button>
    </div>
  </div>
</template>

<script setup>
import { User, Baby, Star, Heart, Play } from 'lucide-vue-next'

defineProps({
  voice: { type: Object, required: true },
  isFavorite: { type: Boolean, default: false },
  showPreview: { type: Boolean, default: true },
  showSelect: { type: Boolean, default: false },
});
defineEmits(["toggleFavorite", "preview", "select"]);
</script>

<style scoped>
.voice-card {
  position: relative;
  padding: 20px;
}

.voice-card.featured {
  border-color: var(--primary);
  background: linear-gradient(135deg, #fff 0%, #eef2ff 100%);
}

.voice-top {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.voice-avatar {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.voice-avatar.male {
  background: #dbeafe;
  color: #3b82f6;
}
.voice-avatar.female {
  background: #fce7f3;
  color: #ec4899;
}
.voice-avatar.child {
  background: #fef3c7;
  color: #f59e0b;
}

.voice-info {
  flex: 1;
  min-width: 0;
}

.voice-name {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 6px;
}

.voice-meta {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.voice-desc {
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

.voice-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.fav-btn {
  background: none;
  padding: 4px;
  border-radius: 50%;
  flex-shrink: 0;
  transition: transform var(--transition);
  color: var(--text-muted);
}

.fav-btn:hover {
  transform: scale(1.2);
}

.fav-btn.active {
  color: var(--warning);
}
</style>
