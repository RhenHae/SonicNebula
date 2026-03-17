<script setup>
import { store } from '../store.js'

// 模拟 KNN 向量检索返回的最相似的 5 首歌
const knnRecommendations =[
  { id: 101, title: 'Echoes of Silence', artist: 'Explosions in the Sky', genre: 'PostRock', similarity: '98.2%' },
  { id: 102, title: 'Fuzz Dream', artist: 'My Bloody Valentine', genre: 'Shoegaze', similarity: '95.7%' },
  { id: 103, title: 'Midnight City', artist: 'Coldplay', genre: 'Rock', similarity: '91.4%' },
  { id: 104, title: 'Tears in Rain', artist: 'Mono', genre: 'PostRock', similarity: '89.1%' },
  { id: 105, title: 'Steel Pulse', artist: 'Metallica', genre: 'Metal', similarity: '85.5%' }
]
</script>

<template>
  <div class="analysis-container">
    <!-- 顶部核心区 (左右分栏) -->
    <div class="core-layout">
      
      <!-- 左侧：信号深度解析 + 上传区域 -->
      <div class="left-panel glass-panel">
        <div class="panel-header">
          <h2 class="primary-text">📡 信号源深度解析</h2>
          <p class="sub-text">实时呈现所选音频的声学基因及元数据</p>
        </div>

        <!-- 歌曲详细信息卡片 -->
        <div class="info-card">
          <h3>🎯 当前锁定: {{ store.activeSong.title }}</h3>
          <div class="metrics-grid">
            <div class="metric">
              <span>艺术家</span>
              <strong>{{ store.activeSong.artist }}</strong>
            </div>
            <div class="metric">
              <span>流派象限</span>
              <strong class="primary-text">{{ store.activeSong.genre }}</strong>
            </div>
            <div class="metric">
              <span>节拍频率</span>
              <strong>{{ store.activeSong.bpm.toFixed(0) }} Hz</strong>
            </div>
          </div>
        </div>

        <!-- 🔌 上传音频/专辑接口 -->
        <div class="upload-section">
          <h3>📂 数据源注入 (Data Ingestion)</h3>
          <p class="sub-text">上传本地音频文件或专辑目录，触发后端 Spark 分布式特征提取引擎。</p>
          <div class="upload-dropzone">
            <div class="upload-icon">📤</div>
            <p>拖拽音频文件 / 文件夹至此<br><span class="primary-text">或点击浏览本地文件</span></p>
            <span class="support-text">支持 .mp3, .wav, .flac 格式</span>
          </div>
        </div>
      </div>

      <!-- 右侧面板：雷达图、频谱图、KNN推荐区 -->
      <div class="right-panel">
        <!-- 雷达图卡片 -->
        <div class="chart-card glass-panel">
          <h3 class="primary-text">📊 多维声学特征雷达 (Radar)</h3>
          <div class="chart-placeholder">
            <span>[图表挂载区] 将在此处渲染 ECharts 雷达图<br>对比该歌曲与流派均值的六维特征</span>
          </div>
        </div>
        
        <!-- 频谱图卡片 -->
        <div class="chart-card glass-panel">
          <h3 class="primary-text">🧬 MFCC 频谱基因序列 (Heatmap)</h3>
          <div class="chart-placeholder">
            <span>[图表挂载区] 将在此处渲染 20 维 MFCC 阵列热力图</span>
          </div>
        </div>

        <!-- KNN 推荐卡片 -->
        <div class="knn-card-panel glass-panel">
          <div class="panel-header flex-header">
            <h3 class="primary-text">🔗 高维空间向量关联 (KNN Vector Search)</h3>
            <span class="badge">基于 ChromaDB 欧氏距离检索</span>
          </div>
          <p class="sub-text">系统在 21 维声学特征空间中，计算出与当前锁定曲目<b>欧几里得距离最近</b>的 5 个音频节点，推测其为您潜在偏好的音乐。</p>
          
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
      </div>
    </div>
  </div>
</template>

<style scoped>
.analysis-container {
  width: 100vw;
  height: 100vh;
  padding: 80px 40px 20px 40px; /* 避开顶部导航栏 */
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  pointer-events: none;
  overflow-y: auto;
}

.analysis-container::-webkit-scrollbar {
  display: none;
}

/* 玻璃态通用类 */
.glass-panel {
  background: var(--panel-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 25px;
  pointer-events: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  transition: background-color 0.3s, border-color 0.3s;
}

.primary-text {
  color: var(--primary-color);
  margin: 0 0 5px 0;
}

.sub-text {
  color: var(--text-sub);
  font-size: 13px;
  margin: 0 0 15px 0;
}

/* 核心布局：左右分栏 */
.core-layout {
  display: flex;
  gap: 20px;
  flex: 1;
  min-height: 0;
}

/* 左侧面板 */
.left-panel {
  flex: 5;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 0;
  overflow-y: auto;
}

.info-card {
  background: var(--panel-bg);
  padding: 25px;
  border-radius: 12px;
  transition: background-color 0.3s;
}

.info-card h3 {
  margin: 0 0 20px 0;
  color: var(--text-main);
  font-size: 18px;
}

.metrics-grid {
  display: flex;
  gap: 20px;
}

.metric {
  flex: 1;
  background: var(--panel-bg);
  padding: 20px;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  transition: background-color 0.3s;
}

.metric span {
  color: var(--text-sub);
  font-size: 13px;
  margin-bottom: 8px;
}

.metric strong {
  color: var(--text-main);
  font-size: 20px;
}

/* 上传区域 */
.upload-section h3 {
  margin: 0 0 5px 0;
  color: var(--text-main);
  font-size: 16px;
}

.upload-dropzone {
  border: 2px dashed var(--border-color);
  background: var(--panel-bg);
  border-radius: 12px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.upload-dropzone:hover {
  background: var(--primary-faint);
  border-color: var(--primary-color);
}

.upload-icon {
  font-size: 32px;
  margin-bottom: 10px;
}

.support-text {
  font-size: 11px;
  color: var(--text-sub);
  margin-top: 10px;
  display: block;
}

/* 右侧面板 */
.right-panel {
  flex: 5;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 0;
  overflow-y: auto;
}

.chart-card {
  flex: 3;
  display: flex;
  flex-direction: column;
  padding: 20px;
  min-height: 0;
}

.chart-placeholder {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px dashed var(--border-color);
  border-radius: 8px;
  color: var(--text-sub);
  text-align: center;
  font-size: 14px;
  background: transparent;
  margin-top: 10px;
}

/* KNN 卡片面板 */
.knn-card-panel {
  flex: 4;
  display: flex;
  flex-direction: column;
  padding: 25px;
  min-height: 0;
}

.flex-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.badge {
  background: var(--primary-color);
  color: var(--bg-color);
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.knn-cards {
  display: flex;
  gap: 20px;
  margin-top: 15px;
  overflow-x: auto;
  padding-bottom: 10px;
  flex-wrap: wrap;
}

.knn-cards::-webkit-scrollbar {
  height: 6px;
}

.knn-cards::-webkit-scrollbar-thumb {
  background: var(--primary-color);
  border-radius: 3px;
}

.knn-card {
  flex: 1 1 180px;
  min-width: 180px;
  background: var(--panel-bg);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 15px;
  display: flex;
  gap: 15px;
  align-items: center;
  transition: transform 0.2s, border-color 0.2s, background-color 0.3s;
  cursor: pointer;
}

.knn-card:hover {
  transform: translateY(-5px);
  border-color: var(--primary-color);
}

.knn-rank {
  font-size: 24px;
  font-weight: 900;
  color: var(--text-sub);
  opacity: 0.3;
  font-style: italic;
}

.knn-info h4 {
  margin: 0 0 5px 0;
  color: var(--text-main);
  font-size: 15px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 130px;
}

.knn-info p {
  margin: 0 0 10px 0;
  color: var(--text-sub);
  font-size: 12px;
}

.knn-tags {
  display: flex;
  gap: 8px;
}

.tag-genre {
  font-size: 10px;
  background: var(--panel-bg);
  color: var(--text-sub);
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid var(--border-color);
}

.tag-sim {
  font-size: 10px;
  background: var(--primary-faint);
  color: var(--primary-color);
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid var(--primary-color);
}
</style>