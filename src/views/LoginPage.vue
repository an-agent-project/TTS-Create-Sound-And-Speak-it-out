<template>
  <div class="login-page" >
        <div class="ripple-bg">
      <svg class="water-surface" viewBox="0 0 1440 900" preserveAspectRatio="none">
        <defs>
          <radialGradient id="wg1" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#15803d" stop-opacity="0.2"/><stop offset="100%" stop-color="#15803d" stop-opacity="0"/></radialGradient>
          <radialGradient id="wg2" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#14532d" stop-opacity="0.14"/><stop offset="100%" stop-color="#14532d" stop-opacity="0"/></radialGradient>
          <radialGradient id="wg3" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#22c55e" stop-opacity="0.12"/><stop offset="100%" stop-color="#22c55e" stop-opacity="0"/></radialGradient>
        </defs>
        <circle cx="80" cy="150" r="50" fill="url(#wg1)" class="drop d1"/><circle cx="80" cy="150" r="100" fill="url(#wg1)" class="drop d1b"/>
        <circle cx="350" cy="280" r="45" fill="url(#wg2)" class="drop d2"/><circle cx="350" cy="280" r="95" fill="url(#wg2)" class="drop d2b"/>
        <circle cx="780" cy="160" r="55" fill="url(#wg1)" class="drop d3"/><circle cx="780" cy="160" r="115" fill="url(#wg1)" class="drop d3b"/>
        <circle cx="1200" cy="400" r="40" fill="url(#wg3)" class="drop d4"/><circle cx="1200" cy="400" r="90" fill="url(#wg3)" class="drop d4b"/>
        <circle cx="620" cy="580" r="48" fill="url(#wg1)" class="drop d5"/><circle cx="620" cy="580" r="105" fill="url(#wg1)" class="drop d5b"/>
        <circle cx="200" cy="650" r="42" fill="url(#wg2)" class="drop d6"/><circle cx="200" cy="650" r="92" fill="url(#wg2)" class="drop d6b"/>
        <circle cx="1050" cy="650" r="50" fill="url(#wg3)" class="drop d7"/><circle cx="1050" cy="650" r="108" fill="url(#wg3)" class="drop d7b"/>
        <circle cx="500" cy="100" r="35" fill="url(#wg2)" class="drop d8"/><circle cx="500" cy="100" r="80" fill="url(#wg2)" class="drop d8b"/>
        <circle cx="1350" cy="180" r="38" fill="url(#wg1)" class="drop d9"/><circle cx="1350" cy="180" r="85" fill="url(#wg1)" class="drop d9b"/>
        <circle cx="150" cy="400" r="44" fill="url(#wg3)" class="drop d10"/><circle cx="150" cy="400" r="95" fill="url(#wg3)" class="drop d10b"/>
        <circle cx="900" cy="750" r="46" fill="url(#wg1)" class="drop d11"/><circle cx="900" cy="750" r="100" fill="url(#wg1)" class="drop d11b"/>
        <circle cx="400" cy="750" r="36" fill="url(#wg2)" class="drop d12"/><circle cx="400" cy="750" r="82" fill="url(#wg2)" class="drop d12b"/>
      </svg>
      <div class="ripple r1"></div><div class="ripple r2"></div><div class="ripple r3"></div><div class="ripple r4"></div>
      <div class="ripple r5"></div><div class="ripple r6"></div><div class="ripple r7"></div><div class="ripple r8"></div>
      <div class="ripple r9"></div><div class="ripple r10"></div><div class="ripple r11"></div><div class="ripple r12"></div>
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
        <audio ref="bgMusic" loop preload="auto" src="/bgm.mp3"></audio>
        <router-link to="/" class="back-home"><ArrowLeft :size="14" />返回首页</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { ArrowLeft, Drama, Eye, EyeOff, Lock, Mail, Mic, Music, ShieldCheck, User, Volume2, VolumeX, Zap } from "lucide-vue-next";
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
    errorMsg.value = "请填写完整的重置密码信息";
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
  } catch (err) {
    errorMsg.value = err.message || "重置密码失败";
  } finally {
    resettingPassword.value = false;
  }
}
async function handleRegister() {
  errorMsg.value = "";
  successMsg.value = "";
  const email = (isResetPassword.value ? resetForm.email : regForm.email).trim().toLowerCase();
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



/* ?? ???? ?? */
const bgMusic = ref(null);
function tryPlay() {
  const audio = bgMusic.value;
  if (!audio || !audio.paused) return;
  audio.volume = 0.35;
  audio.play().catch(() => {});
}
// ?????????????
function autoPlayOnInteraction() {
  tryPlay();
  document.removeEventListener("click", autoPlayOnInteraction);
  document.removeEventListener("keydown", autoPlayOnInteraction);
  document.removeEventListener("touchstart", autoPlayOnInteraction);
}
onMounted(() => {
  tryPlay(); // ???????
  document.addEventListener("click", autoPlayOnInteraction);
  document.addEventListener("keydown", autoPlayOnInteraction);
  document.addEventListener("touchstart", autoPlayOnInteraction);
});

/* ?? ???? ?? */
let rippleId = 0;

const remembered = localStorage.getItem("rememberedAccount") || localStorage.getItem("rememberedEmail");
if (remembered) {
  loginForm.identifier = remembered;
  rememberMe.value = true;
}
</script>

<style scoped>
.login-page{display:flex;min-height:100vh;width:100%;align-items:center;justify-content:center;background:var(--bg)}
.ripple-bg{position:fixed;inset:0;overflow:hidden;pointer-events:none;z-index:0}
.water-surface{position:absolute;inset:0;width:100%;height:100%;opacity:1}
.drop{transform-origin:center;animation:dropRipple 5s ease-out infinite}
.d1{animation-delay:0s}.d1b{animation-delay:.12s}.d2{animation-delay:.7s}.d2b{animation-delay:.82s}
.d3{animation-delay:1.4s}.d3b{animation-delay:1.52s}.d4{animation-delay:2.1s}.d4b{animation-delay:2.22s}
.d5{animation-delay:2.8s}.d5b{animation-delay:2.92s}.d6{animation-delay:3.5s}.d6b{animation-delay:3.62s}
.d7{animation-delay:4.2s}.d7b{animation-delay:4.32s}.d8{animation-delay:.35s}.d8b{animation-delay:.47s}
.d9{animation-delay:1.05s}.d9b{animation-delay:1.17s}.d10{animation-delay:1.75s}.d10b{animation-delay:1.87s}
.d11{animation-delay:2.45s}.d11b{animation-delay:2.57s}.d12{animation-delay:3.15s}.d12b{animation-delay:3.27s}
@keyframes dropRipple{0%{r:16;opacity:1}40%{r:50;opacity:.55}100%{r:150;opacity:0}}
.ripple{position:absolute;border-radius:50%;border:1px solid #15803d;opacity:0;animation:rippleOut 6s ease-out infinite}
.r1{width:60px;height:60px;top:10%;left:5%;animation-delay:0s}
.r2{width:80px;height:80px;top:50%;left:70%;animation-delay:.75s}
.r3{width:50px;height:50px;top:20%;left:55%;animation-delay:1.5s}
.r4{width:70px;height:70px;top:65%;left:15%;animation-delay:2.25s}
.r5{width:90px;height:90px;top:35%;left:40%;animation-delay:3s}
.r6{width:55px;height:55px;top:75%;left:55%;animation-delay:3.75s}
.r7{width:65px;height:65px;top:28%;left:80%;animation-delay:4.5s}
.r8{width:75px;height:75px;top:45%;left:25%;animation-delay:5.25s}
.r9{width:45px;height:45px;top:85%;left:10%;animation-delay:.5s}
.r10{width:85px;height:85px;top:15%;left:65%;animation-delay:1.25s}
.r11{width:55px;height:55px;top:55%;left:90%;animation-delay:2s}
.r12{width:70px;height:70px;top:80%;left:40%;animation-delay:2.75s}
@keyframes rippleOut{0%{transform:scale(.2);opacity:.3}35%{opacity:.12}100%{transform:scale(4);opacity:0}}
.login-right{width:100%;max-width:440px;padding:40px 20px;position:relative;z-index:1}
.form-wrapper{width:100%;max-width:400px}
.form-header{text-align:center;margin-bottom:32px}
.form-header h2{font-size:26px;font-weight:700;color:#1e293b;margin-bottom:8px}
.form-header p{font-size:14px;color:#64748b}
.auth-form{background:#fff;border-radius:16px;padding:32px 28px;box-shadow:0 4px 24px rgba(0,0,0,.06)}
.input-group{margin-bottom:18px}
.input-group label{display:block;font-size:13px;font-weight:600;color:#374151;margin-bottom:6px}
.input-box{display:flex;align-items:center;border:1px solid #d1d5db;border-radius:10px;overflow:hidden;transition:border-color .2s,box-shadow .2s;background:#fff}
.input-box:focus-within{border-color:var(--primary);box-shadow:0 0 0 3px rgba(45,138,78,.15)}
.input-icon{margin:0 10px;color:#9ca3af;flex-shrink:0}
.input-box input{flex:1;border:none;outline:none;padding:12px 12px 12px 0;font-size:14px;color:#1e293b;background:transparent;min-width:0}
.input-box input::placeholder{color:#9ca3af}
.toggle-pwd{padding:0 12px;cursor:pointer;color:#9ca3af;user-select:none;flex-shrink:0;display:flex;align-items:center}
.toggle-pwd:hover{color:var(--primary)}
.code-row{display:flex;gap:10px}
.code-input-box{flex:1}
.send-code-btn{flex-shrink:0;min-width:110px;padding:10px 14px;background:var(--primary);color:#fff;border:none;border-radius:10px;font-size:13px;font-weight:600;cursor:pointer;white-space:nowrap;transition:background .2s}
.send-code-btn:hover:not(:disabled){background:var(--primary-hover)}
.send-code-btn:disabled{background:#86efac;cursor:not-allowed}
.form-options{display:flex;align-items:center;justify-content:space-between;margin-bottom:18px}
.remember-me{display:flex;align-items:center;gap:6px;font-size:13px;color:#6b7280;cursor:pointer}
.remember-me input[type=checkbox]{accent-color:var(--primary);width:16px;height:16px}
.form-options a{font-size:13px;color:var(--primary);text-decoration:none;font-weight:500}
.form-options a:hover{text-decoration:underline}
.err-msg{background:#fef2f2;border:1px solid #fecaca;color:#dc2626;padding:10px 14px;border-radius:8px;font-size:13px;margin-bottom:16px}
.success-msg{background:#f0fdf4;border:1px solid #bbf7d0;color:#14532d;padding:10px 14px;border-radius:8px;font-size:13px;margin-bottom:16px}
.submit-btn{width:100%;padding:13px;background:linear-gradient(135deg,var(--primary),var(--primary-hover));color:#fff;border:none;border-radius:10px;font-size:15px;font-weight:600;cursor:pointer;transition:transform .15s,box-shadow .15s}
.submit-btn:hover:not(:disabled){transform:translateY(-1px);box-shadow:0 4px 14px rgba(45,138,78,.35)}
.submit-btn:active{transform:translateY(0)}
.submit-btn:disabled{opacity:.6;cursor:not-allowed}
.form-footer{text-align:center;margin-top:20px;font-size:14px;color:#64748b}
.form-footer a{color:var(--primary);text-decoration:none;font-weight:600}
.form-footer a:hover{text-decoration:underline}
.back-home{display:flex;align-items:center;justify-content:center;gap:4px;margin-top:16px;font-size:13px;color:#94a3b8;text-decoration:none;transition:color .2s}
.back-home:hover{color:var(--primary)}
@media(max-width:768px){.login-left{display:none}.login-right{flex:1;padding:24px 16px}.auth-form{padding:24px 20px}.code-row{flex-direction:column}.send-code-btn{width:100%}}
</style>
