<template>
  <div class="archive-container">
    
    <!-- 状态：未就绪 -->
    <template v-if="analysisState < 2">
      <div class="empty-state">
        <div class="empty-cover">🎵</div>
        <h2 style="color: #666; margin-top: 15px;">等待信号接入...</h2>
      </div>
    </template>

    <!-- 状态：已就绪 -->
    <template v-else>
      <!-- 头部：导航控制 -->
      <div class="archive-header">
        <div class="archive-badge">{{ currentViewData.isAlbum ? '💿 专辑数字母带' : '🎵 单曲数字档案' }}</div>
        
        <div class="track-navigator" v-if="currentArchive.type === 'album'">
          <button class="nav-arrow" @click="$emit('prev-track')" title="上一曲/总览">◀</button>
          <span class="nav-status">{{ currentViewData.isAlbum ? '总览' : `${currentViewData.track_num} / ${currentArchive.tracks.length}` }}</span>
          <button class="nav-arrow" @click="$emit('next-track')" title="下一曲/总览">▶</button>
        </div>
      </div>
      
      <!-- ================= 档案内容区 ================= -->
      <div class="archive-dossier">
        
        <!-- 左侧：固定大小封面 -->
        <div class="cover-wrapper">
          <img :src="currentViewData.cover" class="archive-cover" alt="Cover" />
        </div>
        
        <!-- 右侧：极其严谨的双列网格区 -->
        <div class="dossier-info">
          
          <!-- 行 1：大标题 (允许换行或滚动) -->
          <div class="title-row">
            <div class="marquee-box">
              <span class="d-value highlight-title marquee-text" :title="currentViewData.title">{{ currentViewData.title }}</span>
            </div>
          </div>
          
          <!-- 行 2：信息网格 (2 列) -->
          <div class="dossier-info-grid">
            
            <div class="grid-item">
              <span class="d-label">ARTIST</span>
              <span class="d-value ellipsis" :title="currentViewData.artist">{{ currentViewData.artist }}</span>
            </div>
            
            <div class="grid-item" v-if="!currentViewData.isAlbum">
              <span class="d-label">ALBUM</span>
              <span class="d-value ellipsis" :title="currentViewData.album">{{ currentViewData.album }}</span>
            </div>
            
            <div class="grid-item" v-if="!currentViewData.isAlbum">
              <span class="d-label">TRACK #</span>
              <span class="d-value tag-track">{{ currentViewData.track_num }}</span>
            </div>
            
            <div class="grid-item" v-if="currentViewData.isAlbum">
              <span class="d-label">TOTAL</span>
              <span class="d-value tag-track">{{ currentViewData.trackCount }} 首</span>
            </div>
            
            <div class="grid-item">
              <span class="d-label">GENRE</span>
              <span class="d-value tag-genre">{{ currentViewData.genre }}</span>
            </div>
            
            <div class="grid-item">
              <span class="d-label">BPM</span>
              <span class="d-value tag-bpm">{{ currentViewData.bpm.toFixed(0) }}</span>
            </div>

            <!-- 🔑 人工校准 (添加保存按钮) -->
            <div class="grid-item full-width" v-if="!currentViewData.isAlbum">
              <div class="correction-row">
                 <span class="d-label" style="color:var(--primary-color)">AI DETECT:</span>
                 <select :value="localGenre" @change="handleGenreChange" class="custom-select-mini">
                   <option v-for="g in availableGenres" :key="g" :value="g">{{ g }}</option>
                 </select>
                 <!-- 🔑 新增：保存按钮 -->
                 <button v-if="isModified" class="save-btn" @click="saveCorrection" :disabled="isSaving">
                   {{ isSaving ? '...' : '💾 覆写基质' }}
                 </button>
              </div>
            </div>

          </div> <!-- 结束网格区 -->
        </div> <!-- 结束详情区 -->
      </div> <!-- 结束内容区 -->

      <!-- ================= 独立区：基因序列 ================= -->
      <div class="dna-section" v-if="analysisState === 3 && !currentViewData.isAlbum">
         <span class="d-label">MFCC SEQUENCE <span style="color:#555; font-size:10px;">[01-20]</span></span>
         <div class="dna-heatmap-wrapper">
            <HeatmapBarcode :mfccVector="currentViewData.mfcc_vector" />
         </div>
      </div>

      <!-- ================= 独立区：百科情报 ================= -->
      <div class="wiki-section custom-scroll" v-if="analysisState >= 2">
        <h4 style="color: #aaa; font-size: 12px; margin: 0 0 8px 0; border-bottom: 1px dashed #333; padding-bottom: 4px;">📡 网络空间情报 (Wiki)</h4>
        <p style="color: #777; font-size: 12px; line-height: 1.5; margin: 0;">
          [预留空间] 后续将通过网络爬虫接入百科数据，动态展示艺术家 ({{ currentViewData.artist }}) 的背景介绍。
        </p>
      </div>

    </template>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import axios from 'axios'
import HeatmapBarcode from './HeatmapBarcode.vue'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const props = defineProps({
  analysisState: Number,
  currentArchive: Object,
  currentViewData: Object,
  availableGenres: { 
    type: Array, 
    default: () => ['Metal', 'MidwestEMO', 'Postpunk', 'PostRock', 'Shoegaze', 'Blues', 'Funk', 'Jazz', 'Reggae', 'ElectronicMusic', 'Unknown'] 
  }
})

const emit = defineEmits(['switch-to-album', 'prev-track', 'next-track', 'update-genre'])

const localGenre = ref('')
const isModified = ref(false)
const isSaving = ref(false)

watch(() => props.currentViewData.genre, (newVal) => {
  localGenre.value = newVal
  isModified.value = false
}, { immediate: true })

const handleGenreChange = (e) => {
  localGenre.value = e.target.value
  isModified.value = (localGenre.value !== props.currentViewData.genre)
}

const saveCorrection = async () => {
  isSaving.value = true
  
  const payload = {
    title: props.currentViewData.title,
    artist: props.currentViewData.artist,
    corrected_genre: localGenre.value
  }
  
  console.log('📡 发送修正请求:', payload)
  
  try {
    const response = await axios.post(`${API_BASE_URL}/api/correct_genre`, payload, {
      headers: { 'Content-Type': 'application/json' }
    })
    
    console.log('✅ 修正成功:', response.data)
    emit('update-genre', localGenre.value)
    isModified.value = false
  } catch (error) {
    console.error('❌ 修正失败:', error)
    const errorDetail = error.response?.data?.detail
    let errorMsg = error.message
    if (errorDetail) {
      if (typeof errorDetail === 'object') {
        errorMsg = `未找到歌曲\n\n请求标题：${errorDetail.requested_title}\nCSV 中标题样例：\n${errorDetail.csv_title_samples?.join('\n')}`
      } else {
        errorMsg = errorDetail
      }
    }
    alert("❌ 修正失败：" + errorMsg)
  } finally {
    isSaving.value = false
  }
}
</script>

<style scoped>
/* 核心防御：强制控制尺寸，绝不允许内容撑破容器 */
.archive-container { 
  display: flex; flex-direction: column; gap: 15px; 
  width: 100%; height: 100%; 
  overflow: hidden; 
}

.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; }
.empty-cover { width: 80px; height: 80px; border-radius: 12px; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; font-size: 30px; }
.title-skeleton { font-size: 18px; color: #555; margin-top: 15px;}

.archive-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px dashed rgba(255,255,255,0.1); padding-bottom: 10px; flex-shrink: 0;}
.archive-badge { font-size: 11px; font-weight: bold; color: var(--primary-color); background: var(--primary-faint); padding: 4px 8px; border-radius: 4px;}
.track-navigator { background: rgba(0,0,0,0.3); border-radius: 20px; padding: 2px 5px; display: flex; align-items: center; gap: 10px; border: 1px solid rgba(255,255,255,0.05);}
.nav-arrow { background: transparent; border: none; color: #888; cursor: pointer; font-size: 14px; padding: 2px 8px; border-radius: 50%; transition: 0.2s;}
.nav-arrow:hover { color: var(--primary-color); background: rgba(255,255,255,0.1); }
.nav-status { font-family: monospace; font-size: 12px; color: #fff; min-width: 60px; text-align: center;}

/* ======== 档案内容区排版 ======== */
.archive-dossier { 
  display: flex; gap: 20px; align-items: flex-start; 
  width: 100%; flex-shrink: 0;
}

.cover-wrapper { flex-shrink: 0; }
.archive-cover { width: 120px; height: 120px; border-radius: 12px; object-fit: cover; box-shadow: 0 5px 20px rgba(0,0,0,0.6); border: 1px solid rgba(255,255,255,0.1); }

.dossier-info { 
  flex: 1; min-width: 0; /* 极限防撑爆关键 */
  display: flex; flex-direction: column; gap: 8px;
}

/* 标题行跑马灯优化 */
.title-row { width: 100%; min-width: 0; }
.highlight-title { font-size: 20px; font-weight: 900; color: var(--primary-color); }
.marquee-box { flex: 1; min-width: 0; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
.marquee-text { display: inline-block; white-space: nowrap; transition: transform 0.2s; }
.marquee-box:hover .marquee-text { animation: scroll-text 4s linear infinite alternate; }
@keyframes scroll-text { 0% { transform: translateX(0); } 100% { transform: translateX(calc(-100% + 200px)); } }

/* 网格排版 */
.dossier-info-grid { 
  display: grid; grid-template-columns: 1fr 1fr; gap: 8px 15px; width: 100%;
}
.grid-item { display: flex; align-items: center; gap: 10px; min-width: 0; }
.full-width { grid-column: 1 / -1; }

.d-label { font-size: 10px; color: var(--text-sub); font-family: monospace; font-weight: bold; flex-shrink: 0; width: 45px;}
.d-value { font-size: 13px; color: var(--text-main); font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}

.tag-genre { font-size: 11px; padding: 2px 6px; border-radius: 4px; font-weight: bold; background: var(--primary-faint); color: var(--primary-color); border: 1px solid var(--border-color); width: max-content;}
.tag-bpm { font-size: 12px; font-weight: bold; color: var(--text-main); font-family: monospace; width: max-content; background: rgba(255,255,255,0.05); padding: 2px 6px; border-radius: 4px;}
.tag-track { font-size: 12px; padding: 2px 6px; border-radius: 4px; font-weight: bold; background: rgba(185,0,255,0.1); color: #B900FF; border: 1px solid #B900FF; font-family: monospace; width: max-content;}

/* 🔑 校准选择框 (您的原有样式 + 保存按钮) */
.correction-row { 
  display: flex; 
  align-items: center; 
  gap: 8px; 
  background: rgba(0,0,0,0.3); 
  padding: 4px 8px; 
  border-radius: 6px; 
  width: fit-content; 
  border: 1px solid rgba(255,255,255,0.05);
}
.custom-select-mini { 
  background: transparent; 
  border: none; 
  color: var(--primary-color); 
  outline: none; 
  font-weight: bold; 
  cursor: pointer; 
  font-size: 12px;
}

/* 🔑 新增：保存按钮样式 */
.save-btn {
  padding: 3px 8px;
  font-size: 11px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  background: var(--primary-color);
  color: #000;
  font-weight: bold;
  white-space: nowrap;
  transition: 0.2s;
  box-shadow: 0 0 8px var(--primary-faint);
}
.save-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}
.save-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* ======== DNA 条形码区 ======== */
.dna-section { flex-shrink: 0; display: flex; flex-direction: column; gap: 5px; margin-top: 5px;}
.dna-label { font-size: 10px; color: var(--primary-color); font-family: monospace; font-weight: bold;}
.dna-heatmap-wrapper { width: 100%; height: 35px; border-radius: 4px; overflow: hidden; border: 1px solid rgba(255,255,255,0.1); }

/* ======== 百科情报区 ======== */
.wiki-section { 
  flex: 1; /* 占据剩余的所有纵向空间 */
  min-height: 80px; 
  background: rgba(0,0,0,0.2); 
  border-radius: 8px; 
  padding: 12px; 
  overflow-y: auto; 
}
.custom-scroll::-webkit-scrollbar { width: 4px; }
.custom-scroll::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }
</style>