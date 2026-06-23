<template>
  <div class="auth-overlay" @click.self="emit('close')">
    <div class="auth-card animate">
      <div class="imgcontainer">
        <span class="close-btn" title="关闭" @click="emit('close')">&times;</span>
        <img src="https://static.runoob.com/images/mix/img_avatar.png" alt="Avatar" class="avatar" />
      </div>

      <div v-if="!isRegister" class="container">
        <label><b>邮箱或用户名</b></label>
        <input v-model="loginForm.identifier" type="text" placeholder="请输入邮箱或用户名" required />

        <label><b>密码</b></label>
        <div class="pwd-wrap">
          <input
            v-model="loginForm.password"
            :type="showPwd ? 'text' : 'password'"
            placeholder="请输入密码"
            required
          />
          <span class="toggle-pwd" @click="showPwd = !showPwd">
            <EyeOff v-if="showPwd" :size="18" />
            <Eye v-else :size="18" />
          </span>
        </div>

        <div v-if="errorMsg" class="err-msg">{{ errorMsg }}</div>

        <button class="login-btn" type="button" :disabled="loggingIn" @click="handleLogin">
          {{ loggingIn ? "登录中" : "登录" }}
        </button>

        <label class="remember-me">
          <input v-model="rememberMe" type="checkbox" />
          记住账号
        </label>
      </div>

      <div v-else class="container">
        <label><b>邮箱</b></label>
        <input v-model="regForm.email" type="email" placeholder="请输入邮箱地址" required />

        <label><b>验证码</b></label>
        <div class="code-row">
          <input v-model="regForm.code" type="text" class="code-input" placeholder="6位验证码" maxlength="6" required />
          <button type="button" class="send-code-btn" :disabled="codeCountdown > 0" @click="sendVerificationCode">
            {{ codeCountdown > 0 ? codeCountdown + "s" : "发送验证码" }}
          </button>
        </div>

        <label><b>账号名称</b></label>
        <input v-model="regForm.username" type="text" placeholder="请设置账号名称" required />

        <label><b>密码</b></label>
        <div class="pwd-wrap">
          <input
            v-model="regForm.password"
            :type="showPwd ? 'text' : 'password'"
            placeholder="请设置密码"
            required
          />
          <span class="toggle-pwd" @click="showPwd = !showPwd">
            <EyeOff v-if="showPwd" :size="18" />
            <Eye v-else :size="18" />
          </span>
        </div>

        <label><b>确认密码</b></label>
        <div class="pwd-wrap">
          <input
            v-model="regForm.confirmPassword"
            :type="showPwd ? 'text' : 'password'"
            placeholder="请再次输入密码"
            required
          />
        </div>

        <div v-if="errorMsg" class="err-msg">{{ errorMsg }}</div>
        <div v-if="successMsg" class="success-msg">{{ successMsg }}</div>

        <button class="login-btn" type="button" :disabled="registering" @click="handleRegister">
          {{ registering ? "注册中" : "注册" }}
        </button>
      </div>

      <div class="container footer-container">
        <button type="button" class="cancelbtn" @click="emit('close')">取消</button>
        <span class="footer-links">
          <template v-if="!isRegister">
            <a href="#" @click.prevent="switchToRegister">注册账号</a>
          </template>
          <template v-else>
            <a href="#" @click.prevent="switchToLogin">返回登录</a>
          </template>
          <span class="divider">|</span>
          <a href="#" @click.prevent="forgotPassword">忘记密码?</a>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, watch } from "vue";
import { Eye, EyeOff } from "lucide-vue-next";
import { useAppStore } from "../stores/app";

const emit = defineEmits(["close"]);
const store = useAppStore();

const isRegister = ref(false);
const errorMsg = ref("");
const successMsg = ref("");
const rememberMe = ref(false);
const showPwd = ref(false);
const loggingIn = ref(false);
const registering = ref(false);
const codeCountdown = ref(0);
let countdownTimer = null;

const loginForm = reactive({ identifier: "", password: "" });
const regForm = reactive({ email: "", code: "", username: "", password: "", confirmPassword: "" });

watch(isRegister, () => {
  loginForm.identifier = "";
  loginForm.password = "";
  regForm.email = "";
  regForm.code = "";
  regForm.username = "";
  regForm.password = "";
  regForm.confirmPassword = "";
  showPwd.value = false;
  errorMsg.value = "";
  successMsg.value = "";
  codeCountdown.value = 0;
  if (countdownTimer) clearInterval(countdownTimer);
});

function switchToRegister() {
  isRegister.value = true;
}

function switchToLogin() {
  isRegister.value = false;
}

function forgotPassword() {
  alert("请联系管理员重置密码");
}

function validateEmail(email) {
  return /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email);
}

async function sendVerificationCode() {
  errorMsg.value = "";
  successMsg.value = "";
  const email = regForm.email.trim().toLowerCase();
  if (!email) {
    errorMsg.value = "请先输入邮箱地址";
    return;
  }
  if (!validateEmail(email)) {
    errorMsg.value = "邮箱格式不正确";
    return;
  }

  try {
    const response = await fetch("/api/auth/send-code", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "发送失败");
    successMsg.value = data.code
      ? `验证码已发送至 ${email}，开发验证码：${data.code}`
      : `验证码已发送至 ${email}`;
    if (data.code) console.log("[DEV] verification code:", data.code);
    codeCountdown.value = 60;
    countdownTimer = setInterval(() => {
      codeCountdown.value -= 1;
      if (codeCountdown.value <= 0) clearInterval(countdownTimer);
    }, 1000);
  } catch (err) {
    errorMsg.value = err.message || "发送失败";
  }
}

async function handleLogin() {
  errorMsg.value = "";
  const identifier = loginForm.identifier.trim();
  if (!identifier || !loginForm.password.trim()) {
    errorMsg.value = "请输入账号和密码";
    return;
  }

  loggingIn.value = true;
  try {
    const result = await store.login(identifier, loginForm.password);
    if (!result.success) {
      errorMsg.value = result.message;
      return;
    }
    if (rememberMe.value) {
      localStorage.setItem("rememberedAccount", identifier);
    } else {
      localStorage.removeItem("rememberedAccount");
    }
    emit("close");
  } finally {
    loggingIn.value = false;
  }
}

async function handleRegister() {
  errorMsg.value = "";
  successMsg.value = "";
  const email = regForm.email.trim().toLowerCase();
  const username = regForm.username.trim();
  const code = regForm.code.trim();

  if (!email || !code || !username || !regForm.password.trim()) {
    errorMsg.value = "请填写完整的注册信息";
    return;
  }
  if (!validateEmail(email)) {
    errorMsg.value = "邮箱格式不正确";
    return;
  }
  if (code.length !== 6) {
    errorMsg.value = "请输入6位验证码";
    return;
  }
  if (regForm.password !== regForm.confirmPassword) {
    errorMsg.value = "两次密码输入不一致";
    return;
  }
  if (regForm.password.length < 4) {
    errorMsg.value = "密码长度不能少于4位";
    return;
  }

  registering.value = true;
  try {
    const result = await store.register(username, regForm.password, email, code);
    if (!result.success) {
      errorMsg.value = result.message;
      return;
    }
    emit("close");
  } finally {
    registering.value = false;
  }
}

const remembered = localStorage.getItem("rememberedAccount") || localStorage.getItem("rememberedEmail");
if (remembered) {
  loginForm.identifier = remembered;
  rememberMe.value = true;
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

.pwd-wrap {
  position: relative;
}

.pwd-wrap input {
  padding-right: 40px;
}

.pwd-wrap .toggle-pwd {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  color: #9ca3af;
  display: flex;
  align-items: center;
  user-select: none;
}

.pwd-wrap .toggle-pwd:hover {
  color: #6366f1;
}

.container input::placeholder {
  color: #bbb;
}

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

.err-msg {
  background: #fff2f0;
  border: 1px solid #ffccc7;
  color: #cf1322;
  padding: 8px 14px;
  border-radius: 6px;
  font-size: 13px;
  margin-top: 8px;
}

.success-msg {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #16a34a;
  padding: 8px 14px;
  border-radius: 6px;
  font-size: 13px;
  margin-top: 8px;
}

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
    padding: 14px 20px;
  }

  .container {
    padding: 12px 20px;
  }
}

.animate {
  animation: animatezoom 0.35s;
}

@keyframes animatezoom {
  from { transform: scale(0); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}
</style>
