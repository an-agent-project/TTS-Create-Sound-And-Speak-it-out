<template>
  <div class="bind-overlay" @click.self="$emit('close')">
    <div class="bind-card">
      <button class="close-x" @click="$emit('close')">✕</button>

      <div class="bind-icon">📱</div>
      <h3 class="bind-title">绑定手机号</h3>
      <p class="bind-desc">为了账户安全，建议绑定手机号</p>

      <div class="input-group">
        <span class="input-icon">📱</span>
        <input
          v-model="phone"
          type="tel"
          class="clean-input"
          placeholder="请输入手机号"
          maxlength="11"
        />
      </div>

      <div class="input-group sms-group">
        <span class="input-icon">✉️</span>
        <input
          v-model="code"
          type="text"
          class="clean-input"
          placeholder="请输入验证码"
          maxlength="6"
        />
        <button
          class="sms-btn"
          :disabled="countdown > 0 || phone.length < 11"
          @click="sendCode"
        >
          {{ countdown > 0 ? countdown + 's' : '获取验证码' }}
        </button>
      </div>

      <div v-if="error" class="error-msg">{{ error }}</div>

      <div class="bind-actions">
        <button class="submit-btn" @click="handleBind">确认绑定</button>
        <button class="skip-btn" @click="$emit('close')">暂时跳过</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useAppStore } from "../stores/app.js";

const store = useAppStore();
const emit = defineEmits(["close", "bindSuccess"]);

const phone = ref("");
const code = ref("");
const countdown = ref(0);
const error = ref("");

function sendCode() {
  if (phone.value.length < 11) {
    error.value = "请输入正确的手机号";
    return;
  }
  error.value = "";
  countdown.value = 60;
  const timer = setInterval(() => {
    countdown.value--;
    if (countdown.value <= 0) clearInterval(timer);
  }, 1000);
  code.value = "123456";
}

function handleBind() {
  error.value = "";
  if (phone.value.length < 11) { error.value = "请输入正确的手机号"; return; }
  if (!code.value) { error.value = "请输入验证码"; return; }
  if (code.value !== "123456") { error.value = "验证码错误"; return; }

  store.updatePhone(phone.value);
  emit("bindSuccess");
}
</script>

<style scoped>
.bind-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 2100;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bind-card {
  background: #fff;
  border-radius: 12px;
  width: 320px;
  padding: 32px 28px 24px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
  position: relative;
  text-align: center;
}

.close-x {
  position: absolute;
  top: 12px;
  right: 14px;
  background: none;
  border: none;
  font-size: 16px;
  color: #999;
  cursor: pointer;
}

.bind-icon {
  font-size: 40px;
  margin-bottom: 12px;
}

.bind-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 6px;
  color: #333;
}

.bind-desc {
  font-size: 13px;
  color: #999;
  margin-bottom: 24px;
}

.input-group {
  display: flex;
  align-items: center;
  border: 1px solid #e5e5e5;
  border-radius: 6px;
  padding: 0 12px;
  background: #fafafa;
  margin-bottom: 12px;
  transition: border-color 0.2s;
}

.input-group:focus-within {
  border-color: var(--primary);
  background: #fff;
}

.input-icon {
  font-size: 16px;
  margin-right: 8px;
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
}

.sms-btn:disabled {
  color: #ccc;
  cursor: not-allowed;
}

.error-msg {
  background: #fff2f0;
  border: 1px solid #ffccc7;
  color: #ff4d4f;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 13px;
  margin-bottom: 12px;
}

.bind-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 4px;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  background: #333;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.submit-btn:hover {
  background: #555;
}

.skip-btn {
  background: none;
  border: none;
  color: #999;
  font-size: 13px;
  cursor: pointer;
  padding: 8px;
}

.skip-btn:hover {
  color: #666;
}
</style>