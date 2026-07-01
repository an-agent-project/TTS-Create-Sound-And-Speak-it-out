<template>
  <div class="admin-shell">
    <aside class="sidebar">
      <div class="sidebar-brand-row">
        <router-link to="/" class="sidebar-brand"><Shield :size="20" /> 管理后台</router-link>
        <button class="theme-btn" type="button" :title="isDark ? '切换日间模式' : '切换夜间模式'" @click="toggleTheme">
          <Sun v-if="isDark" :size="16" /><Moon v-else :size="16" />
        </button>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/admin/materials" class="sidebar-link"><FolderOpen :size="16" /> 素材管理</router-link>
        <router-link to="/admin/voices" class="sidebar-link"><Mic :size="16" /> 音色管理</router-link>
        <router-link to="/admin/works" class="sidebar-link"><Headphones :size="16" /> 作品管理</router-link>
        <router-link to="/admin/reports" class="sidebar-link"><Flag :size="16" /> 举报审核</router-link>
        <router-link to="/admin/health" class="sidebar-link"><Activity :size="16" /> 服务状态</router-link>
      </nav>
    </aside>
    <div class="admin-main">
      <header class="admin-topbar">
        <span class="admin-welcome">欢迎，{{ store.user.username }}</span><router-link to="/" class="back-btn"><ArrowLeft :size="16" /> 返回前台</router-link>
      </header>
      <div class="admin-content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import { Shield, FolderOpen, Mic, Headphones, Flag, Activity, Sun, Moon, ArrowLeft } from 'lucide-vue-next'
import { onMounted, ref } from 'vue'
import { useAppStore } from '../../stores/app.js'
const store = useAppStore()
const isDark = ref(false)
function toggleTheme() {
  isDark.value = !isDark.value; document.documentElement.classList.toggle('theme-dark', isDark.value); localStorage.setItem('theme_mode', isDark.value ? 'dark' : 'light')
}
onMounted(() => {
  document.documentElement.classList.toggle('theme-dark', localStorage.getItem('theme_mode') === 'dark')
  isDark.value = document.documentElement.classList.contains('theme-dark')
})
</script>

<style scoped>
.admin-shell{display:flex;min-height:100vh;background:var(--bg)}
.sidebar{width:220px;background:var(--bg-card);border-right:1px solid var(--border);padding:20px 0;flex-shrink:0}
.sidebar-brand-row{display:flex;align-items:center;justify-content:space-between;padding:0 20px 16px;border-bottom:1px solid var(--border);margin-bottom:8px}
.sidebar-brand{display:flex;align-items:center;gap:8px;font-weight:700;font-size:15px;color:#c08b30;text-decoration:none}
.sidebar-link{display:flex;align-items:center;gap:10px;padding:10px 20px;font-size:14px;color:var(--text-secondary);text-decoration:none;transition:all var(--transition);border-left:3px solid transparent}
.sidebar-link:hover{background:var(--primary-light);color:var(--primary)}
.sidebar-link.router-link-active{background:var(--primary-light);color:var(--primary);border-left-color:var(--primary);font-weight:600}
.admin-main{flex:1;display:flex;flex-direction:column;min-width:0}
.admin-topbar{display:flex;align-items:center;padding:0 24px;height:50px;background:var(--bg-card);border-bottom:1px solid var(--border)}
.admin-welcome{font-size:13px;color:var(--text-secondary)}
.back-btn{display:inline-flex;align-items:center;gap:6px;padding:6px 14px;border-radius:var(--radius-sm);font-size:13px;color:var(--text-secondary);text-decoration:none;font-weight:500;border:1px solid var(--border);background:var(--bg);transition:all var(--transition);margin-left:12px}
.back-btn:hover{color:var(--primary);border-color:var(--primary);background:var(--primary-light)}
.theme-btn{width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:var(--primary-light);color:var(--primary);border:1px solid var(--border);cursor:pointer;transition:all var(--transition);flex-shrink:0}.theme-btn:hover{background:var(--primary);color:#fff}
.admin-content{padding:24px;flex:1;overflow-y:auto}
</style>
