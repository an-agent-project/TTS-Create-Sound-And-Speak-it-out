<template>
  <header class="app-header">
    <div class="header-inner">
      <router-link to="/" class="logo">
        <span class="logo-icon">🎧</span>
        <span class="logo-text">有声读物智能生成系统</span>
      </router-link>
      <nav class="nav-links">
        <router-link to="/workspace" class="nav-link">
          <span>✨</span> 创作工作台
        </router-link>
        <router-link to="/voices" class="nav-link">
          <span>🎙️</span> 音色库
        </router-link>
        <router-link to="/my-works" class="nav-link">
          <span>📂</span> 我的作品
        </router-link>
      </nav>
      <div class="header-actions">
        <router-link to="/workspace" class="btn btn-primary btn-sm">
          🚀 开始创作
        </router-link>
      </div>
    </div>
  </header>
</template>

<script setup></script>

<style scoped>
.app-header {
  background: var(--bg-card);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(12px);
}

.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  height: 60px;
  display: flex;
  align-items: center;
  gap: 32px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
  font-size: 17px;
  color: var(--text);
  flex-shrink: 0;
}

.logo-icon {
  font-size: 24px;
}

.nav-links {
  display: flex;
  gap: 4px;
  flex: 1;
}

.nav-link {
  padding: 8px 16px;
  border-radius: var(--radius-sm);
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
  transition: all var(--transition);
  display: flex;
  align-items: center;
  gap: 4px;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: var(--primary);
  background: var(--primary-light);
}

@media (max-width: 640px) {
  .logo-text {
    display: none;
  }
  .header-actions {
    display: none;
  }
  .nav-link span {
    display: none;
  }
}
</style>
