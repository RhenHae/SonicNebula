<script setup>
import { ref } from 'vue'
import FileUpload from '../FileUpload.vue'

// 核心状态：0-上传, 1-准备, 2-处理中, 3-完成
const fileState = ref(0)
const selectedFile = ref(null)
const processProgress = ref(0)

// 🎶 新增了吉他轨，共 5 轨
const tracks = ref([
  { name: '人声 (Vocals)', color: '#FF003C', muted: false },
  { name: '吉他 (Guitar)', color: '#00F0FF', muted: false }, // 新增
  { name: '鼓点 (Drums)', color: '#00FFCC', muted: false },
  { name: '贝斯 (Bass)', color: '#FCEE0A', muted: false },
  { name: '其他 (Other)', color: '#B900FF', muted: false }
])

const onFileReceived = (file) => {
  const sizeMB = (file.size / (1024 * 1024)).toFixed(2)
  selectedFile.value = { name: file.name, size: `${sizeMB} MB` }
  fileState.value = 1
}

const startProcess = () => {
  fileState.value = 2
  processProgress.value = 0
  const interval = setInterval(() => {
    processProgress.value += 5
    if (processProgress.value >= 100) {
      clearInterval(interval)
      fileState.value = 3
    }
  }, 100)
}

const reset = () => { 
  fileState.value = 0
  selectedFile.value = null
  processProgress.value = 0 
}

// 🚀 【关键修复】：暴露 fileState 供父组件的防呆拦截器读取！
defineExpose({ fileState, reset })
</script>

<template>
  <div class="studio-module">
    <div class="workbench-header">
      <!-- 文案通俗化 -->
      <h3>🎛️ 音轨分离提取 (Stem Split)</h3>
      <button v-if="fileState > 0" class="btn outline" @click="reset">🗑️ 清空重置</button>
    </div>

    <!-- 状态 0: 上传 -->
    <div v-if="fileState === 0" class="upload-zone-wrapper">
      <div style="width: 60%">
        <FileUpload title="导入音频文件" subtitle="支持 MP3, WAV, FLAC (最大 50MB)" @file-selected="onFileReceived" />
      </div>
    </div>

    <!-- 状态 1: 准备 -->
    <div v-if="fileState === 1" class="upload-zone-wrapper">
      <div class="file-ready-box">
        <div class="upload-icon" style="color: #00FFCC">🎵</div>
        <h4 style="color: #00FFCC">{{ selectedFile.name }}</h4>
        <p>文件大小: {{ selectedFile.size }} | 状态: 准备就绪</p>
      </div>
      <button class="btn primary btn-large" style="margin-top:20px" @click="startProcess">🚀 开始分离音轨</button>
    </div>

    <!-- 状态 2: 处理中 -->
    <div v-if="fileState === 2" class="processing-zone">
      <div class="radar-spinner"></div>
      <h3 style="color: #00FFCC;">AI 正在拆解音频...</h3>
      <div class="progress-bar"><div class="progress-fill" :style="{ width: processProgress + '%' }"></div></div>
      <span class="progress-text">{{ processProgress }}%</span>
    </div>

    <!-- 状态 3: 结果 -->
    <div v-if="fileState === 3" class="result-zone">
      <!-- 使用 flex: 1 均分高度，绝不出现滚动条 -->
      <div class="tracks-container">
        <div class="track-row" v-for="(track, index) in tracks" :key="index">
          <div class="track-controls">
            <span class="track-name" :style="{ color: track.color }">{{ track.name }}</span>
            <div class="track-btns">
              <button class="t-btn" :class="{ active: track.muted }" @click="track.muted = !track.muted">M</button>
              <button class="t-btn">S</button>
              <button class="t-btn dl-btn" title="下载此轨道">⬇</button>
            </div>
          </div>
          <div class="track-waveform" :style="{ opacity: track.muted ? 0.2 : 1 }">
            <div class="fake-wave-bar" v-for="i in 100" :key="i" :style="{ height: 10+Math.random()*90+'%', backgroundColor: track.color }"></div>
          </div>
        </div>
      </div>
      <div class="result-actions">
        <button class="btn primary">▶ 播放全部</button>
        <button class="btn outline">📦 一键打包下载 (ZIP)</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import '../../styles/studio-module.css';

/* 🎯 高度自适应优化：让 5 个音轨完美塞进容器，不溢出 */
.tracks-container { 
  display: flex; 
  flex-direction: column; 
  gap: 8px; /* 减小间距 */
  flex: 1; 
  overflow: hidden; /* 绝对禁止滚动 */
}
.track-row { 
  flex: 1; /* 5个轨道均分剩余高度 */
  min-height: 0; /* 防止内容撑破 flex 容器 */
  display: flex; 
  background: rgba(0,0,0,0.4); 
  border-radius: 8px; 
  align-items: center; 
  border: 1px solid rgba(255,255,255,0.05); 
  padding: 5px 15px; /* 减小内边距 */
}
</style>