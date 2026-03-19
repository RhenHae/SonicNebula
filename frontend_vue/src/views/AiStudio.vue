<script setup>
import { ref, shallowRef } from 'vue'
import { onBeforeRouteLeave } from 'vue-router'
import StemSeparator from '../components/Studio/StemSeparator.vue'
import AutoTranscriber from '../components/Studio/AutoTranscriber.vue'
import FormatConverter from '../components/Studio/FormatConverter.vue'

// 1. 插件化路由注册表 (文案全流通俗化)
const tabs =[
  { id: 'separation', name: '音轨分离提取', desc: '把一首歌拆分成伴奏、人声、吉他等 5 条独立轨道。', component: StemSeparator },
  { id: 'transcription', name: 'AI 自动生成乐谱', desc: '让 AI 听歌，自动写出乐谱和吉他/钢琴和弦。', component: AutoTranscriber },
  { id: 'conversion', name: '音频格式转换', desc: '支持 MP3、WAV、FLAC 等常见格式互相转换。', component: FormatConverter }
]

const activeTabId = ref(tabs[0].id)
const activeComponent = shallowRef(tabs[0].component)
const currentStudioRef = ref(null)

// 2. 内部 Tab 切换时的拦截
const handleTabChange = (tab) => {
  if (activeTabId.value === tab.id) return
  
  // 🚀 核心修复：正确读取 currentStudioRef.value 的 fileState
  if (currentStudioRef.value && currentStudioRef.value.fileState > 0) {
    if (!window.confirm("⚠️ 切换功能将清空您刚才上传的文件和进度！\n\n确定要放弃当前进度吗？")) return
  }
  
  activeTabId.value = tab.id
  activeComponent.value = tab.component
}

// 3. 路由跳转时的拦截
onBeforeRouteLeave(async (to, from, next) => {
  // 🚀 核心修复：判断是否有未完成的任务
  if (currentStudioRef.value && currentStudioRef.value.fileState > 0) {
    const confirmed = window.confirm("⚠️ 您的文件还未处理保存！离开此页面将丢失进度。\n\n确定要离开吗？")
    if (confirmed) {
      if (typeof currentStudioRef.value.reset === 'function') {
        currentStudioRef.value.reset()
      }
      next() // 放行
    } else {
      next(false) // 拦截，留在当前页面
    }
  } else {
    next() // 没数据，直接放行
  }
})
</script>

<template>
  <div class="studio-glass-overlay">
    <div class="studio-container">
      
      <!-- 左侧：功能选择侧边栏 -->
      <div class="studio-sidebar glass-panel">
        <div class="sidebar-header">
          <h2 style="color: var(--primary-color); margin: 0;">AI 实验室</h2>
          <p style="margin: 5px 0 0 0; font-size: 12px; color: var(--text-sub);">智能音乐处理工具箱</p>
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

      <!-- 右侧：核心工作台 -->
      <div class="studio-workbench glass-panel">
        <transition name="fade" mode="out-in">
          <!-- 动态加载子组件，并赋予 ref -->
          <component :is="activeComponent" ref="currentStudioRef" />
        </transition>
      </div>

    </div>
  </div>
</template>

<style scoped>
.studio-glass-overlay { width: 100vw; height: 100vh; background: rgba(5, 5, 10, 0.5); backdrop-filter: blur(25px); -webkit-backdrop-filter: blur(25px); position: absolute; top: 0; left: 0; z-index: 10; display: flex; align-items: center; justify-content: center; pointer-events: auto; }
.studio-container { display: flex; gap: 20px; width: 90vw; height: 85vh; margin-top: 60px; }
.glass-panel { background: var(--island-bg); border: 1px solid var(--border-color); border-radius: 16px; box-shadow: 0 15px 35px rgba(0,0,0,0.3); display: flex; flex-direction: column; overflow: hidden; position: relative;}

.studio-sidebar { width: 300px; flex-shrink: 0; padding: 25px; }
.sidebar-header { margin-bottom: 30px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 15px; }
.tab-list { display: flex; flex-direction: column; gap: 15px; overflow-y: auto; }
.tab-item { padding: 15px; border-radius: 10px; border: 1px solid transparent; background: rgba(255,255,255,0.02); cursor: pointer; transition: all 0.3s; }
.tab-item:hover { background: rgba(255,255,255,0.05); }
.tab-item.active { background: rgba(0, 255, 204, 0.08); border-color: var(--primary-color); box-shadow: 0 0 15px rgba(0, 255, 204, 0.1); }
.tab-name { color: var(--text-main); font-weight: bold; font-size: 15px; margin-bottom: 5px; }
.tab-desc { color: var(--text-sub); font-size: 12px; line-height: 1.5; }

.studio-workbench { flex: 1; padding: 30px; position: relative; }
</style>