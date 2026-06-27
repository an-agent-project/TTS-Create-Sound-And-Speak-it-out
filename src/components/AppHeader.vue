<template>
  <header class="app-header">
    <div class="header-inner">
      <router-link to="/" class="logo"><Mic class="logo-icon" :size="24" /><span class="logo-text">有声读物智能生成系统</span></router-link>
      <nav class="nav-links">
        <router-link to="/workspace" class="nav-link"><Pen :size="16" /> 创作工作台</router-link>
        <router-link to="/extract" class="nav-link"><Wand2 :size="16" /> 音色提取台</router-link>
        <router-link to="/voices/public" class="nav-link"><Library :size="16" /> 公共音色库</router-link>
        <router-link to="/voices" class="nav-link"><Drama :size="16" /> 个人音色库</router-link>
        <router-link to="/workshop" class="nav-link"><FolderOpen :size="16" /> 个人素材库</router-link>
      </nav>
      <div class="header-actions">
        <template v-if="store.isLoggedIn">
          <div class="user-menu" ref="menuRef">
            <button class="user-btn" @click="open = !open">
              <div class="user-avatar-mini">
                <img v-if="store.user.avatar" :src="store.user.avatar" class="avatar-thumb" />
                <span v-else class="avatar-initial">{{ store.user.username ? store.user.username[0] : "?" }}</span>
              </div>
              <span class="user-name">{{ store.user.username }}</span>
              <ChevronDown :size="14" class="chevron" :class="{ open }" />
            </button>
            <div v-if="open" class="dropdown">
              <router-link to="/profile" class="dropdown-item" @click="open = false"><User :size="15" /> 个人中心</router-link>
              <router-link v-if="store.isAdmin" to="/admin" class="dropdown-item admin-item" @click="open = false"><Shield :size="15" /> 管理后台</router-link>
              <button class="dropdown-item logout" @click="handleLogout">退出登录</button>
            </div>
          </div>
        </template>
        <template v-else>
          <router-link to="/login" class="btn btn-login">登录</router-link>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Mic, Pen, Drama, FolderOpen, Wand2, ChevronDown, User, Shield, Library } from 'lucide-vue-next'
import { useAppStore } from "../stores/app.js";

const store = useAppStore();
const router = useRouter();
const open = ref(false);
const menuRef = ref(null);

function handleClickOutside(e) {
  if (menuRef.value && !menuRef.value.contains(e.target)) {
    open.value = false;
  }
}

function handleLogout() {
  open.value = false;
  store.logout();
  router.push("/");
}

onMounted(() => document.addEventListener("click", handleClickOutside));
onUnmounted(() => document.removeEventListener("click", handleClickOutside));
</script>

<style scoped>
.app-header{background:var(--bg-card);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:100;backdrop-filter:blur(12px)}
.header-inner{max-width:1200px;margin:0 auto;padding:0 24px;height:60px;display:flex;align-items:center;gap:32px}
.logo{display:flex;align-items:center;gap:8px;font-weight:700;font-size:17px;color:var(--text);flex-shrink:0;text-decoration:none}
.logo-icon{color:var(--primary);flex-shrink:0}
.nav-links{display:flex;gap:4px;flex:1}
.nav-link{padding:8px 16px;border-radius:var(--radius-sm);font-size:14px;color:var(--text-secondary);font-weight:500;transition:all var(--transition);display:flex;align-items:center;gap:6px;text-decoration:none}
.nav-link:hover,.nav-link.router-link-active{color:var(--primary);background:var(--primary-light)}
.btn-login{background:var(--primary);color:#fff;padding:8px 22px;border-radius:var(--radius-sm);font-size:14px;font-weight:600;transition:all var(--transition);white-space:nowrap;text-decoration:none}
.btn-login:hover{background:var(--primary-hover);transform:translateY(-1px);box-shadow:var(--shadow-md)}
.user-menu{position:relative}
.user-btn{display:flex;align-items:center;gap:8px;padding:4px 14px 4px 4px;border-radius:28px;background:var(--primary-light);color:var(--primary);font-weight:600;font-size:14px;transition:all var(--transition);border:none;cursor:pointer;font-family:inherit}
.user-btn:hover{background:var(--primary);color:#fff}
.user-btn:hover .chevron{color:#fff}
.user-avatar-mini{width:32px;height:32px;border-radius:50%;overflow:hidden;background:var(--primary);color:#fff;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.avatar-thumb{width:100%;height:100%;object-fit:cover}
.avatar-initial{font-size:16px;font-weight:700}
.user-name{max-width:80px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.chevron{color:var(--primary);transition:transform var(--transition)}
.chevron.open{transform:rotate(180deg)}
.dropdown{position:absolute;top:calc(100% + 8px);right:0;background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);box-shadow:var(--shadow-lg);min-width:180px;overflow:hidden;z-index:200}
.dropdown-item{display:flex;align-items:center;gap:8px;padding:10px 18px;font-size:14px;color:var(--text);text-decoration:none;transition:background var(--transition);border:none;background:none;width:100%;text-align:left;cursor:pointer;font-family:inherit}
.dropdown-item:hover{background:var(--primary-light);color:var(--primary)}
.admin-item{color:#c08b30;font-weight:600}
.logout{border-top:1px solid var(--border);color:#e53e3e}
.logout:hover{background:#fff5f5;color:#c53030}
@media(max-width:640px){.logo-text{display:none}.nav-link span{display:none}.user-name{display:none}}
</style>
