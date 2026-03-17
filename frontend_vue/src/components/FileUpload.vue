<script setup>
import { ref } from 'vue'

const props = defineProps({
  title: { type: String, default: '点击或拖拽文件至此' },
  subtitle: { type: String, default: '支持格式: MP3, WAV, FLAC' },
  accept: { type: String, default: '.mp3,.wav,.flac' },
  isDirectory: { type: Boolean, default: false } // 新增：是否开启文件夹上传模式
})

// emit: 如果是单文件，返回 File 对象；如果是文件夹，返回 FileList 数组
const emit = defineEmits(['file-selected', 'folder-selected'])

const fileInputRef = ref(null)
const isDragging = ref(false)

const triggerInput = () => fileInputRef.value.click()

const handleFileChange = (e) => {
  const files = e.target.files
  if (!files || files.length === 0) return

  if (props.isDirectory) {
    // 文件夹模式：过滤出支持的音频文件
    const validFiles = Array.from(files).filter(file => {
      const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase()
      return props.accept.includes(ext)
    })
    emit('folder-selected', validFiles)
  } else {
    // 单文件模式
    emit('file-selected', files[0])
  }
  
  e.target.value = '' // 清空状态，允许重复传
}

// 拖拽事件（文件夹拖拽稍微复杂，这里统一做视觉反馈，实际获取数据靠 input）
const onDragOver = (e) => { e.preventDefault(); isDragging.value = true }
const onDragLeave = (e) => { e.preventDefault(); isDragging.value = false }
const onDrop = (e) => {
  e.preventDefault()
  isDragging.value = false
  const files = e.dataTransfer.files
  if (!files || files.length === 0) return
  
  // 对于拖拽，我们这里做一个简单的回退处理：拖啥就返回啥
  if (props.isDirectory) {
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
    <!-- 动态决定是否加上 webkitdirectory 和 multiple -->
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
/* 继承你主题的变量 */
.upload-dropzone {
  border: 2px dashed var(--border-color); 
  background: var(--panel-bg);
  width: 100%; height: 200px; border-radius: 12px; /* 高度调小一点，适应分析页 */
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  cursor: pointer; transition: all 0.3s; box-sizing: border-box;
}
.upload-dropzone:hover, .upload-dropzone.is-dragging { 
  border-color: var(--primary-color); background: var(--primary-faint); 
}
.upload-icon { font-size: 40px; margin-bottom: 10px; filter: grayscale(1); transition: 0.3s; }
.upload-dropzone:hover .upload-icon { filter: grayscale(0); transform: scale(1.1); }
.bounce { animation: bounce 0.5s infinite alternate; filter: grayscale(0); }
@keyframes bounce { from { transform: translateY(0); } to { transform: translateY(-10px); } }
h4 { color: var(--text-main); margin: 0 0 5px 0; font-size: 16px; pointer-events: none; }
p { color: var(--text-sub); margin: 0; font-size: 12px; pointer-events: none; }
</style>