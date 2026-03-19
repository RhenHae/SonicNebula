<script setup>
import { ref } from 'vue'
import FileUpload from '../FileUpload.vue'

// 核心状态：0-上传, 1-就绪, 2-转换中, 3-完成
const fileState = ref(0)
const selectedFile = ref(null)
const processProgress = ref(0)

// 转换配置参数
const targetFormat = ref('FLAC')
const targetBitrate = ref('Lossless (16-bit/44.1kHz)')

// 接收文件
const onFileReceived = (file) => {
  const sizeMB = (file.size / (1024 * 1024)).toFixed(2)
  selectedFile.value = { name: file.name, size: `${sizeMB} MB` }
  fileState.value = 1
}

// 模拟格式转换过程
const startProcess = () => {
  fileState.value = 2
  processProgress.value = 0
  const interval = setInterval(() => {
    processProgress.value += 8 // 转换通常比AI模型快
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

// 暴露内部状态给父组件 (AiStudio.vue) 用于防呆拦截
defineExpose({ fileState })
</script>

<template>
  <div class="studio-module">
    <!-- 头部区域 -->
    <div class="workbench-header">
      <h3>格式转换</h3>
      <button v-if="fileState > 0" class="btn outline" @click="reset">🗑️ 清空重置</button>
    </div>

    <!-- ================= 状态 0: 数据注入 ================= -->
    <div v-if="fileState === 0" class="upload-zone-wrapper">
      <div style="width: 60%">
        <FileUpload 
          title="注入待转换的音频信号" 
          subtitle="支持输入: MP3, WAV, AAC, OGG (最大 100MB)" 
          @file-selected="onFileReceived" 
        />
      </div>
    </div>

    <!-- ================= 状态 1: 参数配置与就绪 ================= -->
    <div v-if="fileState === 1" class="upload-zone-wrapper">
      
      <div class="file-ready-box" style="width: 70%;">
        <div class="upload-icon" style="color: var(--primary-color)">🎶</div>
        <h4 style="color: var(--primary-color)">{{ selectedFile.name }}</h4>
        <p>原始体积: {{ selectedFile.size }} | 状态: 校验通过，等待参数下发</p>
        
        <!-- 转换参数面板 -->
        <div class="transcode-settings">
          <div class="setting-row">
            <span class="setting-label">目标封装格式 (Format):</span>
            <div class="toggle-group">
              <span :class="{active: targetFormat==='FLAC'}" @click="targetFormat='FLAC'">FLAC</span>
              <span :class="{active: targetFormat==='WAV'}" @click="targetFormat='WAV'">WAV</span>
              <span :class="{active: targetFormat==='MP3'}" @click="targetFormat='MP3'">MP3</span>
            </div>
          </div>
          
          <div class="setting-row" style="margin-top: 15px;">
            <span class="setting-label">目标位深度/采样率 (Bitrate):</span>
            <select v-model="targetBitrate" class="custom-select">
              <option value="Lossless (16-bit/44.1kHz)">无损标准CD (16-bit/44.1kHz)</option>
              <option value="Hi-Res (24-bit/96kHz)">Hi-Res 高解析 (24-bit/96kHz)</option>
              <option value="320kbps CBR">最高音质 MP3 (320kbps CBR)</option>
            </select>
          </div>
        </div>
      </div>

      <button class="btn primary btn-large" style="margin-top:20px" @click="startProcess">
        ⚙️ 启动 FFmpeg 核心转码
      </button>
    </div>

    <!-- ================= 状态 2: 转码处理中 ================= -->
    <div v-if="fileState === 2" class="processing-zone">
      <!-- 极客风格：音频流转动画 -->
      <div class="transcode-animation">
        <div class="block source-block">Raw Data</div>
        <div class="data-stream">
           <div class="particle" v-for="i in 5" :key="i" :style="{animationDelay: i*0.2+'s'}"></div>
        </div>
        <div class="block target-block">{{ targetFormat }}</div>
      </div>
      
      <h3 style="color: var(--primary-color); margin-top: 30px;">FFmpeg Encoder is running...</h3>
      <p class="progress-text">正在重采样并重新封装音频流...</p>
      <div class="progress-bar"><div class="progress-fill" :style="{ width: processProgress + '%' }"></div></div>
      <span class="progress-text">{{ processProgress }}%</span>
    </div>

    <!-- ================= 状态 3: 转换完成 ================= -->
    <div v-if="fileState === 3" class="result-zone" style="justify-content: center;">
      <div class="conversion-result-box glass-panel">
         <div class="success-icon">✅</div>
         <h3 style="color:var(--primary-color); margin-bottom: 5px;">转码任务已完成</h3>
         
         <div class="result-details">
           <div class="detail-line">
             <span class="label">输入流:</span>
             <span class="value">{{ selectedFile.name }} ({{ selectedFile.size }})</span>
           </div>
           <div class="detail-line">
             <span class="label">输出流:</span>
             <span class="value highlight">SonicNebula_Output.{{ targetFormat.toLowerCase() }}</span>
           </div>
           <div class="detail-line">
             <span class="label">编码参数:</span>
             <span class="value">{{ targetBitrate }}</span>
           </div>
         </div>
         
         <div class="action-row" style="margin-top: 30px;">
           <button class="btn primary btn-large">💾 下载至本地硬盘</button>
           <button class="btn outline" @click="reset" style="margin-left: 15px;">↺ 继续转码</button>
         </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
@import '@/styles/studio-module.css';

/* 转换专属设置面板 */
.transcode-settings {
  margin-top: 25px;
  padding-top: 20px;
  border-top: 1px dashed rgba(255,255,255,0.1);
  text-align: left;
}
.setting-row { display: flex; align-items: center; justify-content: space-between; }
.setting-label { color: var(--text-main); font-size: 14px; font-weight: bold; }
.custom-select { width: 200px; padding: 6px; background: rgba(0,0,0,0.5); color: var(--primary-color); border: 1px solid var(--border-color); border-radius: 6px; outline: none; font-size: 12px; }

/* 炫酷的转码数据流动画 */
.transcode-animation { display: flex; align-items: center; gap: 20px; }
.block { padding: 15px 25px; border-radius: 8px; font-family: monospace; font-weight: bold; letter-spacing: 1px; }
.source-block { background: rgba(255,255,255,0.1); color: #888; border: 1px solid #555; }
.target-block { background: rgba(0,255,204,0.1); color: var(--primary-color); border: 1px solid var(--primary-color); box-shadow: 0 0 15px var(--primary-faint); }
.data-stream { position: relative; width: 150px; height: 4px; background: rgba(255,255,255,0.05); border-radius: 2px; overflow: hidden; }
.particle { position: absolute; top: 0; left: -10px; width: 10px; height: 100%; background: var(--primary-color); box-shadow: 0 0 8px var(--primary-color); animation: streamFlow 1s linear infinite; }
@keyframes streamFlow { 0% { left: -10px; } 100% { left: 100%; } }

/* 转换结果卡片 */
.conversion-result-box {
  width: 60%; margin: 0 auto; text-align: center; padding: 40px;
  border: 1px solid var(--primary-color); background: rgba(0,255,204,0.02);
}
.success-icon { font-size: 50px; margin-bottom: 10px; text-shadow: 0 0 20px rgba(0,255,204,0.5); }
.result-details { margin-top: 25px; text-align: left; background: rgba(0,0,0,0.4); padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); }
.detail-line { display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 14px; }
.detail-line:last-child { margin-bottom: 0; }
.detail-line .label { color: var(--text-sub); }
.detail-line .value { color: var(--text-main); font-weight: bold; }
.detail-line .highlight { color: var(--primary-color); font-family: monospace; }
</style>