<template>
  <div class="extract-page">
    <div class="page-header">
      <h1><Wand2 :size="28" class="title-icon" /> 音色提取台</h1>
      <p>上传本地音频，AI 提取人声音色，一键加入你的个人音色库</p>
    </div>

    <div class="extract-layout">
      <!-- LEFT: 提取结果 -->
      <div class="extract-left card">
        <h3>
          <Music :size="18" />
          提取结果
          <span class="result-count" v-if="extractedVoices.length">{{ extractedVoices.length }} 个音色</span>
        </h3>

        <!-- 结果列表 -->
        <div v-if="extractedVoices.length > 0" class="result-list">
          <div
            v-for="voice in extractedVoices"
            :key="voice.id"
            class="result-card"
            :class="{ playing: playingId === voice.id }"
          >
            <div class="voice-icon">
              <Mic :size="28" />
            </div>
            <div class="voice-info">
              <div class="voice-name">{{ voice.name }}</div>
              <div class="voice-meta">
                <span class="tag" v-for="t in voice.tags" :key="t">{{ t }}</span>
                <span class="meta-item"><Clock :size="12" />{{ formatTime(voice.duration) }}</span>
                <span class="meta-item"><HardDrive :size="12" />{{ formatSize(voice.size) }}</span>
              </div>
            </div>
            <div class="voice-actions">
              <button class="act-btn play-btn" @click="togglePlay(voice)">
                <Pause v-if="playingId === voice.id" :size="16" />
                <Play v-else :size="16" />
              </button>
              <button class="act-btn" @click="addToLibrary(voice)" title="添加到个人音色库">
                <Plus :size="16" />
              </button>
              <button class="act-btn" @click="downloadVoice(voice)" title="下载到本地">
                <Download :size="16" />
              </button>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else class="empty-extract">
          <Upload :size="48" class="empty-icon" />
          <p>等待上传音频后点击提取</p>
        </div>
      </div>

      <!-- RIGHT: 上传 & 提取 -->
      <div class="extract-right card">
        <h3><Upload :size="18" /> 上传音频</h3>

        <!-- 上传区域 -->
        <div
          class="upload-zone"
          :class="{ 'has-file': uploadedFile, 'dragover': isDragover }"
          @click="triggerUpload"
          @dragover.prevent="isDragover = true"
          @dragleave="isDragover = false"
          @drop.prevent="handleDrop"
        >
          <template v-if="!uploadedFile">
            <FileAudio :size="40" class="upload-icon" />
            <p class="upload-text">拖拽音频文件到此处或点击上传</p>
            <p class="upload-hint">支持 MP3 / WAV / FLAC / M4A 格式</p>
          </template>
          <template v-else>
            <div class="file-preview">
              <FileAudio :size="36" />
              <div class="file-info">
                <span class="file-name">{{ uploadedFile.name }}</span>
                <span class="file-meta">{{ formatSize(uploadedFile.size) }}</span>
              </div>
              <button class="remove-file" @click.stop="removeFile">x</button>
            </div>
          </template>
          <input ref="fileInput" type="file" accept=".mp3,.wav,.flac,.m4a,.aac" style="display:none" @change="onFileSelected" />
        </div>

        <div class="clone-form">
          <label class="field-label" for="clone-name">音色名称</label>
          <input id="clone-name" v-model="cloneName" class="form-input" type="text" placeholder="例如：我的旁白音色" />
          <label class="field-label" for="clone-preferred-name">英文标识</label>
          <input id="clone-preferred-name" v-model="clonePreferredName" class="form-input" type="text" placeholder="可选，例如 my_voice" />
        </div>

        <!-- 提取按钮 -->
        <button
          class="extract-btn"
          :disabled="!uploadedFile || !cloneName || isExtracting"
          @click="cloneVoice"
        >
          <Loader v-if="isExtracting" :size="18" class="spin" />
          <Wand2 v-else :size="18" />
          {{ isExtracting ? '正在克隆音色...' : '克隆音色' }}
        </button>

        <!-- 状态提示 -->
        <div v-if="extractStatus" class="extract-status" :class="{ success: extractOk, error: !extractOk }">
          {{ extractStatus }}
        </div>
      </div>
    </div>

    <audio ref="audioEl" @timeupdate="onTime" @loadedmetadata="onMeta" @ended="onEnd"></audio>
  </div>
</template>

<script setup>
import { ref, reactive, onBeforeUnmount } from "vue"
import { Wand2, Music, Upload, Mic, Play, Pause, Plus, Download, Clock, HardDrive, FileAudio, Loader } from "lucide-vue-next"
import { createVoiceClone, synthesizeVoicePreview } from "../services/api.js"

const fileInput = ref(null)
const audioEl = ref(null)
const uploadedFile = ref(null)
const isDragover = ref(false)
const isExtracting = ref(false)
const extractStatus = ref("")
const extractOk = ref(true)
const cloneName = ref("")
const clonePreferredName = ref("")
const playingId = ref(null)
const currentTime = ref(0)
const duration = ref(0)
const progressPercent = ref(0)

// 提取结果
const extractedVoices = reactive([])

// --- 上传 ---
function triggerUpload() { fileInput.value?.click() }

function onFileSelected(e) {
  const f = e.target.files?.[0]
  if (f) {
    uploadedFile.value = f
    extractStatus.value = ""
    if (!cloneName.value) cloneName.value = f.name.replace(/\.[^.]+$/, "")
  }
  e.target.value = ""
}

function handleDrop(e) {
  isDragover.value = false
  const f = e.dataTransfer?.files?.[0]
  if (f) {
    uploadedFile.value = f
    extractStatus.value = ""
    if (!cloneName.value) cloneName.value = f.name.replace(/\.[^.]+$/, "")
  }
}

function removeFile() {
  uploadedFile.value = null
  extractStatus.value = ""
  cloneName.value = ""
  clonePreferredName.value = ""
}

// --- 音色克隆 ---
async function cloneVoice() {
  if (!uploadedFile.value || !cloneName.value || isExtracting.value) return
  isExtracting.value = true
  extractStatus.value = ""
  extractOk.value = true

  try {
    const formData = new FormData()
    formData.append("name", cloneName.value)
    formData.append("preferredName", clonePreferredName.value || cloneName.value)
    formData.append("file", uploadedFile.value)
    const clonedVoice = await createVoiceClone(formData)
    const preview = await synthesizeVoicePreview({
      text: "你好，这是我的克隆音色试听。欢迎来到音色提取台。",
      voiceId: clonedVoice.providers?.[0]?.providerVoiceId,
    })
    extractedVoices.unshift({
      id: clonedVoice.id || Date.now(),
      name: clonedVoice.displayName || clonedVoice.name || cloneName.value,
      tags: ["个人音色", "已入库"],
      duration: preview.duration || 0,
      size: uploadedFile.value.size,
      src: preview.audioUrl,
    })
    extractStatus.value = "音色克隆成功，试听音频已生成，并已加入个人音色库。"
    extractOk.value = true
    uploadedFile.value = null
    cloneName.value = ""
    clonePreferredName.value = ""
  } catch (error) {
    extractStatus.value = error.message || "音色克隆失败"
    extractOk.value = false
  } finally {
    isExtracting.value = false
  }
}
// --- 播放 ---
function togglePlay(voice) {
  if (playingId.value === voice.id) {
    audioEl.value?.pause()
    playingId.value = null
    return
  }
  playingId.value = voice.id
  const el = audioEl.value
  if (!el || !voice.src) return
  el.src = voice.src
  el.play()
}

function onTime() {
  if (audioEl.value) {
    currentTime.value = audioEl.value.currentTime
    if (duration.value > 0) progressPercent.value = (currentTime.value / duration.value) * 100
  }
}
function onMeta() {
  if (audioEl.value) duration.value = audioEl.value.duration || 0
}
function onEnd() { playingId.value = null }

// --- 操作 ---
function addToLibrary(voice) {
  alert("已在个人音色库中：" + voice.name)
}
function downloadVoice(voice) {
  if (voice.src) {
    const a = document.createElement("a")
    a.href = voice.src
    a.download = voice.name + ".wav"
    a.click()
  }
}

function formatTime(s) {
  if (!s) return "0:00"
  const m = Math.floor(s / 60)
  return m + ":" + String(Math.floor(s % 60)).padStart(2, "0")
}
function formatSize(b) {
  if (!b) return ""
  if (b < 1024) return b + " B"
  if (b < 1048576) return (b / 1024).toFixed(1) + " KB"
  return (b / 1048576).toFixed(1) + " MB"
}

onBeforeUnmount(() => { audioEl.value?.pause() })
</script>

<style scoped>
.extract-page{max-width:1200px;margin:0 auto;padding:32px 24px}
.page-header{margin-bottom:24px}
.page-header h1{font-size:24px;font-weight:700;display:flex;align-items:center;gap:10px;color:#1e293b}
.page-header p{font-size:14px;color:#64748b;margin-top:4px}
.title-icon{color:#6366f1}

.extract-layout{display:grid;grid-template-columns:1fr 380px;gap:24px;align-items:start}

/* Card base */
.card{background:#fff;border-radius:16px;padding:24px;box-shadow:0 2px 12px rgba(0,0,0,.04);border:1px solid #e2e8f0}
.card h3{font-size:16px;font-weight:600;display:flex;align-items:center;gap:8px;color:#1e293b;margin-bottom:20px}

/* LEFT: results */
.result-count{font-size:13px;font-weight:400;color:#94a3b8;margin-left:auto}
.result-list{display:flex;flex-direction:column;gap:10px}
.result-card{display:flex;align-items:center;gap:14px;padding:14px 16px;background:#f8fafc;border-radius:12px;border:1px solid #e2e8f0;transition:all .2s}
.result-card:hover{border-color:#c7d2fe}
.result-card.playing{border-color:#6366f1;background:#eef2ff}
.voice-icon{width:48px;height:48px;background:#eef2ff;border-radius:12px;display:flex;align-items:center;justify-content:center;color:#6366f1;flex-shrink:0}
.voice-info{flex:1;min-width:0}
.voice-name{font-size:14px;font-weight:600;color:#1e293b;margin-bottom:4px}
.voice-meta{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.tag{font-size:11px;padding:2px 8px;background:#eef2ff;color:#6366f1;border-radius:4px;font-weight:500}
.meta-item{display:flex;align-items:center;gap:3px;font-size:11px;color:#94a3b8}
.voice-actions{display:flex;gap:4px;flex-shrink:0}
.act-btn{width:32px;height:32px;border:1px solid #e2e8f0;border-radius:8px;background:#fff;color:#64748b;display:flex;align-items:center;justify-content:center;cursor:pointer;transition:all .15s}
.act-btn:hover{border-color:#6366f1;color:#6366f1;background:#eef2ff}
.play-btn{width:36px;height:36px;border-radius:50%;background:#6366f1;border:none;color:#fff}
.play-btn:hover{background:#4f46e5;color:#fff}

.empty-extract{text-align:center;padding:60px 20px;color:#94a3b8}
.empty-icon{margin-bottom:12px;opacity:.4}

/* RIGHT: upload */
.upload-zone{border:2px dashed #d1d5db;border-radius:12px;padding:40px 20px;text-align:center;cursor:pointer;transition:all .2s;margin-bottom:16px}
.upload-zone:hover{border-color:#6366f1;background:#f8faff}
.upload-zone.dragover{border-color:#6366f1;background:#eef2ff}
.upload-zone.has-file{border-style:solid;border-color:#6366f1;background:#f8faff;padding:24px}
.upload-icon{color:#94a3b8;margin-bottom:12px}
.upload-text{font-size:14px;color:#475569;font-weight:500}
.upload-hint{font-size:12px;color:#94a3b8;margin-top:4px}

.file-preview{display:flex;align-items:center;gap:12px;color:#475569}
.file-name{font-weight:500;font-size:14px}
.file-meta{font-size:12px;color:#94a3b8}
.remove-file{width:24px;height:24px;border-radius:50%;border:1px solid #e2e8f0;background:#fff;color:#94a3b8;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:12px;margin-left:auto}
.remove-file:hover{background:#fef2f2;border-color:#fecaca;color:#ef4444}

.clone-form{display:grid;gap:8px;margin-bottom:16px}
.field-label{font-size:12px;font-weight:600;color:#64748b}
.form-input{height:38px;border:1px solid #d1d5db;border-radius:8px;padding:0 10px;color:#1e293b;background:#fff}
.form-input:focus{outline:none;border-color:#6366f1;box-shadow:0 0 0 3px rgba(99,102,241,.12)}

.extract-btn{width:100%;padding:14px;background:linear-gradient(135deg,#6366f1,#7c3aed);color:#fff;border:none;border-radius:10px;font-size:15px;font-weight:600;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:8px;transition:all .15s}
.extract-btn:hover:not(:disabled){transform:translateY(-1px);box-shadow:0 4px 14px rgba(99,102,241,.4)}
.extract-btn:disabled{opacity:.5;cursor:not-allowed}
.spin{animation:spin 1s linear infinite}
@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}

.extract-status{margin-top:12px;padding:10px 14px;border-radius:8px;font-size:13px;text-align:center}
.extract-status.success{background:#f0fdf4;color:#16a34a;border:1px solid #bbf7d0}
.extract-status.error{background:#fef2f2;color:#dc2626;border:1px solid #fecaca}

@media(max-width:768px){
  .extract-layout{grid-template-columns:1fr}
  .extract-right{order:-1}
}
</style>
