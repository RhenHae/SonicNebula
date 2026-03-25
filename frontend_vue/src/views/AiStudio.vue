<script setup>
import { ref, shallowRef } from 'vue'
import { onBeforeRouteLeave } from 'vue-router'
import StemSeparator from '../components/Studio/StemSeparator.vue'
import AutoTranscriber from '../components/Studio/AutoTranscriber.vue'
import FormatConverter from '../components/Studio/FormatConverter.vue'

// 插件化路由注册表
const tabs = [
  { id: 'separation', name: '音轨分离提取', desc: '把一首歌拆分成伴奏、人声、吉他等 5 条独立轨道。', component: StemSeparator },
  { id: 'transcription', name: 'AI 自动生成乐谱', desc: '让 AI 听歌，自动写出乐谱和吉他/钢琴和弦。', component: AutoTranscriber },
  { id: 'conversion', name: '音频格式转换', desc: '支持 MP3、WAV、FLAC 等常见格式互相转换。', component: FormatConverter }
]

const activeTabId = ref(tabs[0].id)
const activeComponent = shallowRef(tabs[0].component)
const currentStudioRef = ref(null)

const handleTabChange = (tab) => {
  if (activeTabId.value === tab.id) return
  if (currentStudioRef.value && currentStudioRef.value.fileState > 0) {
    if (!window.confirm("⚠️ 切换功能将清空您刚才上传的文件和进度！\n\n确定要放弃当前进度吗？")) return
  }
  activeTabId.value = tab.id
  activeComponent.value = tab.component
}

onBeforeRouteLeave(async (to, from, next) => {
  if (currentStudioRef.value && currentStudioRef.value.fileState > 0) {
    const confirmed = window.confirm("⚠️ 您的文件还未处理保存！离开此页面将丢失进度。\n\n确定要离开吗？")
    if (confirmed) {
      if (typeof currentStudioRef.value.reset === 'function') {
        currentStudioRef.value.reset()
      }
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
  <!-- 全局毛玻璃遮罩，复用 theme.css 的 global-glass-overlay 类 -->
  <div class="global-glass-overlay">
    <div class="studio-container">
      <!-- 左侧侧边栏：使用玻璃面板通用类 -->
      <div class="studio-sidebar glass-panel">
        <div class="sidebar-header">
          <h2 class="primary-text">AI 实验室</h2>
          <p class="sub-text" style="margin-top: 5px;">智能音乐处理工具箱</p>
        </div>
        
        <div class="tab-list">
          <div 
            v-for="tab in tabs" :key="tab.id"
            class="tab-item" :class="{ active: activeTabId === tab.id }"
            @click="handleTabChange(tab)" 
          >
            <div class="tab-name">{{ tab.name }}</div>
            <div class="tab-desc">{{ tab.desc }}</div>
          </div>
        </div>
      </div>

      <!-- 右侧工作台：使用玻璃面板通用类 -->
      <div class="studio-workbench glass-panel">
        <transition name="fade" mode="out-in">
          <component :is="activeComponent" ref="currentStudioRef" />
        </transition>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 仅保留组件特有布局，全局样式已由 theme.css 提供 */
.studio-container {
  display: flex;
  gap: 20px;
  width: 90vw;
  height: 85vh;
  margin-top: 60px;
  color: glass-panel(var(--text-main) / 0.8);
}

/* 侧边栏固定宽度 */
.studio-sidebar {
  width: 300px;
  flex-shrink: 0;
  padding: 25px;
}

.sidebar-header {
  margin-bottom: 30px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 15px;
}

.tab-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  overflow-y: auto;
}

.tab-item {
  padding: 15px;
  border-radius: 10px;
  border: 1px solid transparent;
  background: rgba(255, 255, 255, 0.02);
  cursor: pointer;
  transition: all 0.3s;
}

.tab-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.tab-item.active {
  background: rgba(0, 255, 204, 0.08);
  border-color: var(--primary-color);
  box-shadow: 0 0 15px rgba(0, 255, 204, 0.1);
}

.tab-name {
  color: var(--text-main);
  font-weight: bold;
  font-size: 15px;
  margin-bottom: 5px;
}

.tab-desc {
  color: var(--text-sub);
  font-size: 12px;
  line-height: 1.5;
}

.studio-workbench {
  flex: 1;
  padding: 30px;
  position: relative;
}
</style>