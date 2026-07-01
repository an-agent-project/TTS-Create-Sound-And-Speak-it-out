<template>
  <div class="extract-page">
    <div class="page-header">
      <h1><Wand2 :size="28" class="title-icon" /> 音色提取台</h1>
      <p>上传本地音频，调用 AI 克隆人声音色，并加入你的个人音色库</p>
    </div>

    <div class="extract-layout">
      <div class="extract-left card">
        <h3>
          <Music :size="18" />
          提取结果
          <span class="result-count" v-if="extractedVoices.length">{{ extractedVoices.length }} 个音色</span>
        </h3>

        <div v-if="extractedVoices.length > 0" class="result-list">
          <div
            v-for="voice in extractedVoices"
            :key="voice.id"
            class="result-card"
            :class="{ playing: playingId === voice.id }"
          >
            <div class="voice-icon"><Mic :size="28" /></div>
            <div class="voice-info">
              <div class="voice-name">{{ voice.name }}</div>
              <div class="voice-meta">
                <span class="tag" v-for="tag in voice.tags" :key="tag">{{ tag }}</span>
                <span class="meta-item"><Clock :size="12" />{{ formatTime(voice.duration) }}</span>
                <span class="meta-item"><HardDrive :size="12" />{{ formatSize(voice.size) }}</span>
              </div>
            </div>
            <div class="voice-actions">
              <button class="act-btn play-btn" type="button" @click="togglePlay(voice)">
                <Pause v-if="playingId === voice.id" :size="16" />
                <Play v-else :size="16" />
              </button>
              <button class="act-btn" type="button" @click="addToLibrary(voice)" title="已加入个人音色库">
                <Plus :size="16" />
              </button>
              <button class="act-btn" type="button" @click="downloadVoice(voice)" title="下载试听音频">
                <Download :size="16" />
              </button>
            </div>
          </div>
        </div>

        <div v-else class="empty-extract">
          <Upload :size="48" class="empty-icon" />
          <p>等待上传音频后开始克隆</p>
        </div>
      </div>

      <div class="extract-right card">
        <h3><Upload :size="18" /> 上传音频</h3>

        <div
          class="upload-zone"
          :class="{ 'has-file': uploadedFile, dragover: isDragover }"
          @click="triggerUpload"
          @dragover.prevent="isDragover = true"
          @dragleave="isDragover = false"
          @drop.prevent="handleDrop"
        >
          <template v-if="!uploadedFile">
            <FileAudio :size="40" class="upload-icon" />
            <p class="upload-text">拖拽音频文件到此处或点击上传</p>
            <p class="upload-hint">支持 MP3 / WAV / FLAC / M4A / AAC</p>
          </template>
          <template v-else>
            <div class="file-preview">
              <FileAudio :size="36" />
              <div class="file-info">
                <span class="file-name">{{ uploadedFile.name }}</span>
                <span class="file-meta">{{ formatSize(uploadedFile.size) }}</span>
              </div>
              <button class="remove-file" type="button" @click.stop="removeFile">x</button>
            </div>
          </template>
          <input ref="fileInput" type="file" accept=".mp3,.wav,.flac,.m4a,.aac" hidden @change="onFileSelected" />
        </div>

        <div class="clone-form">
          <label class="field-label" for="clone-name">音色名称</label>
          <input id="clone-name" v-model="cloneName" class="form-input" type="text" placeholder="例如：我的旁白音色" />
          <label class="field-label" for="clone-preferred-name">英文标识</label>
          <input id="clone-preferred-name" v-model="clonePreferredName" class="form-input" type="text" placeholder="可选，例如 my_voice" />
        </div>

        <button class="extract-btn" type="button" :disabled="!uploadedFile || !cloneName || isExtracting" @click="cloneVoice">
          <Loader v-if="isExtracting" :size="18" class="spin" />
          <Wand2 v-else :size="18" />
          {{ isExtracting ? '正在克隆音色...' : '克隆音色' }}
        </button>

        <div v-if="isExtracting" class="clone-progress-card">
          <div class="clone-progress-header">
            <span>{{ cloneProgressMessage || '正在准备克隆任务' }}</span>
            <strong>{{ cloneProgress }}%</strong>
          </div>
          <div class="clone-progress-track">
            <div class="clone-progress-fill" :style="{ width: cloneProgress + '%' }"></div>
          </div>
        </div>

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
import { createJobEventSource, createVoiceCloneJob, synthesizeVoicePreview } from "../services/api.js"

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
const cloneProgress = ref(0)
const cloneProgressMessage = ref("")
const cloneJobSource = ref(null)
const extractedVoices = reactive([])

function triggerUpload() { fileInput.value?.click() }

function onFileSelected(event) {
  const file = event.target.files?.[0]
  if (file) setUploadedFile(file)
  event.target.value = ""
}

function handleDrop(event) {
  isDragover.value = false
  const file = event.dataTransfer?.files?.[0]
  if (file) setUploadedFile(file)
}

function setUploadedFile(file) {
  uploadedFile.value = file
  extractStatus.value = ""
  cloneProgress.value = 0
  cloneProgressMessage.value = ""
  if (!cloneName.value) cloneName.value = file.name.replace(/\.[^.]+$/, "")
}

function removeFile() {
  uploadedFile.value = null
  extractStatus.value = ""
  cloneProgress.value = 0
  cloneProgressMessage.value = ""
  cloneName.value = ""
  clonePreferredName.value = ""
}

async function cloneVoice() {
  if (!uploadedFile.value || !cloneName.value || isExtracting.value) return
  isExtracting.value = true
  extractStatus.value = ""
  extractOk.value = true

  try {
    const formData = new FormData()
    formData.append("name", cloneName.value)
    if (clonePreferredName.value.trim()) formData.append("preferredName", clonePreferredName.value.trim())
    formData.append("file", uploadedFile.value)

    cloneProgress.value = 1
    cloneProgressMessage.value = "正在提交克隆任务"
    const { jobId } = await createVoiceCloneJob(formData)
    const clonedVoice = await waitForCloneJob(jobId)

    cloneProgress.value = 92
    cloneProgressMessage.value = "正在生成试听音频"
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
    cloneProgress.value = 100
    cloneProgressMessage.value = "音色克隆完成"
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
    closeCloneJobSource()
  }
}

function waitForCloneJob(jobId) {
  closeCloneJobSource()
  return new Promise((resolve, reject) => {
    const source = createJobEventSource(jobId)
    cloneJobSource.value = source

    source.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data)
        cloneProgress.value = Math.max(0, Math.min(100, Number(payload.progress || 0)))
        cloneProgressMessage.value = payload.message || "正在克隆音色"
        if (payload.status === "completed") {
          closeCloneJobSource()
          resolve(payload.result?.voice)
        } else if (payload.status === "failed") {
          closeCloneJobSource()
          reject(new Error(payload.error || payload.message || "音色克隆失败"))
        }
      } catch (error) {
        closeCloneJobSource()
        reject(error)
      }
    }

    source.onerror = () => {
      closeCloneJobSource()
      reject(new Error("克隆进度连接中断"))
    }
  })
}

function closeCloneJobSource() {
  if (cloneJobSource.value) {
    cloneJobSource.value.close()
    cloneJobSource.value = null
  }
}

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
function onMeta() { if (audioEl.value) duration.value = audioEl.value.duration || 0 }
function onEnd() { playingId.value = null }
function addToLibrary(voice) { extractStatus.value = `${voice.name} 已在个人音色库中。`; extractOk.value = true }
function downloadVoice(voice) {
  if (!voice.src) return
  const link = document.createElement("a")
  link.href = voice.src
  link.download = `${voice.name}.mp3`
  link.click()
}
function formatTime(seconds) {
  if (!seconds) return "0:00"
  const minutes = Math.floor(seconds / 60)
  return `${minutes}:${String(Math.floor(seconds % 60)).padStart(2, "0")}`
}
function formatSize(bytes) {
  if (!bytes) return ""
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1048576).toFixed(1)} MB`
}

onBeforeUnmount(() => {
  audioEl.value?.pause()
  closeCloneJobSource()
})
</script>

<style scoped>
.extract-page{max-width:1200px;margin:0 auto;padding:32px 24px}.page-header{margin-bottom:24px}.page-header h1{font-size:24px;font-weight:700;display:flex;align-items:center;gap:10px;color:var(--text)}.page-header p{font-size:14px;color:var(--text-secondary);margin-top:4px}.title-icon{color:var(--primary)}.extract-layout{display:grid;grid-template-columns:1fr 380px;gap:24px;align-items:stretch}.card{background:var(--bg-card);border-radius:16px;padding:24px;box-shadow:var(--shadow);border:1px solid var(--border)}.card h3{font-size:16px;font-weight:600;display:flex;align-items:center;gap:8px;color:var(--text);margin-bottom:20px}.result-count{font-size:13px;font-weight:400;color:var(--text-muted);margin-left:auto}.result-list{display:flex;flex-direction:column;gap:10px}.result-card{display:flex;align-items:center;gap:14px;padding:14px 16px;background:var(--bg);border-radius:12px;border:1px solid var(--border);transition:all .2s}.result-card:hover,.result-card.playing{border-color:var(--primary);background:var(--primary-light)}.voice-icon{width:48px;height:48px;background:var(--primary-light);border-radius:12px;display:flex;align-items:center;justify-content:center;color:var(--primary);flex-shrink:0}.voice-info{flex:1;min-width:0}.voice-name{font-size:14px;font-weight:600;color:var(--text);margin-bottom:4px}.voice-meta{display:flex;align-items:center;gap:8px;flex-wrap:wrap}.tag{font-size:11px;padding:2px 8px;background:var(--primary-light);color:var(--primary);border-radius:4px;font-weight:500}.meta-item{display:flex;align-items:center;gap:3px;font-size:11px;color:var(--text-muted)}.voice-actions{display:flex;gap:4px;flex-shrink:0}.act-btn{width:32px;height:32px;border:1px solid var(--border);border-radius:8px;background:var(--bg-card);color:var(--text-secondary);display:flex;align-items:center;justify-content:center;cursor:pointer;transition:all .15s}.act-btn:hover{border-color:var(--primary);color:var(--primary);background:var(--primary-light)}.play-btn{width:36px;height:36px;border-radius:50%;background:var(--primary);border:none;color:#fff}.play-btn:hover{background:var(--primary-hover);color:#fff}.empty-extract{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;text-align:center;color:var(--text-muted)}.empty-icon{margin-bottom:12px;opacity:.4}.upload-zone{border:2px dashed var(--border);border-radius:12px;padding:40px 20px;text-align:center;cursor:pointer;transition:all .2s;margin-bottom:16px;background:var(--bg)}.upload-zone:hover,.upload-zone.dragover,.upload-zone.has-file{border-color:var(--primary);background:var(--primary-light)}.upload-icon{color:var(--text-muted);margin-bottom:12px}.upload-text{font-size:14px;color:var(--text-secondary);font-weight:500}.upload-hint{font-size:12px;color:var(--text-muted);margin-top:4px}.file-preview{display:flex;align-items:center;gap:12px;color:var(--text-secondary)}.file-info{min-width:0;text-align:left}.file-name{display:block;font-weight:500;font-size:14px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.file-meta{font-size:12px;color:var(--text-muted)}.remove-file{width:24px;height:24px;border-radius:50%;border:1px solid var(--border);background:var(--bg-card);color:var(--text-muted);cursor:pointer;margin-left:auto}.remove-file:hover{background:rgba(248,113,113,.12);border-color:rgba(248,113,113,.28);color:var(--danger)}.clone-form{display:grid;gap:8px;margin-bottom:16px}.field-label{font-size:12px;font-weight:600;color:var(--text-secondary)}.form-input{height:38px;border:1px solid var(--border);border-radius:8px;padding:0 10px;color:var(--text);background:var(--bg-card)}.form-input:focus{outline:none;border-color:var(--primary);box-shadow:0 0 0 3px var(--primary-light)}.extract-btn{width:100%;padding:14px;background:var(--primary);color:#fff;border:none;border-radius:10px;font-size:15px;font-weight:600;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:8px;transition:all .15s}.extract-btn:hover:not(:disabled){background:var(--primary-hover);transform:translateY(-1px);box-shadow:var(--shadow-md)}.extract-btn:disabled{opacity:.5;cursor:not-allowed}.clone-progress-card{margin:12px 0 0;padding:12px;border:1px solid var(--border);border-radius:10px;background:var(--bg-card)}.clone-progress-header{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:8px;font-size:13px;color:var(--text-secondary)}.clone-progress-header strong{color:var(--primary)}.clone-progress-track{height:8px;overflow:hidden;border-radius:999px;background:var(--border-light)}.clone-progress-fill{height:100%;border-radius:inherit;background:var(--primary);transition:width .25s ease}.spin{animation:spin 1s linear infinite}@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}.extract-status{margin-top:12px;padding:10px 14px;border-radius:8px;font-size:13px;text-align:center}.extract-status.success{background:rgba(52,211,153,.12);color:var(--success);border:1px solid rgba(52,211,153,.28)}.extract-status.error{background:rgba(248,113,113,.12);color:var(--danger);border:1px solid rgba(248,113,113,.28)}@media(max-width:768px){.extract-layout{grid-template-columns:1fr}.extract-right{order:-1}}
</style>
