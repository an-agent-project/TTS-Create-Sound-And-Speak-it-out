<template>
  <div class="login-page">
    <!-- 左侧品牌区 -->
    <div class="login-left">
      <div class="brand-content">
        <div class="brand-logo">
          <Mic :size="42" class="brand-mic" />
          <h1>有声读物智能生成系统</h1>
        </div>
        <p class="brand-desc">AI 驱动的语音合成平台，让文字拥有温度</p>
        <div class="feature-list">
          <div class="feature-item">
            <Drama :size="22" />
            <span>多场景角色扮演</span>
          </div>
          <div class="feature-item">
            <Music :size="22" />
            <span>BGM 智能搭配</span>
          </div>
          <div class="feature-item">
            <Zap :size="22" />
            <span>一键快速生成</span>
          </div>
        </div>
      </div>
      <div class="bg-decoration">
        <div class="circle c1"></div>
        <div class="circle c2"></div>
        <div class="circle c3"></div>
      </div>
    </div>

    <!-- 右侧表单区 -->
    <div class="login-right">
      <div class="form-wrapper">
        <div class="form-header">
          <h2>{{ isRegister ? '创建账号' : '欢迎回来' }}</h2>
          <p>{{ isRegister ? '注册新账号以使用全部功能' : '登录您的账号以继续' }}</p>
        </div>

        <!-- 登录表单 -->
        <form v-if="!isRegister" @submit.prevent="handleLogin" class="auth-form">
          <div class="input-group">
            <label>账户名称</label>
            <div class="input-box">
              <User :size="18" class="input-icon" />
              <input
                type="text"
                v-model="loginForm.username"
                placeholder="请输入账户名称"
                required
              />
            </div>
          </div>

          <div class="input-group">
            <label>密码</label>
            <div class="input-box">
              <Lock :size="18" class="input-icon" />
              <input
                :type="showPwd ? 'text' : 'password'"
                v-model="loginForm.password"
                placeholder="请输入密码"
                required
              />
              <span class="toggle-pwd" @click="showPwd = !showPwd">
                <EyeOff v-if="showPwd" :size="18" />
                <Eye v-else :size="18" />
              </span>
            </div>
          </div>

          <div class="form-options">
            <label class="remember-me">
              <input type="checkbox" v-model="rememberMe" />
              <span>记住我</span>
            </label>
            <a href="#" @click.prevent="forgotPassword">忘记密码?</a>
          </div>

          <div v-if="errorMsg" class="err-msg">{{ errorMsg }}</div>

          <button type="submit" class="submit-btn">登 录</button>
        </form>

        <!-- 注册表单 -->
        <form v-if="isRegister" @submit.prevent="handleRegister" class="auth-form">
          <div class="input-group">
            <label>账户名称</label>
            <div class="input-box">
              <User :size="18" class="input-icon" />
              <input
                type="text"
                v-model="regForm.username"
                placeholder="请设置账户名称"
                required
              />
            </div>
          </div>

          <div class="input-group">
            <label>密码</label>
            <div class="input-box">
              <Lock :size="18" class="input-icon" />
              <input
                :type="showPwd ? 'text' : 'password'"
                v-model="regForm.password"
                placeholder="请设置密码（至少4位）"
                required
              />
              <span class="toggle-pwd" @click="showPwd = !showPwd">
                <EyeOff v-if="showPwd" :size="18" />
                <Eye v-else :size="18" />
              </span>
            </div>
          </div>

          <div class="input-group">
            <label>确认密码</label>
            <div class="input-box">
              <Lock :size="18" class="input-icon" />
              <input
                type="password"
                v-model="regForm.confirmPassword"
                placeholder="请再次输入密码"
                required
              />
            </div>
          </div>

          <div v-if="errorMsg" class="err-msg">{{ errorMsg }}</div>

          <button type="submit" class="submit-btn">注 册</button>
        </form>

        <div class="form-footer">
          <template v-if="!isRegister">
            还没有账号？
            <a href="#" @click.prevent="switchToRegister">立即注册</a>
          </template>
          <template v-if="isRegister">
            已有账号？
            <a href="#" @click.prevent="switchToLogin">立即登录</a>
          </template>
        </div>

        <router-link to="/" class="back-home">
          <ArrowLeft :size="14" /> 返回首页
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/app'
import { Mic, Drama, Music, Zap, User, Lock, Eye, EyeOff, ArrowLeft } from 'lucide-vue-next'

const router = useRouter()
const store = useAppStore()

const isRegister = ref(false)
const errorMsg = ref('')
const rememberMe = ref(false)
const showPwd = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const regForm = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})

watch(isRegister, () => {
  loginForm.username = ''
  loginForm.password = ''
  regForm.username = ''
  regForm.password = ''
  regForm.confirmPassword = ''
  showPwd.value = false
  errorMsg.value = ''
})

function switchToRegister() {
  isRegister.value = true
}

function switchToLogin() {
  isRegister.value = false
}

function forgotPassword() {
  alert('请联系管理员重置密码')
}

function handleLogin() {
  errorMsg.value = ''
  if (!loginForm.username.trim() || !loginForm.password.trim()) {
    errorMsg.value = '请输入账户名称和密码'
    return
  }
  const result = store.login(loginForm.username.trim(), loginForm.password.trim())
  if (!result.success) {
    errorMsg.value = result.message
    return
  }
  if (rememberMe.value) {
    localStorage.setItem('rememberedUser', loginForm.username.trim())
  } else {
    localStorage.removeItem('rememberedUser')
  }
  router.push('/')
}

function handleRegister() {
  errorMsg.value = ''
  if (!regForm.username.trim() || !regForm.password.trim()) {
    errorMsg.value = '请填写完整的注册信息'
    return
  }
  if (regForm.password !== regForm.confirmPassword) {
    errorMsg.value = '两次密码输入不一致'
    return
  }
  if (regForm.password.length < 4) {
    errorMsg.value = '密码长度不能少于4位'
    return
  }
  const result = store.register(regForm.username.trim(), regForm.password.trim())
  if (!result.success) {
    errorMsg.value = result.message
    return
  }
  router.push('/')
}

const remembered = localStorage.getItem('rememberedUser')
if (remembered) {
  loginForm.username = remembered
  rememberMe.value = true
}
</script>

<style scoped>
.login-page {
  display: flex;
  min-height: 100vh;
  width: 100%;
}

.login-left {
  flex: 1;
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #a855f7 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  padding: 60px 40px;
}

.brand-content {
  position: relative;
  z-index: 1;
  max-width: 420px;
  color: #fff;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.brand-mic {
  flex-shrink: 0;
}

.brand-logo h1 {
  font-size: 26px;
  font-weight: 700;
  line-height: 1.3;
}

.brand-desc {
  font-size: 16px;
  opacity: 0.85;
  margin-bottom: 40px;
  line-height: 1.6;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 15px;
  opacity: 0.9;
}

.bg-decoration .circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.06);
}

.c1 {
  width: 300px;
  height: 300px;
  top: -80px;
  right: -60px;
}

.c2 {
  width: 200px;
  height: 200px;
  bottom: -40px;
  left: -40px;
}

.c3 {
  width: 120px;
  height: 120px;
  top: 50%;
  right: 30px;
  transform: translateY(-50%);
}

.login-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  padding: 40px;
}

.form-wrapper {
  width: 100%;
  max-width: 400px;
}

.form-header {
  text-align: center;
  margin-bottom: 32px;
}

.form-header h2 {
  font-size: 26px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.form-header p {
  font-size: 14px;
  color: #64748b;
}

.auth-form {
  background: #fff;
  border-radius: 16px;
  padding: 32px 28px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
}

.input-group {
  margin-bottom: 18px;
}

.input-group label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 6px;
}

.input-box {
  display: flex;
  align-items: center;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  overflow: hidden;
  transition: border-color 0.2s, box-shadow 0.2s;
  background: #fff;
}

.input-box:focus-within {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12);
}

.input-icon {
  margin: 0 10px;
  color: #9ca3af;
  flex-shrink: 0;
}

.input-box input {
  flex: 1;
  border: none;
  outline: none;
  padding: 12px 12px 12px 0;
  font-size: 14px;
  color: #1e293b;
  background: transparent;
}

.input-box input::placeholder {
  color: #9ca3af;
}

.toggle-pwd {
  padding: 0 12px;
  cursor: pointer;
  color: #9ca3af;
  user-select: none;
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.toggle-pwd:hover {
  color: #6366f1;
}

.form-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #6b7280;
  cursor: pointer;
}

.remember-me input[type="checkbox"] {
  accent-color: #6366f1;
  width: 16px;
  height: 16px;
}

.form-options a {
  font-size: 13px;
  color: #6366f1;
  text-decoration: none;
  font-weight: 500;
}

.form-options a:hover {
  text-decoration: underline;
}

.err-msg {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 13px;
  margin-bottom: 16px;
}

.submit-btn {
  width: 100%;
  padding: 13px;
  background: linear-gradient(135deg, #6366f1, #7c3aed);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  letter-spacing: 6px;
  transition: transform 0.15s, box-shadow 0.15s;
}

.submit-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
}

.submit-btn:active {
  transform: translateY(0);
}

.form-footer {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: #64748b;
}

.form-footer a {
  color: #6366f1;
  text-decoration: none;
  font-weight: 600;
}

.form-footer a:hover {
  text-decoration: underline;
}

.back-home {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  margin-top: 16px;
  font-size: 13px;
  color: #94a3b8;
  text-decoration: none;
  transition: color 0.2s;
}

.back-home:hover {
  color: #6366f1;
}

@media (max-width: 768px) {
  .login-left {
    display: none;
  }

  .login-right {
    flex: 1;
    padding: 24px 16px;
  }

  .auth-form {
    padding: 24px 20px;
  }
}
</style>
