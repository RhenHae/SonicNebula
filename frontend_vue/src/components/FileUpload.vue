<script setup>
import { ref } from 'vue'

const props = defineProps({
  title: { type: String, default: '点击或拖拽文件至此' },
  subtitle: { type: String, default: '支持格式: MP3, WAV, FLAC' },
  accept: { type: String, default: '.mp3,.wav,.flac' },
  isDirectory: { type: Boolean, default: false } // 控制是选单文件还是选文件夹
})

const emit = defineEmits(['file-selected', 'folder-selected'])

const fileInputRef = ref(null)
const isDragging = ref(false)

const triggerInput = () => {
  // 每次点击前清空 value，否则选同一个文件不会触发 change
  if (fileInputRef.value) fileInputRef.value.value = ''
  fileInputRef.value.click()
}

const handleFileChange = (e) => {
  const files = e.target.files
  if (!files || files.length === 0) return

  if (props.isDirectory) {
    const validFiles = Array.from(files).filter(file => {
      const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase()
      return props.accept.includes(ext)
    })
    emit('folder-selected', validFiles)
  } else {
    emit('file-selected', files[0])
  }
}

// 拖拽事件处理
const onDragOver = (e) => { e.preventDefault(); isDragging.value = true }
const onDragLeave = (e) => { e.preventDefault(); isDragging.value = false }
const onDrop = (e) => {
  e.preventDefault()
  isDragging.value = false
  const files = e.dataTransfer.files
  if (!files || files.length === 0) return
  
  if (props.isDirectory) {
     // 注意：原生拖拽文件夹获取内容非常复杂，这里为了稳定性，拖拽文件夹时暂做近似处理
     emit('folder-selected', Array.from(files))
  } else {
     emit('file-selected', files[0])
  }
}
</script>

<template>
  <div 
    class="upload-dropzone" 
    :class="{ 'is-dragging': isDragging }"
    @click="triggerInput"
    @dragover="onDragOver"
    @dragleave="onDragLeave"
    @drop="onDrop"
  >
    <input 
      type="file" 
      ref="fileInputRef" 
      :accept="props.accept"
      :webkitdirectory="props.isDirectory"
      :multiple="props.isDirectory"
      style="display: none" 
      @change="handleFileChange"
    >
    <div class="upload-icon" :class="{ 'bounce': isDragging }">📥</div>
    <h4>{{ props.title }}</h4>
    <p>{{ props.subtitle }}</p>
  </div>
</template>

<style scoped>
.upload-dropzone { border: 2px dashed var(--border-color); background: rgba(0, 255, 204, 0.02); width: 100%; height: 180px; border-radius: 12px; display: flex; flex-direction: column; align-items: center; justify-content: center; cursor: pointer; transition: all 0.3s; box-sizing: border-box; padding: 20px;}
.upload-dropzone:hover, .upload-dropzone.is-dragging { border-color: var(--primary-color); background: rgba(0, 255, 204, 0.05); }
.upload-icon { font-size: 36px; margin-bottom: 10px; filter: grayscale(1); transition: 0.3s; }
.upload-dropzone:hover .upload-icon { filter: grayscale(0); transform: scale(1.1); }
.bounce { animation: bounce 0.5s infinite alternate; filter: grayscale(0); }
@keyframes bounce { from { transform: translateY(0); } to { transform: translateY(-10px); } }
h4 { color: var(--text-main); margin: 0 0 5px 0; font-size: 15px; pointer-events: none; }
p { color: var(--text-sub); margin: 0; font-size: 12px; pointer-events: none; text-align: center;}
</style>