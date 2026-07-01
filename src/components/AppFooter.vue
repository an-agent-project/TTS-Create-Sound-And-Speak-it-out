<template>
  <footer class="app-footer" :class="{ 'home-footer': isHome }">
    <div class="footer-inner">
      <p>© 2026 AI Voice Studio · 面向内容创作者的个性化AI配音工具</p>
    </div>
  </footer>
</template>

<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();
const isHome = computed(() => route.path === "/");
</script>

<style scoped>
.app-footer {
  border-top: 1px solid var(--border);
  background: var(--bg-card);
  margin-top: 60px;
}

.app-footer.home-footer {
  margin-top: 0;
  border-top: 1px solid rgba(126, 211, 148, 0.16);
  background: #07120f;
}

.footer-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 24px;
  text-align: center;
  font-size: 13px;
  color: var(--text-muted);
}

.home-footer .footer-inner {
  color: rgba(247, 251, 247, 0.48);
}
</style>
