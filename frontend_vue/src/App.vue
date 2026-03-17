<!-- src/App.vue -->
<script setup>
import { ref, watch } from 'vue'
import { store } from './store.js'
import MouseGlow from './components/MouseGlow.vue'
import NavBar from './components/NavBar.vue'
import SettingsPanel from './components/SettingsPanel.vue'
import NebulaCanvas from './components/NebulaCanvas.vue'
import { useRoute } from 'vue-router'

// 设置面板显隐状态
const showSettings = ref(false)
// 监听路由变化，更新 store.currentPage
const route = useRoute()

// 主题切换：修改 body 类
watch(() => store.theme, (theme) => {
  if (theme === 'light') document.body.classList.add('theme-light')
  else document.body.classList.remove('theme-light')
}, { immediate: true })

// 监听路由变化，更新 store.currentPage
watch(() => route.path, (path) => {
  if (path === '/analysis') store.currentPage = 'analysis'
  else if (path === '/intro') store.currentPage = 'intro'
  else if (path === '/explorer') store.currentPage = 'explorer'
  else store.currentPage = 'explorer' // 默认
}, { immediate: true })

</script>


<template>
  <div class="app-wrapper">
    <MouseGlow />
    <NebulaCanvas class="fullscreen-nebula" />

    <!-- 导航栏：点击设置按钮切换 showSettings -->
    <NavBar @toggle-settings="showSettings = !showSettings" />

    <!-- 设置面板：位置跟随导航栏右侧，由 showSettings 控制显示 -->
    <SettingsPanel :show="showSettings" />

    <!-- 路由视图 -->
    <div class="router-layer">
      <router-view v-slot="{ Component, route }">
        <transition :name="route.meta.transition || 'slide-fade'" mode="out-in">
          <component :is="Component" :key="route.path" />
        </transition>
      </router-view>
    </div>
  </div>
</template>

<style>
/* 全局基础样式（不含主题变量，建议移至 theme.css） */
:root {
  /* 夜间模式（默认） */
  --bg-color: #05050a;
  --bg-gradient: radial-gradient(circle at center, #1a1a24 0%, #05050a 100%);
  --text-main: #ffffff;
  --text-sub: #888888;
  --panel-bg: rgba(20,20,25,0.95);
  --border-color: rgba(0, 255, 204, 0.3);
  --primary-color: #00FFCC;
  --primary-glow: rgba(0, 255, 204, 0.6);
  --primary-faint: rgba(0, 255, 204, 0.1);
  --island-bg: rgba(20, 20, 25, 0.8);   /* 黑色半透明 */
  --overlay-bg: rgba(0, 0, 0, 0.2);

  /* 导航栏专用变量（夜间） */
  --nav-bg: #000000;
  --nav-text: #888888;
  --nav-text-active: #00FFCC;
  --nav-blur: blur(20px);
}

.theme-light {
  --bg-color: #f8fafc;
  --bg-gradient: linear-gradient(145deg, #ffffff 0%, #f1f5f9 100%);
  --text-main: #0f172a;
  --text-sub: #334155;
  --panel-bg: rgba(255,255,255,0.9);
  --border-color: rgba(0, 255, 204, 0.2);
  --primary-color: #00CCAA;
  --primary-glow: rgba(0, 255, 204, 0.4);
  --primary-faint: rgba(0, 255, 204, 0.1);
  --island-bg: rgba(255, 255, 255, 0.8); /* 白色半透明 */
  --overlay-bg: rgba(255, 255, 255, 0.2);

  /* 导航栏专用变量（日间） */
  --nav-bg: #00CCAA;
  --nav-text: #333333;
  --nav-text-active: #000000;
  --nav-blur: none;
}

body, html {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: var(--bg-gradient);
  font-family: sans-serif;
  color: var(--text-main);
  transition: background 0.5s, color 0.5s;
}

.app-wrapper {
  position: relative;
  width: 100vw;
  height: 100vh;
}

.fullscreen-nebula {
  position: absolute;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 1;
}

.router-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 5;
  pointer-events: none;
  overflow: hidden;
}

/* 路由动画 */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.4s ease-out;
}
/* 进入时从右侧淡入 */
.slide-fade-enter-from {
  opacity: 0;
  transform: translateX(30px);
}
/* 离开时向左侧淡出 */
.slide-fade-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}
/* 适配亮色主题 */
.fullscreen-nebula {
  background-color: #05050a; /* 固定深色背景，不随主题变化 */
}
/* 导航栏适配亮色主题 */
.theme-light .nav-item.active {
  color: white !important;
}
/* 导航栏指示器适配亮色主题 */
.theme-light .nav-indicator {
  background: white !important;
  box-shadow: 0 0 10px white !important;
}
</style>