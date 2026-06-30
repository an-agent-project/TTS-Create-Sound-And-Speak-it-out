<template>
  <div class="card voice-card" >
    <div class="voice-top">
      <div class="voice-avatar" :class="voice.gender">
        <User v-if="voice.gender === 'male'" :size="24" />
        <User v-else-if="voice.gender === 'female'" :size="24" />
        <Baby v-else :size="24" />
      </div>
      <div class="voice-info">
        <h4 class="voice-name">{{ voice.name }} <span v-if="voice.fromPublic" class="badge-public">公共库</span></h4>
        <div class="voice-meta">
          <span v-for="(tag, i) in editableTags" :key="i" class="tag tag-primary tag-editable" @click.stop="startEditTag(i)">
            {{ tag }}
            <X v-if="editing && editingIdx !== i" :size="10" class="tag-remove" @click.stop="removeTag(i)" />
          </span>
          <button v-if="editing && editableTags.length < 5" class="tag tag-add" @click.stop="addTag">+</button>
        </div>
        <div v-if="editing && editingIdx >= 0" class="tag-edit-row">
          <input v-model="editTagValue" placeholder=输入标签 @keyup.enter="saveTag" class="tag-input" />
          <button class="btn btn-primary btn-xs" @click="saveTag">确定</button>
          <button class="btn btn-secondary btn-xs" @click="editingIdx = -1">取消</button>
        </div>
      </div>
      <button class="fav-btn" :class="{ active: isFavorite }" @click.stop="emit('toggleFavorite')">
        <Star v-if="isFavorite" :size="20" fill="var(--warning)" color="var(--warning)" />
        <Heart v-else :size="20" />
      </button>
    </div>
    <p class="voice-desc">{{ voice.description }}</p>
    <div class="voice-actions">
      <button v-if="showPreview" class="btn btn-secondary btn-sm btn-block" @click.stop="emit('preview')">
        <Play :size="14" /> 试听</button>
      <button v-if="showSelect" class="btn btn-primary btn-sm btn-block" @click.stop="emit('select')">
        选择此音色</button>
      <button v-if="showClone" class="btn btn-accent btn-sm btn-block" :disabled="cloneDisabled" @click.stop="emit('clone')">
        <FolderPlus :size="14" /> {{ cloneLabel || '存入我的音色库' }}
      </button>
      <div v-if="manageMode" class="manage-actions">
        <button class="btn btn-outline btn-sm" @click.stop="toggleEdit">
          <Settings2 :size="14" /> {{ editing ? '取消' : '编辑标签' }}
        </button>
        <button
          class="btn btn-danger btn-sm"
          :disabled="voice.isSystemVoice"
          :title="'\u7cfb\u7edf\u9ed8\u8ba4\u97f3\u8272\u4e0d\u53ef\u5220\u9664'"
          @click.stop="!voice.isSystemVoice && emit('deleteVoice')"
        >
          <Trash2 :size="14" /> {{ voice.isSystemVoice ? "\u9ed8\u8ba4\u97f3\u8272" : "\u5220\u9664" }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { User, Baby, Star, Heart, Play, X, Trash2, Settings2, FolderPlus } from 'lucide-vue-next'

const props = defineProps({
  voice: { type: Object, required: true },
  isFavorite: { type: Boolean, default: false },
  showPreview: { type: Boolean, default: true },
  showSelect: { type: Boolean, default: false },
  manageMode: { type: Boolean, default: false },
  showClone: { type: Boolean, default: false },
  cloneLabel: { type: String, default: '存入我的音色库' },
  cloneDisabled: { type: Boolean, default: false },
})
const emit = defineEmits(['toggleFavorite', 'preview', 'select', 'deleteVoice', 'updateTags', 'clone'])

const editing = ref(false)
const editingIdx = ref(-1)
const editTagValue = ref('')
const editableTags = computed(() => [...(props.voice.tags || [props.voice.style, props.voice.category].filter(Boolean))])

function toggleEdit() { editing.value = !editing.value; editingIdx.value = -1 }
function startEditTag(i) { if (!editing.value) return; editingIdx.value = i; editTagValue.value = editableTags.value[i] || '' }
function saveTag() {
  if (editingIdx.value < 0) return
  const v = editTagValue.value.trim()
  if (v) {
    const tags = [...editableTags.value]
    if (editingIdx.value < tags.length) tags[editingIdx.value] = v
    else tags.push(v)
    emit('updateTags', tags)
  }
  editingIdx.value = -1; editTagValue.value = ''
}
function removeTag(i) { const tags = [...editableTags.value]; tags.splice(i, 1); emit('updateTags', tags) }
function addTag() { const tags = [...editableTags.value]; tags.push(''); editingIdx.value = tags.length - 1; editTagValue.value = ''; emit('updateTags', tags) }
</script>

<style scoped>
.voice-card { position: relative; padding: 20px; transition: transform 0.2s, box-shadow 0.2s; cursor: pointer; }
.voice-card:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(0,0,0,0.12); }
.btn:disabled { opacity: .55; cursor: not-allowed; }
.voice-card.featured { border-color: var(--primary); background: linear-gradient(135deg, #fff 0%, var(--primary-light) 100%); }
.voice-top { display: flex; align-items: flex-start; gap: 12px; margin-bottom: 12px; }
.voice-avatar { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.voice-avatar.male { background: #d1fae5; color: #059669; }
.voice-avatar.female { background: #fce7f3; color: #ec4899; }
.voice-avatar.child { background: #fef3c7; color: #f59e0b; }
.voice-info { flex: 1; min-width: 0; }
.voice-name { font-size: 16px; font-weight: 700; margin-bottom: 6px; }
.badge-public { display: inline-block; font-size: 11px; font-weight: 500; background: #dbeafe; color: #3b82f6; padding: 1px 7px; border-radius: 4px; margin-left: 6px; vertical-align: middle; }
.voice-meta { display: flex; gap: 4px; flex-wrap: wrap; align-items: center; }
.voice-desc { font-size: 13px; color: var(--text-secondary); line-height: 1.5; margin-bottom: 14px; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
.voice-actions { display: flex; flex-direction: column; gap: 8px; }
.fav-btn { background: none; padding: 4px; border-radius: 50%; flex-shrink: 0; transition: transform var(--transition); color: var(--text-muted); border: none; cursor: pointer; }
.fav-btn:hover { transform: scale(1.2); }
.fav-btn.active { color: var(--warning); }
.tag-editable { cursor: pointer; position: relative; padding-right: 4px; }
.tag-editable:hover { opacity: .7; }
.tag-remove { cursor: pointer; margin-left: 2px; opacity: .5; }
.tag-remove:hover { opacity: 1; }
.tag-add { border: 1px dashed var(--primary); color: var(--primary); background: #fff; cursor: pointer; }
.tag-add:hover { background: var(--primary-light); }
.tag-edit-row { display: flex; gap: 4px; margin-top: 6px; align-items: center; }
.tag-input { flex: 1; padding: 4px 8px; border: 1px solid #d1d5db; border-radius: 4px; font-size: 12px; outline: none; }
.tag-input:focus { border-color: var(--primary); }
.btn-xs { padding: 3px 10px; font-size: 11px; }
.btn-danger { background: #fee2e2; color: #dc2626; border: 1px solid #fecaca; }
.btn-danger:hover { background: #fecaca; }
.btn-outline { background: #fff; color: var(--primary); border: 1px solid var(--primary-light); }
.btn-outline:hover { background: var(--primary-light); }
.manage-actions { display: flex; gap: 6px; }
.btn-accent { background: #ecfdf5; color: #059669; border: 1px solid #a7f3d0; }
.btn-accent:hover { background: #d1fae5; }
.btn-accent:disabled { opacity: .5; cursor: default; }
</style>