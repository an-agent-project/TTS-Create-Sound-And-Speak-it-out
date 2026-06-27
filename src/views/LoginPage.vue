<template>
  <div class="login-page">
    <div class="login-left">
      <div class="brand-content">
        <div class="brand-logo">
          <Mic :size="42" class="brand-mic" />
          <h1>有声读物智能生成系统</h1>
        </div>
        <p class="brand-desc">AI 驱动的语音合成平台，让文字拥有温度</p>
        <div class="feature-list">
          <div class="feature-item"><Drama :size="22" /><span>多场景角色扮演</span></div>
          <div class="feature-item"><Music :size="22" /><span>BGM 智能搭配</span></div>
          <div class="feature-item"><Zap :size="22" /><span>一键快速生成</span></div>
        </div>
      </div>
      <div class="bg-decoration">
        <div class="circle c1"></div>
        <div class="circle c2"></div>
        <div class="circle c3"></div>
      </div>
    </div>

    <div class="login-right">
      <div class="form-wrapper">
        <div class="form-header">
          <h2>{{ pageTitle }}</h2>
          <p>{{ pageSubtitle }}</p>
        </div>

        <form v-if="!isRegister && !isResetPassword" class="auth-form" @submit.prevent="handleLogin">
          <div class="input-group">
            <label>邮箱或用户名</label>
            <div class="input-box">
              <Mail :size="18" class="input-icon" />
              <input v-model="loginForm.identifier" type="text" placeholder="请输入邮箱或用户名" required />
            </div>
          </div>

          <div class="input-group">
            <label>密码</label>
            <div class="input-box">
              <Lock :size="18" class="input-icon" />
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
          </div>

          <div class="form-options">
            <label class="remember-me">
              <input v-model="rememberMe" type="checkbox" />
              <span>记住账号</span>
            </label>
            <a href="#" @click.prevent="forgotPassword">忘记密码?</a>
          </div>

          <div v-if="errorMsg" class="err-msg">{{ errorMsg }}</div>
          <button type="submit" class="submit-btn" :disabled="loggingIn">
            {{ loggingIn ? "登录中" : "登录" }}
          </button>
        </form>

        <form v-else-if="isRegister" class="auth-form" @submit.prevent="handleRegister">
          <div class="input-group">
            <label>邮箱</label>
            <div class="input-box">
              <Mail :size="18" class="input-icon" />
              <input v-model="regForm.email" type="email" placeholder="请输入邮箱地址" required />
            </div>
          </div>

          <div class="input-group">
            <label>验证码</label>
            <div class="code-row">
              <div class="input-box code-input-box">
                <ShieldCheck :size="18" class="input-icon" />
                <input v-model="regForm.code" type="text" placeholder="请输入6位验证码" maxlength="6" required />
              </div>
              <button type="button" class="send-code-btn" :disabled="codeCountdown > 0" @click="sendVerificationCode">
                {{ codeCountdown > 0 ? codeCountdown + "s" : "发送验证码" }}
              </button>
            </div>
          </div>

          <div class="input-group">
            <label>账号名称</label>
            <div class="input-box">
              <User :size="18" class="input-icon" />
              <input v-model="regForm.username" type="text" placeholder="请设置账号名称" required />
            </div>
          </div>

          <div class="input-group">
            <label>密码</label>
            <div class="input-box">
              <Lock :size="18" class="input-icon" />
              <input
                v-model="regForm.password"
                :type="showPwd ? 'text' : 'password'"
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
                v-model="regForm.confirmPassword"
                :type="showPwd ? 'text' : 'password'"
                placeholder="请再次输入密码"
                required
              />
            </div>
          </div>

          <div v-if="errorMsg" class="err-msg">{{ errorMsg }}</div>
          <div v-if="successMsg" class="success-msg">{{ successMsg }}</div>
          <button type="submit" class="submit-btn" :disabled="registering">
            {{ registering ? "注册中" : "注册" }}
          </button>
        </form>


        <form v-else class="auth-form" @submit.prevent="handleResetPassword">
          <div class="input-group">
            <label>邮箱</label>
            <div class="input-box">
              <Mail :size="18" class="input-icon" />
              <input v-model="resetForm.email" type="email" placeholder="请输入注册邮箱" required />
            </div>
          </div>

          <div class="input-group">
            <label>验证码</label>
            <div class="code-row">
              <div class="input-box code-input-box">
                <ShieldCheck :size="18" class="input-icon" />
                <input v-model="resetForm.code" type="text" placeholder="请输入6位验证码" maxlength="6" required />
              </div>
              <button type="button" class="send-code-btn" :disabled="codeCountdown > 0" @click="sendVerificationCode">
                {{ codeCountdown > 0 ? codeCountdown + "s" : "发送验证码" }}
              </button>
            </div>
          </div>

          <div class="input-group">
            <label>新密码</label>
            <div class="input-box">
              <Lock :size="18" class="input-icon" />
              <input
                v-model="resetForm.newPassword"
                :type="showPwd ? 'text' : 'password'"
                placeholder="请设置新密码（至少4位）"
                required
              />
              <span class="toggle-pwd" @click="showPwd = !showPwd">
                <EyeOff v-if="showPwd" :size="18" />
                <Eye v-else :size="18" />
              </span>
            </div>
          </div>

          <div class="input-group">
            <label>确认新密码</label>
            <div class="input-box">
              <Lock :size="18" class="input-icon" />
              <input
                v-model="resetForm.confirmPassword"
                :type="showPwd ? 'text' : 'password'"
                placeholder="请再次输入新密码"
                required
              />
            </div>
          </div>

          <div v-if="errorMsg" class="err-msg">{{ errorMsg }}</div>
          <div v-if="successMsg" class="success-msg">{{ successMsg }}</div>
          <button type="submit" class="submit-btn" :disabled="resettingPassword">
            {{ resettingPassword ? "重置中" : "重置密码" }}
          </button>
        </form>
        <div class="form-footer">
          <template v-if="isResetPassword">
            想起密码？<a href="#" @click.prevent="switchToLogin">立即登录</a>
          </template>
          <template v-else-if="!isRegister">
            还没有账号？<a href="#" @click.prevent="switchToRegister">立即注册</a>
          </template>
          <template v-else>
            已有账号？<a href="#" @click.prevent="switchToLogin">立即登录</a>
          </template>
        </div>
        <router-link to="/" class="back-home"><ArrowLeft :size="14" />返回首页</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { ArrowLeft, Drama, Eye, EyeOff, Lock, Mail, Mic, Music, ShieldCheck, User, Zap } from "lucide-vue-next";
import { useAppStore } from "../stores/app";
import { resetPassword, sendAuthCode } from "../services/api.js";

const router = useRouter();
const store = useAppStore();

const isRegister = ref(false);
const isResetPassword = ref(false);
const showPwd = ref(false);
const errorMsg = ref("");
const successMsg = ref("");
const rememberMe = ref(false);
const loggingIn = ref(false);
const registering = ref(false);
const resettingPassword = ref(false);
const codeCountdown = ref(0);
let countdownTimer = null;

const loginForm = reactive({ identifier: "", password: "" });
const regForm = reactive({ email: "", code: "", username: "", password: "", confirmPassword: "" });
const resetForm = reactive({ email: "", code: "", newPassword: "", confirmPassword: "" });

const pageTitle = computed(() => {
  if (isResetPassword.value) return "重置密码";
  return isRegister.value ? "创建账号" : "欢迎回来";
});

const pageSubtitle = computed(() => {
  if (isResetPassword.value) return "通过邮箱验证码设置新密码";
  return isRegister.value ? "注册后即可使用全部功能" : "登录账号继续创作";
});

function resetMessagesAndTimer() {
  showPwd.value = false;
  errorMsg.value = "";
  successMsg.value = "";
  codeCountdown.value = 0;
  if (countdownTimer) clearInterval(countdownTimer);
}

watch([isRegister, isResetPassword], () => {
  loginForm.identifier = "";
  loginForm.password = "";
  regForm.email = "";
  regForm.code = "";
  regForm.username = "";
  regForm.password = "";
  regForm.confirmPassword = "";
  resetForm.email = "";
  resetForm.code = "";
  resetForm.newPassword = "";
  resetForm.confirmPassword = "";
  resetMessagesAndTimer();
});

function switchToRegister() {
  isResetPassword.value = false;
  isRegister.value = true;
}

function switchToLogin() {
  isRegister.value = false;
  isResetPassword.value = false;
}

function forgotPassword() {
  isRegister.value = false;
  isResetPassword.value = true;
}

function validateEmail(email) {
  return /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email);
}

async function sendVerificationCode() {
  errorMsg.value = "";
  successMsg.value = "";
  const targetForm = isResetPassword.value ? resetForm : regForm;
  const email = targetForm.email.trim().toLowerCase();
  if (!email) {
    errorMsg.value = "请先输入邮箱地址";
    return;
  }
  if (!validateEmail(email)) {
    errorMsg.value = "邮箱格式不正确";
    return;
  }
  try {
    const data = await sendAuthCode(email);
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
    router.push("/");
  } finally {
    loggingIn.value = false;
  }
}

async function handleResetPassword() {
  errorMsg.value = "";
  successMsg.value = "";
  const email = resetForm.email.trim().toLowerCase();
  const code = resetForm.code.trim();
  if (!email || !code || !resetForm.newPassword.trim()) {
    errorMsg.value = "请填写完整的重置信息";
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
  if (resetForm.newPassword !== resetForm.confirmPassword) {
    errorMsg.value = "两次密码输入不一致";
    return;
  }
  if (resetForm.newPassword.length < 4) {
    errorMsg.value = "密码长度不能少于4位";
    return;
  }
  resettingPassword.value = true;
  try {
    await resetPassword({ email, code, newPassword: resetForm.newPassword });
    successMsg.value = "密码重置成功，请使用新密码登录";
    setTimeout(() => {
      switchToLogin();
      loginForm.identifier = email;
      successMsg.value = "密码重置成功，请登录";
    }, 800);
  } catch (error) {
    errorMsg.value = error.message || "密码重置失败";
  } finally {
    resettingPassword.value = false;
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
    successMsg.value = "注册成功，正在跳转...";
    setTimeout(() => router.push("/"), 800);
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
.login-page{display:flex;min-height:100vh;width:100%}
.login-left{flex:1;background:linear-gradient(135deg,#4f46e5 0%,#7c3aed 50%,#a855f7 100%);display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden;padding:60px 40px}
.brand-content{position:relative;z-index:1;max-width:420px;color:#fff}
.brand-logo{display:flex;align-items:center;gap:12px;margin-bottom:16px}
.brand-mic{flex-shrink:0}
.brand-logo h1{font-size:26px;font-weight:700;line-height:1.3}
.brand-desc{font-size:16px;opacity:.85;margin-bottom:40px;line-height:1.6}
.feature-list{display:flex;flex-direction:column;gap:16px}
.feature-item{display:flex;align-items:center;gap:12px;font-size:15px;opacity:.9}
.bg-decoration .circle{position:absolute;border-radius:50%;background:rgba(255,255,255,.06)}
.c1{width:300px;height:300px;top:-80px;right:-60px}
.c2{width:200px;height:200px;bottom:-40px;left:-40px}
.c3{width:120px;height:120px;top:50%;right:30px;transform:translateY(-50%)}
.login-right{flex:1;display:flex;align-items:center;justify-content:center;background:#f8fafc;padding:40px}
.form-wrapper{width:100%;max-width:400px}
.form-header{text-align:center;margin-bottom:32px}
.form-header h2{font-size:26px;font-weight:700;color:#1e293b;margin-bottom:8px}
.form-header p{font-size:14px;color:#64748b}
.auth-form{background:#fff;border-radius:16px;padding:32px 28px;box-shadow:0 4px 24px rgba(0,0,0,.06)}
.input-group{margin-bottom:18px}
.input-group label{display:block;font-size:13px;font-weight:600;color:#374151;margin-bottom:6px}
.input-box{display:flex;align-items:center;border:1px solid #d1d5db;border-radius:10px;overflow:hidden;transition:border-color .2s,box-shadow .2s;background:#fff}
.input-box:focus-within{border-color:#6366f1;box-shadow:0 0 0 3px rgba(99,102,241,.12)}
.input-icon{margin:0 10px;color:#9ca3af;flex-shrink:0}
.input-box input{flex:1;border:none;outline:none;padding:12px 12px 12px 0;font-size:14px;color:#1e293b;background:transparent;min-width:0}
.input-box input::placeholder{color:#9ca3af}
.toggle-pwd{padding:0 12px;cursor:pointer;color:#9ca3af;user-select:none;flex-shrink:0;display:flex;align-items:center}
.toggle-pwd:hover{color:#6366f1}
.code-row{display:flex;gap:10px}
.code-input-box{flex:1}
.send-code-btn{flex-shrink:0;min-width:110px;padding:10px 14px;background:#6366f1;color:#fff;border:none;border-radius:10px;font-size:13px;font-weight:600;cursor:pointer;white-space:nowrap;transition:background .2s}
.send-code-btn:hover:not(:disabled){background:#4f46e5}
.send-code-btn:disabled{background:#a5b4fc;cursor:not-allowed}
.form-options{display:flex;align-items:center;justify-content:space-between;margin-bottom:18px}
.remember-me{display:flex;align-items:center;gap:6px;font-size:13px;color:#6b7280;cursor:pointer}
.remember-me input[type=checkbox]{accent-color:#6366f1;width:16px;height:16px}
.form-options a{font-size:13px;color:#6366f1;text-decoration:none;font-weight:500}
.form-options a:hover{text-decoration:underline}
.err-msg{background:#fef2f2;border:1px solid #fecaca;color:#dc2626;padding:10px 14px;border-radius:8px;font-size:13px;margin-bottom:16px}
.success-msg{background:#f0fdf4;border:1px solid #bbf7d0;color:#16a34a;padding:10px 14px;border-radius:8px;font-size:13px;margin-bottom:16px}
.submit-btn{width:100%;padding:13px;background:linear-gradient(135deg,#6366f1,#7c3aed);color:#fff;border:none;border-radius:10px;font-size:15px;font-weight:600;cursor:pointer;transition:transform .15s,box-shadow .15s}
.submit-btn:hover:not(:disabled){transform:translateY(-1px);box-shadow:0 4px 14px rgba(99,102,241,.4)}
.submit-btn:active{transform:translateY(0)}
.submit-btn:disabled{opacity:.6;cursor:not-allowed}
.form-footer{text-align:center;margin-top:20px;font-size:14px;color:#64748b}
.form-footer a{color:#6366f1;text-decoration:none;font-weight:600}
.form-footer a:hover{text-decoration:underline}
.back-home{display:flex;align-items:center;justify-content:center;gap:4px;margin-top:16px;font-size:13px;color:#94a3b8;text-decoration:none;transition:color .2s}
.back-home:hover{color:#6366f1}
@media(max-width:768px){.login-left{display:none}.login-right{flex:1;padding:24px 16px}.auth-form{padding:24px 20px}.code-row{flex-direction:column}.send-code-btn{width:100%}}
</style>
