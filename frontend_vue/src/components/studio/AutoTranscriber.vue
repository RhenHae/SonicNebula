<script setup>
import { ref } from 'vue'
import FileUpload from '../FileUpload.vue'

const fileState = ref(0)
const selectedFile = ref(null)
const processProgress = ref(0)
const mockChords =['Cmaj7', 'Am9', 'Dm7', 'G13', 'E7', 'Am']

const onFileReceived = (file) => {
  const sizeMB = (file.size / (1024 * 1024)).toFixed(2)
  selectedFile.value = { name: file.name, size: `${sizeMB} MB` }
  fileState.value = 1
}

const startProcess = () => {
  fileState.value = 2
  processProgress.value = 0
  const interval = setInterval(() => {
    processProgress.value += 10
    if (processProgress.value >= 100) {
      clearInterval(interval)
      fileState.value = 3
    }
  }, 150)
}

const reset = () => { fileState.value = 0; selectedFile.value = null; processProgress.value = 0 }

defineExpose({ fileState, reset })
</script>

<template>
  <div class="studio-module">
    <div class="workbench-header">
      <!-- 文案通俗化 -->
      <h3>AI 自动生成乐谱</h3>
      <button v-if="fileState > 0" class="btn outline" @click="reset">🗑️ 清空重置</button>
    </div>

    <div v-if="fileState === 0" class="upload-zone-wrapper">
      <div style="width: 60%">
        <FileUpload title="导入需要扒谱的音频" subtitle="建议上传纯人声或吉他/钢琴独奏，准确率更高" @file-selected="onFileReceived" />
      </div>
    </div>

    <div v-if="fileState === 1" class="upload-zone-wrapper">
      <div class="file-ready-box">
        <h4 style="color: #00FFCC">{{ selectedFile.name }}</h4>
        <p>状态: 已锁定，准备识别音高与和弦</p>
      </div>
      <button class="btn primary btn-large" style="margin-top:20px" @click="startProcess">🚀 开始生成乐谱</button>
    </div>

    <div v-if="fileState === 2" class="processing-zone">
      <div class="radar-spinner"></div>
      <h3 style="color: #00FFCC;">AI 正在听音识谱...</h3>
      <div class="progress-bar"><div class="progress-fill" :style="{ width: processProgress + '%' }"></div></div>
    </div>

    <div v-if="fileState === 3" class="result-zone">
      <div class="transcription-container">
        <!-- 乐谱预览区 -->
        <div class="piano-roll-mock">
          <div class="midi-note" v-for="i in 20" :key="i" :style="{ left: i*5+'%', top: Math.random()*80+'%', width: Math.random()*10+2+'%' }"></div>
        </div>
        <!-- 实时和弦 -->
        <div class="chord-tracker glass-panel">
          <h4 style="margin:0 0 10px 0; color: #fff;">识别出的吉他/钢琴和弦</h4>
          <div class="chord-ribbon"><div class="chord-block" v-for="(c, i) in mockChords" :key="i">{{ c }}</div></div>
        </div>
        <!-- AI 建议 -->
        <div class="ai-review">
          <h4 style="margin:0 0 10px 0; color: #fff;">AI 扒谱助手提示</h4>
          <p>这首歌的主调是 <b>C大调</b>，和弦走向采用了经典的 <code>6-4-1-5</code> (Am-F-C-G)。建议您下载 MIDI 文件导入到打谱软件 (如 Guitar Pro 或 Logic Pro) 中进行细节微调。</p>
        </div>
      </div>
      <div class="result-actions">
        <button class="btn primary">▶ 播放试听</button>
        <button class="btn outline">🎼 下载 MIDI 格式 (.mid)</button>
        <button class="btn outline">📄 下载 PDF 曲谱</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import '../../styles/studio-module.css';
</style>