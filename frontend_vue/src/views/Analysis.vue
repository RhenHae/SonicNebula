<script setup>
import { ref, computed, nextTick } from 'vue'
import { onBeforeRouteLeave } from 'vue-router'
import axios from 'axios'
import * as echarts from 'echarts'
import FileUpload from '../components/FileUpload.vue'
import ArchiveCard from '../components/analysis/ArchiveCard.vue'
import RadarChart from '../components/analysis/RadarChart.vue'
import ExtraChart from '../components/analysis/ExtraChart.vue'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

// ==========================================
// 📌 1. 核心状态与数据模型
// ==========================================
const analysisState = ref(0)
const parseProgress = ref(0)
const ingestMode = ref('album') 
const uploadInfo = ref({ fileCount: 0, folderName: '', files:[] }) 

const currentArchive = ref({ type: 'none', albumName: '未知', artist: '未知', cover: '', tracks:[] })
const currentViewData = ref({})
const currentTrackIndex = ref(-1)

// 🔑 可用流派列表（与 ArchiveCard 共享）
const availableGenres = ['Metal', 'MidwestEMO', 'Postpunk', 'PostRock', 'Shoegaze', 'Blues', 'Funk', 'Jazz', 'Reggae', 'ElectronicMusic', 'Unknown']

// ==========================================
// 📌 4. 向量检索推荐 (KNN) - 声明提前
// ==========================================
const knnRecommendations = ref([])
const isSearching = ref(false)

// ==========================================
// 📌 2. 文件上传与解析流
// ==========================================
const handleFileUpload = (files, isFolder) => {
  if (!files || files.length === 0) return
  
  currentArchive.value = { type: 'none', albumName: '未知', artist: '未知', cover: '', tracks:[] }
  currentViewData.value = {}
  knnRecommendations.value = []
  
  ingestMode.value = isFolder ? 'album' : 'single'
  uploadInfo.value.files = Array.from(files)
  
  if (isFolder) {
    const pathParts = files[0].webkitRelativePath ? files[0].webkitRelativePath.split('/') : []
    uploadInfo.value.folderName = pathParts.length > 1 ? pathParts[0] : '未知专辑目录'
  } else {
    uploadInfo.value.folderName = files[0].name.replace(/\.[^/.]+$/, "")
  }
  
  uploadInfo.value.fileCount = files.length
  startParsing()
}

const startParsing = async () => {
  if (uploadInfo.value.files.length === 0) return
  
  analysisState.value = 1
  parseProgress.value = 5
  
  const progressTimer = setInterval(() => {
    if (parseProgress.value < 85) parseProgress.value += 2
  }, 400)

  try {
    const formData = new FormData()
    uploadInfo.value.files.forEach(file => {
      formData.append("files", file)
    })

    const res = await axios.post(`${API_BASE_URL}/api/analyze_audio`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    const realTracks = res.data.tracks
    
    clearInterval(progressTimer)
    parseProgress.value = 100
    
    setTimeout(() => {
      const isAlbum = ingestMode.value === 'album'
      currentArchive.value = {
        type: isAlbum ? 'album' : 'single',
        albumName: isAlbum ? realTracks[0].album : realTracks[0].album,
        artist: realTracks[0].artist,
        cover: realTracks[0].cover_url, 
        tracks: realTracks.sort((a, b) => a.trackNum - b.trackNum)
      }
      
      if (isAlbum) switchToAlbumView()
      else switchToTrackView(0)
      
    }, 500)

  } catch (error) {
    clearInterval(progressTimer)
    alert("❌ 信号解析失败，请检查后端 FastAPI 是否在 8000 端口运行！\n" + error)
    resetAnalysis()
  }
}

// ==========================================
// 📌 3. 视图切换逻辑
// ==========================================
const switchToAlbumView = () => {
  currentTrackIndex.value = -1
  const tracks = currentArchive.value.tracks
  const avgBpm = tracks.reduce((sum, t) => sum + t.bpm, 0) / tracks.length
  
  currentViewData.value = {
    isAlbum: true, title: currentArchive.value.albumName, artist: currentArchive.value.artist,
    cover: currentArchive.value.cover, genre: tracks[0].genre, bpm: avgBpm, trackCount: tracks.length,
    radar_vector: tracks[0].radar_vector, genre_avg: tracks[0].genre_avg,
    ai_review: "【专辑分析总览】多维信号已聚合完毕。请点击下方列表查看具体的单曲基因序列与深度特征。"
  }
  analysisState.value = 2
}

const switchToTrackView = (index) => {
  currentTrackIndex.value = index
  currentViewData.value = { ...currentArchive.value.tracks[index], isAlbum: false, cover: currentArchive.value.cover }
  analysisState.value = 3
  fetchRecommendations()
}

const handlePrevTrack = () => {
  if (currentArchive.value.type !== 'album') return
  const total = currentArchive.value.tracks.length
  currentTrackIndex.value = currentTrackIndex.value <= -1 ? total - 1 : currentTrackIndex.value - 1
  if (currentTrackIndex.value === -1) switchToAlbumView()
  else switchToTrackView(currentTrackIndex.value)
}

const handleNextTrack = () => {
  if (currentArchive.value.type !== 'album') return
  const total = currentArchive.value.tracks.length
  currentTrackIndex.value = currentTrackIndex.value >= total - 1 ? -1 : currentTrackIndex.value + 1
  if (currentTrackIndex.value === -1) switchToAlbumView()
  else switchToTrackView(currentTrackIndex.value)
}

const resetAnalysis = () => {
  analysisState.value = 0
  currentArchive.value = { type: 'none', albumName: '未知', artist: '未知', cover: '', tracks:[] }
  currentViewData.value = {}
  currentTrackIndex.value = -1
  knnRecommendations.value = []
}

onBeforeRouteLeave((to, from, next) => {
  if (analysisState.value > 0 && window.confirm("⚠️ 离开此页面将清空当前分析数据！\n确定要离开吗？")) {
    resetAnalysis(); next()
  } else if (analysisState.value === 0) next()
  else next(false)
})

// ==========================================
// 📌 4. 向量检索推荐 (KNN) - 函数实现
// ==========================================
const fetchRecommendations = async () => {
  if (!currentViewData.value.mfcc_vector) {
    console.warn('⚠️ mfcc_vector 不存在')
    knnRecommendations.value = []
    return
  }
  
  if (currentViewData.value.mfcc_vector.length !== 20) {
    console.warn('⚠️ mfcc_vector 长度不对:', currentViewData.value.mfcc_vector.length)
    knnRecommendations.value = []
    return
  }
  
  isSearching.value = true
  try {
    const payload = {
      target_vector: currentViewData.value.mfcc_vector,
      title: currentViewData.value.title,
      artist: currentViewData.value.artist,
      genre: currentViewData.value.genre,  // 🔑 新增：传递当前流派
      limit: 10
    }
    
    console.log('📡 请求推荐:', payload.title, '流派:', payload.genre)
    
    const res = await axios.post(`${API_BASE_URL}/api/recommend`, payload)
    
    console.log('✅ 推荐结果:', res.data.recommendations.length, '首')
    if (res.data.recommendations.length > 0) {
      console.log('📋 第一首推荐:', res.data.recommendations[0])
    }
    
    knnRecommendations.value = res.data.recommendations
  } catch (error) {
    console.error("向量检索失败:", error)
    knnRecommendations.value = []
  } finally {
    isSearching.value = false
  }
}

// ==========================================
// 📌 5. 流派修正与反馈机制 (修复版)
// ==========================================
const saveCorrectionToBackend = async (newGenre) => {
  if (newGenre === currentViewData.value.genre) {
    console.log("⚠️ 流派未变更，跳过保存")
    return
  }
  
  const trackData = currentTrackIndex.value !== -1 
    ? currentArchive.value.tracks[currentTrackIndex.value] 
    : currentViewData.value
  
  if (!trackData || !trackData.title) {
    console.error('❌ 无法获取歌曲数据')
    return
  }
  
  try {
    const payload = {
      title: trackData.title,
      artist: trackData.artist,
      corrected_genre: newGenre
    }
    
    console.log('📡 发送修正:', payload)
    
    const response = await axios.post(`${API_BASE_URL}/api/correct_genre`, payload)
    console.log('✅ 后端响应:', response.data)
    
    // 🔑 1. 更新当前视图
    currentViewData.value.genre = newGenre
    
    // 🔑 2. 更新源数据
    if (currentTrackIndex.value !== -1 && currentArchive.value.tracks[currentTrackIndex.value]) {
      currentArchive.value.tracks[currentTrackIndex.value].genre = newGenre
      currentArchive.value.tracks[currentTrackIndex.value].true_genre = newGenre
    }
    
    // 🔑 3. 等待数据库更新完成
    await new Promise(resolve => setTimeout(resolve, 300))
    
    // 🔑 4. 重新检索推荐（会传递新的流派）
    if (currentViewData.value.mfcc_vector && currentViewData.value.mfcc_vector.length === 20) {
      console.log('🔄 修正后刷新推荐列表，新流派:', newGenre)
      await fetchRecommendations()  // ← 会传递新的 genre
    } else {
      console.warn('⚠️ mfcc_vector 不可用，跳过推荐更新')
    }
    
    console.log(`✅ 流派已更新：${trackData.title} → ${newGenre}`)
    
  } catch (error) {
    console.error("更新流派失败:", error)
    const errorDetail = error.response?.data?.detail
    if (errorDetail && typeof errorDetail === 'object') {
      alert(`❌ 未找到歌曲\n\n请求：${errorDetail.requested_title}\nCSV 样例:\n${errorDetail.csv_title_samples?.slice(0,3).join('\n')}`)
    } else {
      alert("❌ 更新流派失败：" + (errorDetail || error.message))
    }
  }
}
</script>

<template>
  <div class="global-glass-overlay">
    <div class="analysis-container">
      
      <!-- 顶层 Header -->
      <div class="page-header glass-panel-header">
        <div>
          <h1 class="primary-text" style="margin: 0; font-size: 24px;">📡 信号解析控制枢纽</h1>
          <p class="sub-text" style="margin: 5px 0 0 0;">导入音频数据，进行 MFCC 提取与风格推断</p>
        </div>
        <button v-if="analysisState >= 2" class="action-btn outline" @click="resetAnalysis">↺ 终止并清除数据</button>
      </div>

      <!-- 🔑 核心布局：三列结构 (左 4 : 中 3 : 右 3) -->
      <div class="core-layout">
        
        <!-- ================= 左侧 (Flex: 4)：实体数字档案卡 ================= -->
        <div class="left-panel">
          <!-- 🔑 修复：添加 availableGenres prop -->
          <ArchiveCard 
            class="glass-panel" style="flex: 1; min-height: 0;"
            :analysisState="analysisState"
            :currentArchive="currentArchive"
            :currentViewData="currentViewData"
            :availableGenres="availableGenres"
            @switch-to-album="switchToAlbumView"
            @prev-track="handlePrevTrack"
            @next-track="handleNextTrack"
            @update-genre="saveCorrectionToBackend"
          />
          
          <!-- 下方上传坞 -->
          <div class="upload-dock glass-panel" v-if="analysisState < 2">
            <div class="mode-switch flex-row-center">
               <div class="switch-btn" :class="{active: ingestMode === 'single'}" @click="ingestMode = 'single'">单曲注入</div>
               <div class="switch-btn" :class="{active: ingestMode === 'album'}" @click="ingestMode = 'album'">专辑整轨注入</div>
            </div>
            
            <div v-if="analysisState === 0" class="upload-wrapper flex-1">
               <FileUpload 
                 :title="ingestMode === 'album' ? '载入专辑目录' : '载入单曲音频'" 
                 subtitle="拖拽文件至此自动触发解析" 
                 :isDirectory="ingestMode === 'album'" 
                 @folder-selected="f => handleFileUpload(f, true)"
                 @file-selected="f => handleFileUpload([f], false)" 
                 style="height: 100% !important; margin: 0;" 
               />
            </div>
            
            <div v-if="analysisState === 1" class="loading-panel flex-row-center flex-1">
               <div class="radar-spinner"></div>
               <div style="flex:1;">
                 <div style="color:var(--primary-color); font-weight:bold; font-size:14px; margin-bottom: 8px;">DSP Engine Running... {{ parseProgress }}%</div>
                 <div class="progress-bar"><div class="progress-fill" :style="{ width: parseProgress + '%' }"></div></div>
               </div>
            </div>
          </div>
        </div>

        <!-- ================= 中间 (Flex: 3)：图表 + AI 分析区 ================= -->
        <div class="center-panel">
          
          <!-- Row 1: 图表区 -->
          <div class="chart-row">
            <div class="chart-card glass-panel flex-col radar-card">
               <h4 class="box-title">📊 多维声学特征标定</h4>
               <div v-if="analysisState < 2" class="chart-placeholder">等待信号...</div>
               <RadarChart v-else :currentVector="currentViewData.radar_vector" :avgVector="currentViewData.genre_avg" :genreName="currentViewData.genre" />
            </div>
            <div class="chart-card glass-panel flex-col extra-card">
               <h4 class="box-title">📈 {{ currentViewData.isAlbum ? '专辑动能走势' : '频域能量分布' }}</h4>
               <div v-if="analysisState < 2" class="chart-placeholder">等待信号...</div>
               <ExtraChart v-else :isAlbum="currentViewData.isAlbum" :bpmList="currentArchive.tracks.map(t=>t.bpm)" />
            </div>
          </div>

          <!-- Row 2: AI 简评 -->
          <div class="ai-review-row glass-panel flex-col">
             <div class="flex-row-between flex-shrink-0" style="margin-bottom: 10px;">
               <h4 class="box-title" style="margin:0;">🤖 LLM 智能听感分析</h4>
               <span class="badge">Model: DeepSeek V1 8B</span>
             </div>
             <div v-if="analysisState < 2" class="chart-placeholder" style="border: none; margin-top:0;">等待模型推理...</div>
             <div v-else class="review-content flex-1 custom-scroll">
               <p style="margin: 0;">{{ currentViewData.ai_review }}</p>
             </div>
          </div>
        </div>

        <!-- ================= 右侧 (Flex: 3)：推荐列表 ================= -->
        <div class="right-panel">
          <div class="recommendations-box glass-panel flex-col">
            <div class="rec-header flex-row-between flex-shrink-0">
              <h4 class="box-title" style="margin:0;">🔗 近似最近邻检索推荐</h4>
              <span class="badge" style="background: rgba(0,255,204,0.1); color: var(--primary-color);">
                {{ currentViewData.isAlbum ? '推荐相似专辑' : '推荐同频单曲' }}
              </span>
            </div>
            
            <div v-if="analysisState < 2" class="chart-placeholder" style="border: none; margin-top:10px;">需先完成音频解析方可触发检索</div>
            <div v-else-if="isSearching" class="chart-placeholder" style="border: none; margin-top:10px; color: var(--primary-color);">📡 正在连接 ChromaDB...</div>
            
            <!-- 🎵 网易云歌单式列表 -->
            <div v-else class="rec-list flex-1 custom-scroll">
              <div 
                class="rec-item flex-row-center" 
                v-for="(rec, index) in knnRecommendations" :key="rec.id">
                
                <!-- 第 1 列：专辑封面 -->
                <div class="rec-cover-cell flex-shrink-0">
                  <img 
                    :src="rec.cover_url || 'https://ui-avatars.com/api/?name=No+Cover&background=1a1a2e&color=666&size=100'" 
                    class="rec-cover-img" 
                    alt="cover"
                    loading="lazy"
                    @error="e => e.target.src = 'https://ui-avatars.com/api/?name=No+Cover&background=1a1a2e&color=666&size=100'"
                  />
                  <div class="rec-similarity">{{ rec.similarity }}</div>
                </div>
                
                <!-- 第 2 列：歌曲信息 -->
                <div class="rec-info-cell flex-1">
                  <div class="rec-title-row ellipsis" :title="rec.title">{{ rec.title }}</div>
                  <div class="rec-artist-row ellipsis" :title="rec.artist">{{ rec.artist }}</div>
                </div>
                
                <!-- 第 3 列：专辑名称 -->
                <div class="rec-album-cell ellipsis" :title="rec.album || '未知专辑'">
                  {{ rec.album || '未知专辑' }}
                </div>
                
              </div>
              
              <div v-if="!isSearching && knnRecommendations.length === 0 && analysisState >= 2" style="color: var(--text-sub); width:100%; text-align:center; display: flex; align-items: center; justify-content: center; padding: 40px 0;">
                未匹配到高相似度轨迹。
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
/* Header 与按钮 */
.page-header { pointer-events: auto; display: flex; justify-content: space-between; align-items: center; padding: 15px 20px; flex-shrink: 0;}
.action-btn { pointer-events: auto; cursor: pointer; padding: 8px 16px; border-radius: 6px; font-size: 13px; font-weight: bold; transition: 0.2s; background: transparent; border: 1px solid var(--primary-color); color: var(--primary-color); }
.action-btn:hover { background: var(--primary-faint); transform: translateY(-2px); }
.action-btn.outline { background: transparent; border: 1px solid rgba(255, 100, 100, 0.5); color: #ff6464; }
.action-btn.outline:hover { background: rgba(255, 100, 100, 0.1); border-color: #ff6464; }

/* 主容器 */
.analysis-container { width: 100vw; height: 100vh; padding: 75px 30px 20px 30px; box-sizing: border-box; display: flex; flex-direction: column; gap: 20px; background: transparent !important; pointer-events: none; overflow: hidden; }
.core-layout { display: flex; gap: 20px; flex: 1; min-height: 0; }

/* 左侧面板 */
.left-panel { flex: 4; display: flex; flex-direction: column; gap: 15px; height: 100%; min-height: 0; pointer-events: auto; }
.upload-dock { height: 220px; flex-shrink: 0; display: flex; flex-direction: column; }
.mode-switch { display: flex; background: rgba(0,0,0,0.4); border-radius: 8px; padding: 4px; margin-bottom: 10px; flex-shrink: 0; }
.switch-btn { flex: 1; text-align: center; padding: 6px; font-size: 12px; color: #888; cursor: pointer; border-radius: 6px; transition: 0.3s; font-weight: bold; }
.switch-btn.active { background: var(--primary-faint); color: var(--primary-color); }
.upload-wrapper :deep(.upload-dropzone) { height: 130px; padding: 15px; }
.loading-panel { display: flex; align-items: center; gap: 20px; padding: 15px; flex: 1; }

/* 中间面板 */
.center-panel { flex: 3; display: flex; flex-direction: column; gap: 15px; height: 100%; min-height: 0; pointer-events: auto; }
.chart-row { display: flex; gap: 15px; flex: 0 0 auto; min-height: 200px; }
.chart-card { flex: 1; display: flex; flex-direction: column; padding: 15px; box-sizing: border-box; min-width: 0; }
.chart-placeholder { flex: 1; display: flex; align-items: center; justify-content: center; border: 1px dashed rgba(255,255,255,0.1); border-radius: 8px; color: #666; font-size: 13px; margin-top: 10px; min-height: 0; }
.ai-review-row { flex: 1; display: flex; flex-direction: column; min-height: 0; padding: 15px; }
.review-content { flex: 1; background: rgba(0,255,204,0.05); border: 1px solid rgba(0,255,204,0.1); border-radius: 8px; padding: 15px; overflow-y: auto; color: #ddd; font-size: 13px; line-height: 1.6; text-align: justify; min-height: 0; }

/* 右侧面板 - 推荐列表 */
.right-panel { flex: 3; display: flex; flex-direction: column; height: 100%; min-height: 0; pointer-events: auto; min-width: 0; }
.recommendations-box { flex: 1; display: flex; flex-direction: column; padding: 15px; min-height: 0; min-width: 0; overflow: hidden; }
.rec-header { padding-bottom: 12px; border-bottom: 1px solid rgba(255, 255, 255, 0.5); flex-shrink: 0; min-width: 0; }
.rec-list { flex: 1; overflow-y: auto; overflow-x: hidden; display: flex; flex-direction: column; gap: 10px; padding-right: 5px; margin-top: 15px; min-height: 0; min-width: 0; width: 100%; }
.rec-list::-webkit-scrollbar { width: 4px; }
.rec-list::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 2px; }

/* 推荐项 */
.rec-item { display: flex; align-items: center; gap: 12px; padding: 10px 12px; border-radius: 8px; background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.05); transition: 0.2s; cursor: pointer; min-width: 0; width: 94%; max-width: 95%; flex-shrink: 1; }
.rec-item:hover { background: rgba(0,255,204,0.08); border-color: rgba(0,255,204,0.3); transform: translateX(3px); }
.rec-cover-cell { position: relative; width: 48px; height: 48px; flex-shrink: 0; flex-grow: 0; border-radius: 6px; overflow: hidden; min-width: 48px; }
.rec-cover-img { width: 100%; height: 100%; object-fit: cover; display: block; }
.rec-similarity { position: absolute; bottom: 0; left: 0; right: 0; background: rgba(0,0,0,0.75); color: var(--primary-color); font-size: 9px; font-weight: bold; text-align: center; padding: 2px 0; font-family: monospace; }

/* 🔑 修复：歌名与专辑名 50:50 平分 */
.rec-info-cell { flex: 1 1 0; min-width: 0; display: flex; flex-direction: column; justify-content: center; gap: 3px; overflow: hidden; }
.rec-title-row { font-size: 14px; font-weight: bold; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; min-width: 0; }
.rec-artist-row { font-size: 11px; color: #888; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; min-width: 0; }
.rec-album-cell { flex: 1 1 0; min-width: 0; font-size: 11px; color: #666; text-align: right; padding-right: 5px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }

/* 辅助类 */
.flex-col { display: flex; flex-direction: column; }
.flex-row-between { display: flex; justify-content: space-between; align-items: center; }
.flex-row-center { display: flex; align-items: center; gap: 10px; }
.flex-1 { flex: 1; min-height: 0; min-width: 0; }
.flex-shrink-0 { flex-shrink: 0; }
.ellipsis { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
</style>