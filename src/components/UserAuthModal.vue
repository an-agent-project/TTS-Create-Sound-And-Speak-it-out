<template>
  <div class="auth-overlay" @click.self="$emit('close')">
    <div class="auth-card animate">
      <!-- Avatar & Close -->
      <div class="imgcontainer">
        <span class="close-btn" @click="$emit('close')" title="关闭">&times;</span>
        <img
          src="https://static.runoob.com/images/mix/img_avatar.png"
          alt="Avatar"
          class="avatar"
        />
      </div>

      <!-- Login form -->
      <div v-if="!isRegister" class="container">
        <label><b>账户名称</b></label>
        <input
          type="text"
          v-model="loginForm.username"
          placeholder="请输入账户名称"
          required
        />

        <label><b>密码</b></label>
        <input
          type="password"
          v-model="loginForm.password"
          placeholder="请输入密码"
          required
        />

        <div v-if="errorMsg" class="err-msg">{{ errorMsg }}</div>

        <button class="login-btn" type="button" @click="handleLogin">登 录</button>

        <label class="remember-me">
          <input type="checkbox" v-model="rememberMe" />
          记住我
        </label>
      </div>

      <!-- Register form -->
      <div v-if="isRegister" class="container">
        <label><b>账户名称</b></label>
        <input
          type="text"
          v-model="regForm.username"
          placeholder="请设置账户名称"
          required
        />

        <label><b>密码</b></label>
        <input
          type="password"
          v-model="regForm.password"
          placeholder="请设置密码"
          required
        />

        <label><b>确认密码</b></label>
        <input
          type="password"
          v-model="regForm.confirmPassword"
          placeholder="请确认密码"
          required
        />

        <div v-if="errorMsg" class="err-msg">{{ errorMsg }}</div>

        <button class="login-btn" type="button" @click="handleRegister">注 册</button>
      </div>

      <!-- Footer -->
      <div class="container footer-container">
        <button type="button" class="cancelbtn" @click="$emit('close')">取消</button>
        <span class="footer-links">
          <template v-if="!isRegister">
            <a href="#" @click.prevent="switchToRegister">免费注册</a>
          </template>
          <template v-if="isRegister">
            <a href="#" @click.prevent="switchToLogin">立即登录</a>
          </template>
          <span class="divider">|</span>
          <a href="#" @click.prevent="forgotPassword">忘记密码?</a>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { useAppStore } from '../stores/app'

const emit = defineEmits(['close'])
const store = useAppStore()

const isRegister = ref(false)
const errorMsg = ref('')
const rememberMe = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const regForm = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})

// 切换表单时清除数据
watch(isRegister, () => {
  loginForm.username = ''
  loginForm.password = ''
  regForm.username = ''
  regForm.password = ''
  regForm.confirmPassword = ''
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
  emit('close')
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
  emit('close')
}

// 初始化：填充记住的用户名
const remembered = localStorage.getItem('rememberedUser')
if (remembered) {
  loginForm.username = remembered
  rememberMe.value = true
}
</script>

<style scoped>
.auth-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: auto;
  padding-top: 60px;
  padding-bottom: 20px;
}

.auth-card {
  background: #fefefe;
  border: 1px solid #888;
  border-radius: 12px;
  width: 420px;
  max-width: 90vw;
  position: relative;
  box-shadow: 0 8px 32px rgba(0,0,0,0.15);
}

/* 头像容器 */
.imgcontainer {
  text-align: center;
  margin: 24px 0 12px 0;
  position: relative;
}

.avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #eef2ff;
}

/* 关闭按钮 */
.close-btn {
  position: absolute;
  right: 25px;
  top: 0;
  color: #000;
  font-size: 35px;
  font-weight: bold;
  cursor: pointer;
  line-height: 1;
  transition: color 0.15s;
}

.close-btn:hover,
.close-btn:focus {
  color: #ef4444;
}

/* 表单容器 */
.container {
  padding: 16px 28px;
}

.container label {
  display: block;
  font-weight: 600;
  font-size: 14px;
  color: #333;
  margin-bottom: 4px;
  margin-top: 8px;
}

.container input[type="text"],
.container input[type="password"] {
  width: 100%;
  padding: 12px 16px;
  margin: 8px 0;
  display: inline-block;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 14px;
  color: #333;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.2s;
}

.container input:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

.container input::placeholder {
  color: #bbb;
}

/* 记住我 */
.remember-me {
  display: flex !important;
  align-items: center;
  gap: 6px;
  font-weight: 400 !important;
  font-size: 13px !important;
  color: #555 !important;
  margin-top: 6px !important;
  cursor: pointer;
}

.remember-me input[type="checkbox"] {
  width: auto;
  margin: 0;
  accent-color: #6366f1;
}

/* 错误信息 */
.err-msg {
  background: #fff2f0;
  border: 1px solid #ffccc7;
  color: #cf1322;
  padding: 8px 14px;
  border-radius: 6px;
  font-size: 13px;
  margin-top: 8px;
}

/* 登录/注册按钮 */
.login-btn {
  width: 100%;
  padding: 12px;
  margin: 16px 0 8px;
  background: #6366f1;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  letter-spacing: 6px;
  transition: background 0.2s;
}

.login-btn:hover {
  background: #4f46e5;
  opacity: 0.9;
}

/* 底部区域 */
.footer-container {
  background-color: #f1f1f1;
  border-radius: 0 0 12px 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
  padding: 16px 28px;
}

.cancelbtn {
  width: auto;
  padding: 10px 20px;
  background-color: #ef4444;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.cancelbtn:hover {
  background-color: #dc2626;
}

.footer-links {
  font-size: 13px;
  color: #777;
}

.footer-links a {
  color: #6366f1;
  text-decoration: none;
  font-weight: 500;
}

.footer-links a:hover {
  text-decoration: underline;
}

.divider {
  margin: 0 8px;
  color: #ccc;
}

/* 响应式 */
@media screen and (max-width: 480px) {
  .auth-card {
    width: 95vw;
  }

  .cancelbtn {
    width: 100%;
  }

  .footer-container {
    flex-direction: column;
    text-align: center;
  }

  .container {
    padding: 12px 20px;
  }

  .footer-container {
    padding: 14px 20px;
  }
}

@media screen and (max-width: 300px) {
  .footer-links {
    display: block;
    width: 100%;
  }

  .divider {
    display: none;
  }

  .footer-links a {
    display: block;
    margin-top: 4px;
  }

  .cancelbtn {
    width: 100%;
  }

  .imgcontainer {
    margin: 12px 0 6px 0;
  }

  .avatar {
    width: 70px;
    height: 70px;
  }
}

/* 动画 */
.animate {
  -webkit-animation: animatezoom 0.5s;
  animation: animatezoom 0.35s;
}

@-webkit-keyframes animatezoom {
  from { -webkit-transform: scale(0); }
  to   { -webkit-transform: scale(1); }
}

@keyframes animatezoom {
  from { transform: scale(0); opacity: 0; }
  to   { transform: scale(1); opacity: 1; }
}
</style>
