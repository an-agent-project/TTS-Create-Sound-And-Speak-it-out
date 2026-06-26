<template>
  <header class="app-header">
    <div class="header-inner">
      <router-link to="/" class="logo"><Mic class="logo-icon" :size="24" /><span class="logo-text">有声读物智能生成系统</span></router-link>
      <nav class="nav-links">
        <router-link to="/workspace" class="nav-link"><Pen :size="16" /> 创作工作台</router-link>
        <router-link to="/extract" class="nav-link"><Wand2 :size="16" /> 音色提取台</router-link>
        <router-link to="/voices" class="nav-link"><Drama :size="16" /> 个人音色库</router-link>
        <router-link to="/workshop" class="nav-link"><FolderOpen :size="16" /> 个人素材库</router-link>
      </nav>
      <div class="header-actions">
        <template v-if="store.isLoggedIn">
          <router-link to="/profile" class="user-btn">
            <div class="user-avatar-mini">
              <img v-if="store.user.avatar" :src="store.user.avatar" class="avatar-thumb" />
              <span v-else class="avatar-initial">{{ store.user.username ? store.user.username[0] : "?" }}</span>
            </div>
            <span class="user-name">{{ store.user.username }}</span>
          </router-link>
        </template>
        <template v-else>
          <router-link to="/login" class="btn btn-login">登录</router-link>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup>
import { Mic, Pen, Drama, FolderOpen, Wand2 } from 'lucide-vue-next'
import { useAppStore } from "../stores/app.js";
const store = useAppStore();
</script>

<style scoped>
.app-header{background:var(--bg-card);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:100;backdrop-filter:blur(12px)}
.header-inner{max-width:1200px;margin:0 auto;padding:0 24px;height:60px;display:flex;align-items:center;gap:32px}
.logo{display:flex;align-items:center;gap:8px;font-weight:700;font-size:17px;color:var(--text);flex-shrink:0;text-decoration:none}
.logo-icon{color:var(--primary);flex-shrink:0}
.nav-links{display:flex;gap:4px;flex:1}
.nav-link{padding:8px 16px;border-radius:var(--radius-sm);font-size:14px;color:var(--text-secondary);font-weight:500;transition:all var(--transition);display:flex;align-items:center;gap:6px}
.nav-link:hover,.nav-link.router-link-active{color:var(--primary);background:var(--primary-light)}
.btn-login{background:var(--primary);color:#fff;padding:8px 22px;border-radius:var(--radius-sm);font-size:14px;font-weight:600;transition:all var(--transition);white-space:nowrap;text-decoration:none}
.btn-login:hover{background:var(--primary-hover);transform:translateY(-1px);box-shadow:var(--shadow-md)}
.user-btn{display:flex;align-items:center;gap:8px;padding:4px 14px 4px 4px;border-radius:28px;background:var(--primary-light);color:var(--primary);font-weight:600;font-size:14px;transition:all var(--transition);text-decoration:none}
.user-btn:hover{background:var(--primary);color:#fff}
.user-avatar-mini{width:32px;height:32px;border-radius:50%;overflow:hidden;background:var(--primary);color:#fff;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.avatar-thumb{width:100%;height:100%;object-fit:cover}
.avatar-initial{font-size:16px;font-weight:700}
.user-name{max-width:80px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
@media(max-width:640px){.logo-text{display:none}.nav-link span{display:none}.user-name{display:none}}
</style>
