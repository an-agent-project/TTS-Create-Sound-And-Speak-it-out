<template>
  <div class="auth-overlay" @click.self="('close')">
    <div class="auth-card animate">
      <!-- Avatar & Close -->
      <div class="imgcontainer">
        <span class="close-btn" @click="('close')" title="??">&times;</span>
        <img
          src="https://static.runoob.com/images/mix/img_avatar.png"
          alt="Avatar"
          class="avatar"
        />
      </div>

      <!-- Login form -->
      <div v-if="!isRegister" class="container">
        <label><b>邮箱</b></label>
        <input
          type="email"
          v-model="loginForm.email"
          placeholder="请输入邮箱地址"
          required
        />

        <label><b>密码</b></label>
        <input
          type="password"
          v-model="loginForm.password"
          placeholder="请确认密码"
          required
        />

        <div v-if="errorMsg" class="err-msg">{{ errorMsg }}</div>

        <button class="login-btn" type="button" :disabled="loggingIn" @click="handleLogin">? ?</button>

        <label class="remember-me">
          <input type="checkbox" v-model="rememberMe" />
          ???
        </label>
      </div>

      <!-- Register form -->
      <div v-if="isRegister" class="container">
        <label><b>??</b></label>
        <input
          type="email"
          v-model="regForm.email"
          placeholder="???????"
          required
        />

        <label><b>验证码</b></label>
        <div class="code-row">
          <input
            type="text"
            class="code-input"
            v-model="regForm.code"
            placeholder="6????"
            maxlength="6"
            required
          />
          <button
            type="button"
            class="send-code-btn"
            :disabled="codeCountdown > 0"
            @click="sendVerificationCode"
          >
            {{ codeCountdown > 0 ? codeCountdown + 's' : '?????' }}
          </button>
        </div>

        <label><b>????</b></label>
        <input
          type="text"
          v-model="regForm.username"
          placeholder="请设置密码"
          required
        />

        <label><b>确认密码</b></label>
        <input
          type="password"
          v-model="regForm.password"
          placeholder="?????"
          required
        />

        <label><b>????</b></label>
        <input
          type="password"
          v-model="regForm.confirmPassword"
          placeholder="?????"
          required
        />

        <div v-if="errorMsg" class="err-msg">{{ errorMsg }}</div>
        <div v-if="successMsg" class="success-msg">{{ successMsg }}</div>

        <button class="login-btn" type="button" :disabled="registering" @click="handleRegister">? ?</button>
      </div>

      <!-- Footer -->
      <div class="container footer-container">
        <button type="button" class="cancelbtn" @click="('close')">??</button>
        <span class="footer-links">
          <template v-if="!isRegister">
            <a href="#" @click.prevent="switchToRegister">????</a>
          </template>
          <template v-if="isRegister">
            <a href="#" @click.prevent="switchToLogin">????</a>
          </template>
          <span class="divider">|</span>
          <a href="#" @click.prevent="forgotPassword">?????</a>
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
const successMsg = ref('')
const rememberMe = ref(false)
const loggingIn = ref(false)
const registering = ref(false)
const codeCountdown = ref(0)
let countdownTimer = null

const loginForm = reactive({
  email: '',
  password: ''
})

const regForm = reactive({
  email: '',
  code: '',
  username: '',
  password: '',
  confirmPassword: ''
})

// ?????????
watch(isRegister, () => {
  loginForm.email = ''
  loginForm.password = ''
  regForm.email = ''
  regForm.code = ''
  regForm.username = ''
  regForm.password = ''
  regForm.confirmPassword = ''
  errorMsg.value = ''
  successMsg.value = ''
  codeCountdown.value = 0
  if (countdownTimer) clearInterval(countdownTimer)
})

function switchToRegister() {
  isRegister.value = true
}

function switchToLogin() {
  isRegister.value = false
}

function forgotPassword() {
  alert('??????????')
}

// ---------- ????? ----------

async function sendVerificationCode() {
  errorMsg.value = ''
  successMsg.value = ''

  if (!regForm.email.trim()) {
    errorMsg.value = '????????'
    return
  }

  try {
    const response = await fetch('/api/auth/send-code', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: regForm.email.trim().toLowerCase() }),
    })

    if (!response.ok) {
      const err = await response.json()
      throw new Error(err.detail || '????')
    }

    const data = await response.json()
    successMsg.value = '??????? ' + regForm.email.trim()
    if (data.code) {
      console.log('[DEV] ???:', data.code)
    }

    codeCountdown.value = 60
    countdownTimer = setInterval(() => {
      codeCountdown.value--
      if (codeCountdown.value <= 0) {
        clearInterval(countdownTimer)
      }
    }, 1000)
  } catch (err) {
    errorMsg.value = err.message || '???????'
  }
}

// ---------- ?? ----------

async function handleLogin() {
  errorMsg.value = ''
  if (!loginForm.email.trim() || !loginForm.password.trim()) {
    errorMsg.value = '????????'
    return
  }

  loggingIn.value = true
  try {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: loginForm.email.trim().toLowerCase(),
        password: loginForm.password,
      }),
    })

    if (!response.ok) {
      const err = await response.json()
      throw new Error(err.detail || '????')
    }

    const data = await response.json()
    store.setUser(data.user)

    if (rememberMe.value) {
      localStorage.setItem('rememberedEmail', loginForm.email.trim())
    } else {
      localStorage.removeItem('rememberedEmail')
    }

    emit('close')
  } catch (err) {
    errorMsg.value = err.message
  } finally {
    loggingIn.value = false
  }
}

// ---------- ?? ----------

async function handleRegister() {
  errorMsg.value = ''
  successMsg.value = ''

  if (!regForm.email.trim() || !regForm.code.trim() || !regForm.username.trim() || !regForm.password.trim()) {
    errorMsg.value = '??????????'
    return
  }
  if (regForm.code.length !== 6) {
    errorMsg.value = '???6????'
    return
  }
  if (regForm.password !== regForm.confirmPassword) {
    errorMsg.value = '?????????'
    return
  }
  if (regForm.password.length < 4) {
    errorMsg.value = '????????4?'
    return
  }

  registering.value = true
  try {
    const response = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: regForm.email.trim().toLowerCase(),
        username: regForm.username.trim(),
        password: regForm.password,
        code: regForm.code.trim(),
      }),
    })

    if (!response.ok) {
      const err = await response.json()
      throw new Error(err.detail || '????')
    }

    const data = await response.json()
    store.setUser(data.user)
    emit('close')
  } catch (err) {
    errorMsg.value = err.message
  } finally {
    registering.value = false
  }
}

// ???????????
const remembered = localStorage.getItem('rememberedEmail')
if (remembered) {
  loginForm.email = remembered
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

/* ???? */
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

/* ???? */
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

/* ???? */
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
.container input[type="password"],
.container input[type="email"] {
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

/* ???? */
.code-row {
  display: flex;
  gap: 8px;
  margin: 8px 0;
}

.code-input {
  flex: 1;
  margin: 0 !important;
}

.send-code-btn {
  flex-shrink: 0;
  min-width: 100px;
  padding: 8px 10px;
  background: #6366f1;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.2s;
}

.send-code-btn:hover:not(:disabled) {
  background: #4f46e5;
}

.send-code-btn:disabled {
  background: #a5b4fc;
  cursor: not-allowed;
}

/* ??? */
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

/* ???? */
.err-msg {
  background: #fff2f0;
  border: 1px solid #ffccc7;
  color: #cf1322;
  padding: 8px 14px;
  border-radius: 6px;
  font-size: 13px;
  margin-top: 8px;
}

/* ???? */
.success-msg {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #16a34a;
  padding: 8px 14px;
  border-radius: 6px;
  font-size: 13px;
  margin-top: 8px;
}

/* ??/???? */
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

.login-btn:hover:not(:disabled) {
  background: #4f46e5;
  opacity: 0.9;
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* ???? */
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

/* ??? */
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

/* ?? */
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
