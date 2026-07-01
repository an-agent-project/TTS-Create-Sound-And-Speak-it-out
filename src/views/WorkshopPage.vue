<template>
  <div class="workshop-page">
    <div class="workshop-header">
      <div class="header-info">
        <h2><Library :size="24" /> 个人素材库</h2>
        <p>公共音源空间 — 上传你的音源，或浏览获取他人的创作素材</p>
      </div>
      <button class="upload-btn" @click="triggerUpload">
        <Upload :size="18" /> 上传音源文件
      </button>
      <input ref="fileInputRef" type="file" accept=".mp3,.wav,.ogg,.flac,.m4a,.aac,.wma" multiple style="display:none" @change="handleFilesSelected" />
    </div>
    <div class="stats-bar">
      <div class="stat-item"><Music :size="18" /><span>共 <strong>{{ audios.length }}</strong> 个音源</span></div>
    </div>
    <div class="audio-grid" v-if="audios.length > 0">
      <div v-for="audio in audios" :key="audio.id" class="audio-card" :class="{ playing: playingId === audio.id }">
        <div class="audio-icon"><FileAudio :size="36" /><span class="format-badge">{{ audio.format.toUpperCase() }}</span></div>
        <div class="audio-info">
          <div class="audio-name" :title="audio.filename">{{ audio.filename }}</div>
          <div class="audio-meta">
            <span class="meta-item"><Clock :size="13" />{{ formatDuration(audio.duration) }}</span>
            <span class="meta-item"><User :size="13" />{{ audio.uploader || '匿名用户' }}</span>
            <span class="meta-item"><HardDrive :size="13" />{{ formatSize(audio.fileSize) }}</span>
          </div>
        </div>
        <div class="audio-actions">
          <button class="action-btn play-btn" :title="playingId===audio.id?'暂停':'试听'" @click="togglePreview(audio)">
            <Pause v-if="playingId === audio.id" :size="18" /><Play v-else :size="18" />
          </button>
          <button class="action-btn" title="添加到我的音色库" @click="addToLibrary(audio)"><Plus :size="16" /></button>
          <button class="action-btn" title="发送到提取台" @click="sendToExtract(audio)"><Wand2 :size="16" /></button>
          <button class="action-btn" title="下载到本地" @click="downloadAudio(audio)"><Download :size="16" /></button>
        </div>
      </div>
    </div>
    <div v-else class="empty-state">
      <FolderOpen :size="64" class="empty-icon" />
      <h3>工坊暂无音源</h3>
      <p>点击上方按钮上传你的第一个音源文件</p>
    </div>
    <div v-if="playingId" class="player-bar">
      <div class="player-info"><FileAudio :size="18" /><span class="player-name">{{ currentAudio?.filename }}</span><span class="player-time">{{ formatTime(currentTime) }} / {{ formatTime(duration) }}</span></div>
      <div class="player-controls">
        <button class="player-btn" @click="togglePreview(currentAudio)"><Pause v-if="isPlaying" :size="18" /><Play v-else :size="18" /></button>
        <div class="progress-track" @click="seekAudio($event)"><div class="progress-fill" :style="{ width: progressPercent + '%' }"></div></div>
        <button class="player-btn" @click="stopPreview"><X :size="18" /></button>
      </div>
    </div>
    <audio ref="audioRef" @timeupdate="onTimeUpdate" @loadedmetadata="onLoadedMetadata" @ended="onEnded"></audio>
  </div>
</template>

<script setup>
import { ref, onBeforeUnmount, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Library, Upload, Music, Play, Pause, Download, Plus, Clock, User, HardDrive, FileAudio, FolderOpen, X, Wand2 } from 'lucide-vue-next'
import { fetchMaterials, uploadMaterial } from "../services/api.js"

const audios = ref([])

const router = useRouter()
const fileInputRef=ref(null),audioRef=ref(null),playingId=ref(null),currentAudio=ref(null)
const isPlaying=ref(false),currentTime=ref(0),duration=ref(0),progressPercent=ref(0)

function triggerUpload(){fileInputRef.value?.click()}
onMounted(loadMaterials)

async function loadMaterials(){audios.value=await fetchMaterials("bgm")}
async function handleFilesSelected(e){const files=e.target.files;if(!files||!files.length)return;for(const f of files){const formData=new FormData();formData.append("file",f);audios.value.push(await uploadMaterial(formData))};e.target.value=""}
function togglePreview(audio){if(playingId.value===audio.id){if(isPlaying.value){audioRef.value?.pause();isPlaying.value=false}else{audioRef.value?.play();isPlaying.value=true};return};stopPreview();currentAudio.value=audio;playingId.value=audio.id;const el=audioRef.value;if(!el)return;if(audio.audioUrl){el.src=audio.audioUrl}else{el.src="";return};el.load();el.play().then(()=>{isPlaying.value=true}).catch(()=>{isPlaying.value=false})}
function stopPreview(){const el=audioRef.value;if(el){el.pause();el.currentTime=0};playingId.value=null;currentAudio.value=null;isPlaying.value=false;currentTime.value=0;duration.value=0;progressPercent.value=0}
function onTimeUpdate(){if(audioRef.value){currentTime.value=audioRef.value.currentTime;if(duration.value>0)progressPercent.value=(currentTime.value/duration.value)*100}}
function onLoadedMetadata(){if(audioRef.value&&audioRef.value.duration){duration.value=audioRef.value.duration;if(currentAudio.value&&currentAudio.value.duration===0)currentAudio.value.duration=Math.round(audioRef.value.duration)}}
function onEnded(){isPlaying.value=false;currentTime.value=0;progressPercent.value=0}
function seekAudio(e){if(!audioRef.value||!duration.value)return;const rect=e.currentTarget.getBoundingClientRect();audioRef.value.currentTime=((e.clientX-rect.left)/rect.width)*duration.value}
function addToLibrary(audio){alert("已将 "+audio.filename+" 添加到你的音色库")}
function sendToExtract(audio){localStorage.setItem("extractFile",JSON.stringify({name:audio.filename,format:audio.format,src:audio.audioUrl}));router.push("/extract")}
function downloadAudio(audio){if(audio.audioUrl){const a=document.createElement("a");a.href=audio.audioUrl;a.download=audio.filename;a.click()}else{alert("下载功能需要后端支持")}}
function formatDuration(s){if(!s||s<=0)return"--:--";const m=Math.floor(s/60);return m+":"+String(Math.floor(s%60)).padStart(2,"0")}
function formatTime(s){if(!s||s<=0)return"0:00";const m=Math.floor(s/60);return m+":"+String(Math.floor(s%60)).padStart(2,"0")}
function formatSize(b){if(!b)return"";if(b<1024)return b+" B";if(b<1048576)return(b/1024).toFixed(1)+" KB";return(b/1048576).toFixed(1)+" MB"}
onBeforeUnmount(()=>{stopPreview()})
</script>

<style scoped>
.workshop-page{max-width:1100px;margin:0 auto;padding:32px 24px}
.workshop-header{display:flex;align-items:center;justify-content:space-between;gap:20px;margin-bottom:20px;flex-wrap:wrap}
.header-info h2{font-size:22px;font-weight:700;display:flex;align-items:center;gap:10px;color:var(--text);margin-bottom:4px}
.header-info p{font-size:14px;color:var(--text-secondary)}
.upload-btn{display:flex;align-items:center;gap:8px;padding:12px 24px;background:var(--primary);color:#fff;border:none;border-radius:10px;font-size:15px;font-weight:600;cursor:pointer;transition:transform .15s,box-shadow .15s,background .15s;flex-shrink:0}
.upload-btn:hover{background:var(--primary-hover);transform:translateY(-1px);box-shadow:var(--shadow-md)}
.stats-bar{display:flex;gap:20px;margin-bottom:24px;padding:12px 16px;background:var(--bg-card);border:1px solid var(--border);border-radius:10px}
.stat-item{display:flex;align-items:center;gap:6px;font-size:14px;color:var(--text-secondary)}
.stat-item strong{color:var(--primary)}
.audio-grid{display:grid;gap:12px}
.audio-card{display:flex;align-items:center;gap:16px;background:var(--bg-card);border:1px solid var(--border);border-radius:12px;padding:16px 20px;transition:border-color .2s,box-shadow .2s,background .2s}
.audio-card:hover{border-color:var(--primary);box-shadow:var(--shadow)}
.audio-card.playing{border-color:var(--primary);background:var(--primary-light)}
.audio-icon{position:relative;flex-shrink:0;width:56px;height:56px;background:var(--primary-light);border-radius:10px;display:flex;align-items:center;justify-content:center;color:var(--primary)}
.format-badge{position:absolute;bottom:-4px;right:-8px;background:var(--primary);color:#fff;font-size:10px;font-weight:700;padding:2px 6px;border-radius:4px}
.audio-info{flex:1;min-width:0}
.audio-name{font-size:14px;font-weight:600;color:var(--text);margin-bottom:6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.audio-meta{display:flex;gap:14px;flex-wrap:wrap}
.meta-item{display:flex;align-items:center;gap:4px;font-size:12px;color:var(--text-muted)}
.audio-actions{display:flex;gap:6px;flex-shrink:0}
.action-btn{width:36px;height:36px;border:1px solid var(--border);border-radius:8px;background:var(--bg-card);color:var(--text-secondary);display:flex;align-items:center;justify-content:center;cursor:pointer;transition:all .15s}
.action-btn:hover{border-color:var(--primary);color:var(--primary);background:var(--primary-light)}
.play-btn{width:40px;height:40px;border-radius:50%;background:var(--primary);border:none;color:#fff}
.play-btn:hover{background:var(--primary-hover);color:#fff}
.empty-state{text-align:center;padding:80px 20px;color:var(--text-muted)}
.empty-icon{margin-bottom:16px;opacity:.5}
.empty-state h3{font-size:18px;color:var(--text-secondary);margin-bottom:8px}
.empty-state p{font-size:14px}
.player-bar{position:fixed;bottom:0;left:0;right:0;background:var(--bg-card);border-top:2px solid var(--primary);padding:12px 24px;display:flex;align-items:center;justify-content:space-between;gap:20px;box-shadow:var(--shadow-lg);z-index:200}
.player-info{display:flex;align-items:center;gap:10px;color:var(--text-secondary);font-size:13px;min-width:0}
.player-name{font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:200px}
.player-time{color:var(--text-muted);flex-shrink:0}
.player-controls{display:flex;align-items:center;gap:12px;flex:1;max-width:500px}
.player-btn{width:36px;height:36px;border:none;border-radius:50%;background:var(--primary-light);color:var(--primary);display:flex;align-items:center;justify-content:center;cursor:pointer;transition:background .15s;flex-shrink:0}
.player-btn:hover{background:var(--border-light)}
.progress-track{flex:1;height:6px;background:var(--border-light);border-radius:3px;cursor:pointer;overflow:hidden}
.progress-fill{height:100%;background:var(--primary);border-radius:3px;transition:width .1s linear}
@media(max-width:640px){.workshop-header{flex-direction:column;align-items:flex-start}.audio-meta{gap:8px}.audio-actions{flex-direction:column}.player-bar{flex-direction:column;padding:10px 16px}.player-controls{width:100%}}
</style>
