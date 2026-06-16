<template>
  <div class="card scene-card" :style="{ borderColor: scene.color + '40' }" @click="$emit('select')">
    <div class="scene-icon" :style="{ background: scene.color + '15', color: scene.color }">
      {{ scene.icon }}
    </div>
    <h3 class="scene-name">{{ scene.name }}</h3>
    <p class="scene-desc">{{ scene.description }}</p>
    <div class="scene-meta">
      <span class="tag tag-primary">语速 {{ scene.defaultSpeed }}x</span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  scene: { type: Object, required: true },
});
defineEmits(["select"]);
</script>

<style scoped>
.scene-card {
  cursor: pointer;
  text-align: center;
  padding: 28px 20px;
}

.scene-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.scene-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  margin: 0 auto 14px;
}

.scene-name {
  font-size: 17px;
  font-weight: 700;
  margin-bottom: 6px;
}

.scene-desc {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 14px;
}

.scene-meta {
  display: flex;
  justify-content: center;
}
</style>
