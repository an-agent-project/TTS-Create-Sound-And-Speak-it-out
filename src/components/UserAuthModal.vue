<template>
  <div class="auth-overlay" @click.self="$emit('close')">
    <div class="auth-card">
      <!-- Close button -->
      <button class="close-x" @click="$emit('close')">✕</button>

      <!-- Tab switcher -->
      <div class="tab-bar">
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'password' }"
          @click="activeTab = 'password'"
        >
          密码登录
        </button>
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'sms' }"
          @click="activeTab = 'sms'"
        >
          短信登录
        </button>
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'qr' }"
          @click="activeTab = 'qr'"
        >
          扫码登录
        </button>
      </div>

      <!-- ========== PASSWORD LOGIN ========== -->
      <div v-if="activeTab === 'password'" class="tab-content">
        <div v-if="!isPasswordRegister" class="form-wrap">
          <div class="input-group">
            <span class="input-icon">👤</span>
            <input
              v-model="pwForm.username"
              type="text"
              class="clean-input"
              placeholder="请输入账户名称"
              autocomplete="username"
            />
          </div>
          <div class="input-group">
            <span class="input-icon">🔒</span>
            <input
              v-model="pwForm.password"
              type="password"
              class="clean-input"
              placeholder="请输入密码"
              autocomplete="current-password"
            />
          </div>
          <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>
          <button class="submit-btn" @click="handlePasswordLogin">
            登 录
          </button>
          <div class="bottom-link">
            还没有账号？
            <a href="#" @click.prevent="switchToPwRegister">立即注册</a>
          </div>
        </div>

        <!-- Register sub-form -->
        <div v-else class="form-wrap">
          <div class="input-group">
            <span class="input-icon">👤</span>
            <input
              v-model="pwForm.username"
              type="text"
              class="clean-input"
              placeholder="设置账户名称"
              autocomplete="username"
            />
          </div>
          <div class="input-group">
            <span class="input-icon">🔒</span>
            <input
              v-model="pwForm.password"
              type="password"
              class="clean-input"
              placeholder="设置密码"
              autocomplete="new-password"
            />
          </div>
          <div class="input-group">
            <span class="input-icon">🔒</span>
            <input
              v-model="pwForm.confirmPassword"
              type="password"
              class="clean-input"
              placeholder="确认密码"
              autocomplete="new-password"
            />
          </div>
          <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>
          <button class="submit-btn" @click="handlePasswordRegister">
            注 册
          </button>
          <div class="bottom-link">
            已有账号？
            <a href="#" @click.prevent="switchToPwLogin">返回登录</a>
          </div>
        </div>
      </div>

      <!-- ========== SMS LOGIN ========== -->
      <div v-if="activeTab === 'sms'" class="tab-content">
        <div class="form-wrap">
          <div class="input-group">
            <span class="input-icon">📱</span>
            <input
              v-model="smsForm.phone"
              type="tel"
              class="clean-input"
              placeholder="请输入手机号"
              maxlength="11"
            />
          </div>
          <div class="input-group sms-group">
            <span class="input-icon">✉️</span>
            <input
              v-model="smsForm.code"
              type="text"
              class="clean-input"
              placeholder="请输入验证码"
              maxlength="6"
            />
            <button
              class="sms-btn"
              :disabled="smsCountdown > 0"
              @click="sendSms"
            >
              {{ smsCountdown > 0 ? smsCountdown + 's' : '获取验证码' }}
            </button>
          </div>
          <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>
          <button class="submit-btn" @click="handleSmsLogin">
            登 录
          </button>
          <div class="bottom-link" style="font-size:12px;color:var(--text-muted);">
            未注册手机号将自动创建账号
          </div>
        </div>
      </div>

      <!-- ========== QR LOGIN ========== -->
      <div v-if="activeTab === 'qr'" class="tab-content">
        <div class="qr-section">
          <div class="qr-placeholder">
            <span class="qr-icon">📱</span>
            <p class="qr-text">请使用 QQ / 微信 扫码登录</p>
            <div class="fake-qr">
              <div class="qr-grid">
                <div v-for="i in 25" :key="i" class="qr-cell" :class="{ dark: qrPattern.includes(i) }"></div>
              </div>
            </div>
            <p class="qr-hint">扫码后请在手机上确认登录</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Phone Bind Modal (shown after login if no phone) -->
    <PhoneBindModal
      v-if="showPhoneBind"
      :username="newlyLoggedUser"
      @close="showPhoneBind = false; $emit('close')"
      @bind-success="onPhoneBound"
    />
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { useAppStore } from "../stores/app.js";
import PhoneBindModal from "./PhoneBindModal.vue";

const store = useAppStore();
const emit = defineEmits(["close"]);

const activeTab = ref("password");
const isPasswordRegister = ref(false);
const errorMsg = ref("");
const smsCountdown = ref(0);
const showPhoneBind = ref(false);
const newlyLoggedUser = ref("");

// Generate a pseudo-random QR-like pattern for visual effect
const qrPattern = [1,2,3,4,5,6,10,11,15,16,20,21,22,23,24,25];

// Password form
const pwForm = reactive({
  username: "",
  password: "",
  confirmPassword: "",
});

// SMS form
const smsForm = reactive({
  phone: "",
  code: "",
});

function switchToPwRegister() {
  isPasswordRegister.value = true;
  errorMsg.value = "";
  pwForm.username = "";
  pwForm.password = "";
  pwForm.confirmPassword = "";
}

function switchToPwLogin() {
  isPasswordRegister.value = false;
  errorMsg.value = "";
  pwForm.username = "";
  pwForm.password = "";
  pwForm.confirmPassword = "";
}

function handlePasswordLogin() {
  errorMsg.value = "";
  if (!pwForm.username.trim()) { errorMsg.value = "请输入账户名称"; return; }
  if (!pwForm.password) { errorMsg.value = "请输入密码"; return; }

  const users = JSON.parse(localStorage.getItem("users") || "[]");
  const found = users.find(
    (u) => u.username === pwForm.username && u.password === pwForm.password
  );
  if (!found) {
    errorMsg.value = "账户名称或密码错误";
    return;
  }
  store.login(found);
  checkPhoneBind(found.username);
}

function handlePasswordRegister() {
  errorMsg.value = "";
  if (!pwForm.username.trim()) { errorMsg.value = "请设置账户名称"; return; }
  if (!pwForm.password) { errorMsg.value = "请设置密码"; return; }
  if (pwForm.password.length < 3) { errorMsg.value = "密码至少3位"; return; }
  if (pwForm.password !== pwForm.confirmPassword) { errorMsg.value = "两次密码不一致"; return; }

  const users = JSON.parse(localStorage.getItem("users") || "[]");
  if (users.find((u) => u.username === pwForm.username)) {
    errorMsg.value = "账户名称已存在";
    return;
  }
  store.register({
    username: pwForm.username,
    email: "",
    password: pwForm.password,
  });
  checkPhoneBind(pwForm.username);
}

function checkPhoneBind(username) {
  // Check if user has no phone, prompt binding
  const stored = JSON.parse(localStorage.getItem("user") || "{}");
  if (!stored.phone) {
    newlyLoggedUser.value = username;
    showPhoneBind.value = true;
  } else {
    emit("close");
  }
}

function onPhoneBound() {
  showPhoneBind.value = false;
  emit("close");
}

function sendSms() {
  if (smsForm.phone.length < 11) {
    errorMsg.value = "请输入正确的手机号";
    return;
  }
  errorMsg.value = "";
  // Simulate sending SMS
  smsCountdown.value = 60;
  const timer = setInterval(() => {
    smsCountdown.value--;
    if (smsCountdown.value <= 0) {
      clearInterval(timer);
    }
  }, 1000);
  // For demo, auto-fill a code
  smsForm.code = "123456";
}

function handleSmsLogin() {
  errorMsg.value = "";
  if (smsForm.phone.length < 11) { errorMsg.value = "请输入正确的手机号"; return; }
  if (!smsForm.code) { errorMsg.value = "请输入验证码"; return; }
  // Demo: code is always "123456"
  if (smsForm.code !== "123456") { errorMsg.value = "验证码错误"; return; }

  // Find or create user by phone
  const users = JSON.parse(localStorage.getItem("users") || "[]");
  let found = users.find((u) => u.phone === smsForm.phone);
  if (!found) {
    // Auto-register
    found = {
      id: Date.now().toString(),
      username: "用户" + smsForm.phone.slice(-4),
      phone: smsForm.phone,
      password: "",
      email: "",
      avatar: "",
      registeredAt: new Date().toISOString(),
    };
    users.push(found);
    localStorage.setItem("users", JSON.stringify(users));
  }
  store.login(found);
  emit("close");
}
</script>

<style scoped>
/* Overlay - semi transparent */
.auth-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(2px);
}

/* Card - ~1/8 of page (320px on 1920px wide) */
.auth-card {
  background: #ffffff;
  border-radius: 12px;
  width: 340px;
  max-width: calc(100vw - 32px);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
  position: relative;
  padding: 0;
  overflow: hidden;
}

/* Close X */
.close-x {
  position: absolute;
  top: 14px;
  right: 16px;
  background: none;
  border: none;
  font-size: 18px;
  color: #999;
  cursor: pointer;
  z-index: 2;
  padding: 4px 8px;
  border-radius: 4px;
}

.close-x:hover {
  background: #f5f5f5;
  color: #333;
}

/* Tab bar */
.tab-bar {
  display: flex;
  border-bottom: 1px solid #eee;
  padding: 0 20px;
}

.tab-btn {
  flex: 1;
  padding: 16px 0 12px;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  font-size: 14px;
  color: #999;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.tab-btn:hover {
  color: #666;
}

.tab-btn.active {
  color: #333;
  border-bottom-color: #333;
  font-weight: 600;
}

/* Tab content */
.tab-content {
  padding: 28px 28px 32px;
}

.form-wrap {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Clean inputs */
.input-group {
  display: flex;
  align-items: center;
  border: 1px solid #e5e5e5;
  border-radius: 6px;
  padding: 0 12px;
  transition: border-color 0.2s;
  background: #fafafa;
}

.input-group:focus-within {
  border-color: #6366f1;
  background: #fff;
}

.input-icon {
  font-size: 16px;
  margin-right: 8px;
  flex-shrink: 0;
}

.clean-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  padding: 12px 0;
  font-size: 14px;
  color: #333;
}

.clean-input::placeholder {
  color: #bbb;
}

/* SMS input with button */
.sms-group {
  position: relative;
}

.sms-btn {
  position: absolute;
  right: 4px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--primary);
  font-size: 13px;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 4px;
  white-space: nowrap;
}

.sms-btn:hover:not(:disabled) {
  background: var(--primary-light);
}

.sms-btn:disabled {
  color: #ccc;
  cursor: not-allowed;
}

/* Error */
.error-msg {
  background: #fff2f0;
  border: 1px solid #ffccc7;
  color: #ff4d4f;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 13px;
}

/* Submit button */
.submit-btn {
  width: 100%;
  padding: 12px;
  background: #333;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  letter-spacing: 4px;
}

.submit-btn:hover {
  background: #555;
}

/* Bottom link */
.bottom-link {
  text-align: center;
  font-size: 13px;
  color: #999;
}

.bottom-link a {
  color: var(--primary);
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
}

.bottom-link a:hover {
  text-decoration: underline;
}

/* QR section */
.qr-section {
  text-align: center;
}

.qr-icon {
  font-size: 40px;
  display: block;
  margin-bottom: 12px;
}

.qr-text {
  font-size: 14px;
  color: #666;
  margin-bottom: 20px;
}

/* Fake QR code visual */
.fake-qr {
  width: 140px;
  height: 140px;
  margin: 0 auto 16px;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 8px;
  background: #fff;
}

.qr-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  grid-template-rows: repeat(5, 1fr);
  width: 100%;
  height: 100%;
  gap: 2px;
}

.qr-cell {
  background: #f5f5f5;
  border-radius: 2px;
}

.qr-cell.dark {
  background: #333;
}

.qr-hint {
  font-size: 12px;
  color: #aaa;
}
</style>