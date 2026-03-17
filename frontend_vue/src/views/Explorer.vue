<script setup>
import { ref } from 'vue'
import { store } from '../store.js'

// 控制灵动岛展开/收起的状态
const isExpanded = ref(false)

const warpToRandom = () => {
  // 留给 FastAPI 的接口
  alert("正在连接 ChromaDB 向量库获取下一首推荐...")
}

const toggleExpand = () => {
  isExpanded.value = !isExpanded.value
}
</script>

<template>
  <div class="view-container">
    
    <!-- 动态绑定展开类名来控制 CSS 动画 -->
    <div class="island-wrapper" :class="{ 'is-expanded': isExpanded }">
      <div class="giant-island">
        
        <!-- 上半部：核心常驻信息 -->
        <div class="island-main">
          <!-- 左侧波形封面 -->
          <div class="island-leading">
            <div class="waveform-box">
               <div v-for="i in 8" :key="i" class="wave-bar" :style="{animationDelay: i*0.1+'s'}"></div>
            </div>
            <div class="art-placeholder">🎵</div>
          </div>

          <!-- 中间基础信息 -->
          <div class="island-body">
            <div class="info-header">
              <span class="ai-badge">📅 每日推荐</span>
              <span class="card-tag">{{ store.activeSong.genre }}</span>
            </div>
            <h4 class="song-title">{{ store.activeSong.title }}</h4>
            <p class="artist-name">{{ store.activeSong.artist }} <span class="bpm-mark">// {{ store.activeSong.bpm.toFixed(0) }} BPM</span></p>
          </div>

          <!-- 右侧操作区 -->
          <div class="island-trailing">
            <button class="action-btn warp-btn" @click="warpToRandom">✨ 探索下一首</button>
            
            <!-- 展开/收起触发按钮 -->
            <button class="expand-btn" @click="toggleExpand" :title="isExpanded ? '收起详情' : '展开详情'">
              <span class="chevron" :class="{ 'rotated': isExpanded }">▼</span>
            </button>
          </div>
        </div>

        <!-- 下半部：上拉展开的深度信息 -->
        <div class="island-details">
          <div class="detail-divider"></div>
          
          <div class="detail-content">
            <!-- 左侧：补充元数据 -->
            <div class="meta-grid">
              <div class="meta-item">
                <span class="meta-label">创作者 (Artist)</span>
                <span class="meta-value">{{ store.activeSong.artist }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-label">所属专辑 (Album)</span>
                <span class="meta-value">{{ store.activeSong.album }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-label">声学流派 (Genre)</span>
                <span class="meta-value genre-value">{{ store.activeSong.genre }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-label">节拍速度 (Tempo)</span>
                <span class="meta-value">{{ store.activeSong.bpm.toFixed(0) }} BPM</span>
              </div>
            </div>

            <!-- 右侧：AI 简评推荐框 -->
            <div class="ai-review-box">
              <div class="review-header">
                <span class="bot-icon">🤖</span>
                <span class="review-title">AI 智能听感分析</span>
              </div>
              <p class="review-text">
                {{ store.activeSong.ai_review }}
              </p>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
.view-container { width: 100vw; height: 100vh; position: relative; pointer-events: none; }

/* 灵动岛外壳容器 (底部固定，水平居中) */
.island-wrapper { 
  position: absolute; 
  bottom: 40px; 
  left: 50%; 
  transform: translateX(-50%); 
  width: 80vw; 
  z-index: 100; 
  pointer-events: auto; 
}

/* 岛屿本体：弹性布局，平滑过渡 */
.giant-island { 
  width: 100%; 
  background: var(--island-bg); 
  backdrop-filter: blur(25px); -webkit-backdrop-filter: blur(25px);
  border: 1px solid var(--border-color); 
  border-radius: 24px; 
  box-shadow: 0 20px 50px rgba(0,0,0,0.5); 
  display: flex; 
  flex-direction: column; 
  padding: 20px 40px; 
  box-sizing: border-box;
  transition: all 0.5s cubic-bezier(0.25, 1, 0.5, 1);
}

/* 上半部常驻区 (高度固定) */
.island-main { display: flex; align-items: center; width: 100%; height: 80px; }
.island-leading { display: flex; align-items: center; gap: 20px; width: 20%; }
.waveform-box { display: flex; align-items: flex-end; gap: 3px; height: 30px; }
.wave-bar { width: 3px; background: var(--primary-color); animation: waveMove 1s infinite ease-in-out; }
@keyframes waveMove { 0%, 100% { height: 5px; } 50% { height: 25px; } }
.art-placeholder { width: 60px; height: 60px; background: linear-gradient(135deg, #1e3c72, #2a5298); border-radius: 12px; display: flex; justify-content: center; align-items: center; font-size: 24px; }

.island-body { flex: 1; display: flex; flex-direction: column; justify-content: center; margin-left: 20px; }
.info-header { display: flex; gap: 12px; margin-bottom: 4px; align-items: center; }
.ai-badge { font-size: 11px; background: #0066FF; color: #fff; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
.card-tag { font-size: 11px; border: 1px solid var(--primary-color); color: var(--primary-color); padding: 2px 8px; border-radius: 4px; }
.song-title { margin: 0; font-size: 24px; font-weight: bold; color: var(--text-main); }
.artist-name { margin: 4px 0 0; color: var(--text-sub); font-size: 14px; }
.bpm-mark { color: #555; font-size: 12px; margin-left: 10px; font-family: monospace; }

/* 按钮区 */
.island-trailing { width: 25%; display: flex; justify-content: flex-end; align-items: center; gap: 15px; }
.action-btn { background: rgba(255,255,255,0.05); color: var(--text-main); border: 1px solid rgba(255,255,255,0.2); padding: 12px 24px; border-radius: 30px; cursor: pointer; font-weight: bold; transition: 0.3s; }
.warp-btn:hover { border-color: var(--primary-color); color: var(--primary-color); background: rgba(0,255,204,0.1); }

/* 展开切换箭头 */
.expand-btn { 
  background: transparent; border: none; color: var(--text-main); font-size: 16px; cursor: pointer; 
  padding: 10px; border-radius: 50%; transition: 0.3s; display: flex; align-items: center; justify-content: center;
}
/* 鼠标悬停时的视觉反馈 */
.expand-btn:hover { color: var(--primary-color); background: rgba(0,255,204,0.1); }
/* 箭头旋转状态 */
.chevron { transition: transform 0.4s cubic-bezier(0.25, 1, 0.5, 1); display: inline-block; }
/* 旋转180度表示展开状态，颜色变为主题色 */
.chevron.rotated { transform: rotate(180deg); color: var(--primary-color); }

/* 下半部：深度详情区 (高度动画核心) */
.island-details {
  width: 100%;
  max-height: 0;       /* 初始隐藏 */
  opacity: 0;
  overflow: hidden;
  transition: all 0.5s cubic-bezier(0.25, 1, 0.5, 1);
}

/* 激活展开状态 */
.is-expanded .island-details {
  max-height: 300px;   /* 容纳内容的最大高度 */
  opacity: 1;
  margin-top: 20px;
}

.detail-divider {
  width: 100%; height: 1px; background: rgba(255,255,255,0.1); margin-bottom: 20px;
}

.detail-content {
  display: flex; gap: 40px; padding-bottom: 10px;
}

/* 左侧：四个属性方块 */
/* 使用 CSS Grid 来创建两列两行的布局 */
.meta-grid {
  flex: 1; display: grid; grid-template-columns: 1fr 1fr; gap: 15px;
}
/* 每个属性方块的样式 */
.meta-item {
  background: rgba(0,0,0,0.2); padding: 12px 15px; border-radius: 8px;
  display: flex; flex-direction: column; gap: 5px;
  border: 1px solid rgba(255,255,255,0.03);
}
/* 标签和数值的样式 */
.meta-label { color: var(--text-main); font-size: 12px; }
/* 数值部分加粗，单行显示，超出部分省略号 */
.meta-value { color: var(--text-main); font-size: 14px; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* 右侧：AI 简评框 */
.ai-review-box {
  flex: 1.5; background: rgba(0, 255, 204, 0.05); 
  border-left: 4px solid var(--primary-color); border-radius: 0 8px 8px 0;
  padding: 15px 20px; display: flex; flex-direction: column;
}
/* AI 简评标题部分 */
.review-header { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
/* 机器人图标和标题样式 */
.bot-icon { font-size: 18px; }
/* AI 简评标题 */
.review-title { color: var(--primary-color); font-weight: bold; font-size: 14px; }
/* AI 简评内容，支持多行文本，文本对齐为两端 */
.review-text { margin: 0; color: var(--nav-text); font-size: 13px; line-height: 1.6; text-align: justify; }

/* 日间模式覆盖 (基于主题变量) */
.theme-light .wave-bar {
  background: var(--nav-text); /* 日间黑色 */
}
.theme-light .card-tag {
  border-color: var(--nav-text);
  color: var(--nav-text);
}
.theme-light .giant-island {
  border-color: var(--nav-text); /* 容器包边改为黑色 */
}
.theme-light .ai-review-box {
  border-left-color: var(--nav-text); /* AI 边框黑色 */
}
.theme-light .review-title {
  color: var(--nav-text); /* AI 标题黑色 */
}
.theme-light .chevron.rotated {
  color: var(--nav-text); /* 旋转箭头黑色 */
}
.theme-light .genre-value {
  color: var(--nav-text) !important; /* 流派文字黑色 */
}
.theme-light .expand-btn:hover {
  color: var(--nav-text); /* 展开按钮悬停黑色 */
  background: rgba(0, 0, 0, 0.1);
}
</style>