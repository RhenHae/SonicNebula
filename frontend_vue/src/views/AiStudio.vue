<script setup>
import { ref } from 'vue'
import { onBeforeRouteLeave } from 'vue-router'
import { store } from '../store.js'
import FileUpload from '../components/FileUpload.vue'

// 模拟 KNN 向量检索返回的最相似的 5 首歌
const knnRecommendations =[
  { id: 101, title: 'Echoes of Silence', artist: 'Explosions in the Sky', genre: 'PostRock', similarity: '98.2%' },
  { id: 102, title: 'Fuzz Dream', artist: 'My Bloody Valentine', genre: 'Shoegaze', similarity: '95.7%' },
  { id: 103, title: 'Midnight City', artist: 'Coldplay', genre: 'Rock', similarity: '91.4%' },
  { id: 104, title: 'Tears in Rain', artist: 'Mono', genre: 'PostRock', similarity: '89.1%' },
  { id: 105, title: 'Steel Pulse', artist: 'Metallica', genre: 'Metal', similarity: '85.5%' }
]

// ==========================================
// 📌 1. 上传与解析状态管理
// ==========================================
// 状态字典：0=等待上传, 1=已选择专辑, 2=解析中, 3=解析完成展示图表
const analysisState = ref(0)
const uploadInfo = ref({ fileCount: 0, folderName: '' })
const parseProgress = ref(0)

// 接收文件夹数据
const handleFolderSelected = (files) => {
  if (files.length === 0) {
    alert("⚠️ 未检测到有效音频文件！")
    return
  }
  // 尝试获取文件夹名称 (取第一个文件的相对路径的根目录)
  const pathParts = files[0].webkitRelativePath ? files[0].webkitRelativePath.split('/') :[]
  uploadInfo.value.folderName = pathParts.length > 1 ? pathParts[0] : '未知专辑'
  uploadInfo.value.fileCount = files.length
  
  analysisState.value = 1
}

// 模拟触发 Spark 解析
const startParsing = () => {
  analysisState.value = 2
  parseProgress.value = 0
  const interval = setInterval(() => {
    parseProgress.value += 10
    if (parseProgress.value >= 100) {
      clearInterval(interval)
      analysisState.value = 3
    }
  }, 200)
}

const resetAnalysis = () => {
  analysisState.value = 0
  uploadInfo.value = { fileCount: 0, folderName: '' }
}

// ==========================================
// 📌 2. 防呆拦截 (保护用户数据)
// ==========================================
onBeforeRouteLeave((to, from, next) => {
  if (analysisState.value > 0) {
    const confirmed = window.confirm("⚠️ 警告：离开此页面将清空当前上传的专辑与分析进度！\n\n确定要离开吗？")
    if (confirmed) {
      resetAnalysis()
      next()
    } else {
      next(false)
    }
  } else {
    next()
  }
})
</script>

<template>
  <div class="analysis-container">
    <div class="core-layout">
      
      <!-- ================= 左侧：信号源深度解析 ================= -->
      <div class="left-panel glass-panel">
        <div class="panel-header">
          <h2 class="primary-text">📡 信号源深度解析</h2>
          <p class="sub-text">实时呈现所选音频的声学基因及元数据</p>
        </div>

        <div class="info-card">
          <h3>🎯 当前锁定: {{ store.activeSong.title }}</h3>
          <div class="metrics-grid">
            <div class="metric"><span>艺术家</span><strong>{{ store.activeSong.artist }}</strong></div>
            <div class="metric"><span>流派象限</span><strong class="primary-text">{{ store.activeSong.genre }}</strong></div>
            <div class="metric"><span>节拍频率</span><strong>{{ store.activeSong.bpm.toFixed(0) }} Hz</strong></div>
          </div>
        </div>

        <!-- 🔌 动态渲染的数据源注入区 -->
        <div class="upload-section">
          <h3>📂 数据源注入 (Data Ingestion)</h3>
          
          <!-- 状态 0：未上传 -->
          <div v-if="analysisState === 0">
            <p class="sub-text">上传本地专辑目录，触发后端 Spark 分布式特征提取引擎。</p>
            <FileUpload 
              title="点击或拖拽专辑文件夹至此" 
              subtitle="自动提取专辑内所有 MP3/WAV/FLAC 文件"
              :isDirectory="true"
              @folder-selected="handleFolderSelected"
            />
          </div>

          <!-- 状态 1：已选择，等待点火 -->
          <div v-else-if="analysisState === 1" class="upload-ready-box">
             <div class="ready-icon">💽</div>
             <h4 class="primary-text">已锁定专辑: {{ uploadInfo.folderName }}</h4>
             <p class="sub-text">成功挂载 {{ uploadInfo.fileCount }} 条音频轨道</p>
             <button class="action-btn primary" @click="startParsing">🚀 启动 Spark 集群解析</button>
             <button class="action-btn outline" @click="resetAnalysis" style="margin-left: 10px;">取消</button>
          </div>

          <!-- 状态 2 & 3：处理中或已完成 -->
          <div v-else class="upload-ready-box">
             <div v-if="analysisState === 2" class="progress-zone">
                <span class="primary-text">Neural Engine Processing... {{ parseProgress }}%</span>
                <div class="progress-bar"><div class="progress-fill" :style="{ width: parseProgress + '%' }"></div></div>
             </div>
             <div v-else>
               <h4 class="primary-text">✅ 专辑解析完成</h4>
               <p class="sub-text">声学特征已入库，右侧视图已更新。</p>
               <button class="action-btn outline" @click="resetAnalysis">↺ 导入新专辑</button>
             </div>
          </div>
        </div>
      </div>

      <!-- ================= 右侧：数据图表与推荐 ================= -->
      <div class="right-panel">
        
        <!-- 状态 0-2 时：显示占位符 -->
        <template v-if="analysisState < 3">
          <div class="chart-card glass-panel" style="flex: 1;">
             <h3 class="primary-text">📊 多维声学特征雷达 (Radar)</h3>
             <div class="chart-placeholder"><span>[等待数据注入] 注入信号源后将在此处渲染对比雷达图</span></div>
          </div>
          <div class="chart-card glass-panel" style="flex: 1;">
             <h3 class="primary-text">🧬 MFCC 频谱基因序列 (Heatmap)</h3>
             <div class="chart-placeholder"><span>[等待数据注入] 注入信号源后将在此处渲染基因热力图</span></div>
          </div>
          <div class="knn-card-panel glass-panel" style="flex: 1;">
            <div class="panel-header flex-header"><h3 class="primary-text">🔗 高维空间向量关联</h3></div>
            <div class="chart-placeholder"><span>[等待数据注入] 基于 ChromaDB 检索潜在偏好曲目</span></div>
          </div>
        </template>

        <!-- 状态 3：解析完成，显示真实图表数据 (这里目前用占位框演示，后期接 ECharts) -->
        <template v-else>
          <div class="chart-card glass-panel" style="flex: 2;">
            <h3 class="primary-text">📊 多维声学特征雷达 (Radar)</h3>
            <div class="chart-placeholder" style="border-color: var(--primary-color);">
              <span class="primary-text">[ ECharts 雷达图已渲染 ]<br>当前专辑与全局流派均值高度吻合</span>
            </div>
          </div>
          
          <div class="chart-card glass-panel" style="flex: 1.5;">
            <h3 class="primary-text">🧬 MFCC 频谱基因序列 (Heatmap)</h3>
            <div class="chart-placeholder" style="border-color: var(--primary-color);">
              <span class="primary-text">[ ECharts 热力图已渲染 ]</span>
            </div>
          </div>

          <div class="knn-card-panel glass-panel" style="flex: 2.5;">
            <div class="panel-header flex-header">
              <h3 class="primary-text">🔗 高维空间向量关联 (KNN Vector Search)</h3>
              <span class="badge">基于 ChromaDB 欧氏距离检索</span>
            </div>
            <p class="sub-text">系统在 21 维声学特征空间中，计算出与 <b>{{ uploadInfo.folderName }}</b> 欧几里得距离最近的 5 个音频节点。</p>
            
            <div class="knn-cards">
              <div class="knn-card" v-for="(song, index) in knnRecommendations" :key="song.id">
                <div class="knn-rank">#{{ index + 1 }}</div>
                <div class="knn-info">
                  <h4>{{ song.title }}</h4>
                  <p>{{ song.artist }}</p>
                  <div class="knn-tags">
                    <span class="tag-genre">{{ song.genre }}</span>
                    <span class="tag-sim">相似度: {{ song.similarity }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
        
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 继承你之前的 CSS，新增上传交互相关样式 */
.analysis-container { width: 100vw; height: 100vh; padding: 80px 40px 20px 40px; box-sizing: border-box; display: flex; flex-direction: column; pointer-events: none; overflow-y: auto; }
.analysis-container::-webkit-scrollbar { display: none; }
.glass-panel { background: var(--panel-bg); backdrop-filter: blur(20px); border: 1px solid var(--border-color); border-radius: 16px; padding: 25px; pointer-events: auto; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3); transition: 0.3s; }

.primary-text { color: var(--primary-color); margin: 0 0 5px 0; }
.sub-text { color: var(--text-sub); font-size: 13px; margin: 0 0 15px 0; }

.core-layout { display: flex; gap: 20px; flex: 1; min-height: 0; }

/* 左侧信息与上传区 */
.left-panel { flex: 4; display: flex; flex-direction: column; gap: 20px; overflow-y: auto; }
.info-card { background: var(--panel-bg); padding: 25px; border-radius: 12px; }
.info-card h3 { margin: 0 0 20px 0; color: var(--text-main); font-size: 18px; }
.metrics-grid { display: flex; gap: 20px; }
.metric { flex: 1; background: var(--bg-color); padding: 20px; border-radius: 10px; display: flex; flex-direction: column; border: 1px solid rgba(255,255,255,0.05); }
.metric span { color: var(--text-sub); font-size: 13px; margin-bottom: 8px; }
.metric strong { color: var(--text-main); font-size: 20px; }

/* 动态上传盒子状态 */
.upload-section { flex: 1; display: flex; flex-direction: column; }
.upload-ready-box { flex: 1; background: rgba(0, 255, 204, 0.05); border: 1px solid var(--primary-color); border-radius: 12px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 20px;}
.ready-icon { font-size: 40px; margin-bottom: 10px; }
.action-btn { padding: 10px 20px; border-radius: 8px; font-weight: bold; cursor: pointer; transition: 0.3s; font-size: 14px; border: none; }
.action-btn.primary { background: var(--primary-color); color: #000; box-shadow: 0 0 15px var(--primary-glow); margin-top: 15px; }
.action-btn.outline { background: transparent; color: var(--text-main); border: 1px solid var(--text-sub); }

.progress-zone { width: 80%; }
.progress-bar { width: 100%; height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden; margin-top: 10px; }
.progress-fill { height: 100%; background: var(--primary-color); transition: width 0.2s linear; box-shadow: 0 0 10px var(--primary-color); }

/* 右侧图表区 */
.right-panel { flex: 6; display: flex; flex-direction: column; gap: 20px; overflow-y: auto; }
.chart-card { display: flex; flex-direction: column; padding: 20px; }
.chart-placeholder { flex: 1; display: flex; align-items: center; justify-content: center; border: 1px dashed var(--border-color); border-radius: 8px; color: var(--text-sub); text-align: center; font-size: 14px; margin-top: 10px; transition: 0.3s; }

/* KNN 面板 */
.knn-card-panel { display: flex; flex-direction: column; padding: 25px; }
.flex-header { display: flex; justify-content: space-between; align-items: center; }
.badge { background: var(--primary-color); color: var(--bg-color); padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
.knn-cards { display: flex; gap: 20px; margin-top: 15px; overflow-x: auto; padding-bottom: 10px; }
.knn-cards::-webkit-scrollbar { height: 6px; }
.knn-cards::-webkit-scrollbar-thumb { background: var(--primary-color); border-radius: 3px; }
.knn-card { flex: 1 1 180px; min-width: 180px; background: var(--bg-color); border: 1px solid var(--border-color); border-radius: 10px; padding: 15px; display: flex; gap: 15px; align-items: center; transition: 0.3s; cursor: pointer; }
.knn-card:hover { transform: translateY(-5px); box-shadow: 0 5px 15px var(--primary-glow); }
.knn-rank { font-size: 24px; font-weight: 900; color: var(--text-sub); opacity: 0.3; font-style: italic; }
.knn-info h4 { margin: 0 0 5px 0; color: var(--text-main); font-size: 15px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; width: 130px; }
.knn-info p { margin: 0 0 10px 0; color: var(--text-sub); font-size: 12px; }
.knn-tags { display: flex; gap: 8px; }
.tag-genre { font-size: 10px; background: var(--bg-color); color: var(--text-sub); padding: 2px 6px; border-radius: 4px; border: 1px solid var(--border-color); }
.tag-sim { font-size: 10px; background: var(--primary-faint); color: var(--primary-color); padding: 2px 6px; border-radius: 4px; border: 1px solid var(--primary-color); }
</style>