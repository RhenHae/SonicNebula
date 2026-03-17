<!-- src/components/NavBar.vue -->
<template>
  <nav class="custom-navbar">
    <div class="navbar-title">🎵 SonicNebula</div>

    <div class="navbar-menu" @mouseleave="resetIndicator">
      <div class="nav-indicator" :style="indicatorStyle"></div>
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="nav-item"
        active-class="active"
        @mouseenter="moveIndicator"
      >
        {{ t(item.key) }}
      </router-link>
    </div>

    <div class="settings-wrapper">
      <div class="settings-btn" @click="$emit('toggle-settings')">⚙️ 设置</div>
    </div>
  </nav>
</template>

<script setup>
import { ref, nextTick, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { store } from '../store.js'

const route = useRoute()
const emit = defineEmits(['toggle-settings'])

// 导航项配置
const navItems = [
  { path: '/intro', key: 'nav_intro' },
  { path: '/explorer', key: 'nav_explore' },
  { path: '/analysis', key: 'nav_analysis' }
]

// 多语言函数
const dict = {
  zh: { nav_intro: '简介', nav_explore: '探索发现', nav_analysis: '歌曲解析' },
  en: { nav_intro: 'Intro', nav_explore: 'Explorer', nav_analysis: 'Analysis' }
}
const t = (key) => dict[store.lang][key]

// 灵动指示器
const indicatorStyle = ref({ width: '0px', left: '0px', opacity: 0 })

const moveIndicator = (e) => {
  const el = e.currentTarget
  indicatorStyle.value = {
    width: `${el.offsetWidth}px`,
    left: `${el.offsetLeft}px`,
    opacity: 1
  }
}


const resetIndicator = () => {
  nextTick(() => {
    const activeEl = document.querySelector('.nav-item.active')
    if (activeEl) {
      indicatorStyle.value = {
        width: `${activeEl.offsetWidth}px`,
        left: `${activeEl.offsetLeft}px`,
        opacity: 1
      }
    } else {
      indicatorStyle.value = { width: '0px', left: '0px', opacity: 0 }
    }
  })
}

// 路由变化时重置指示器
watch(() => route.path, () => {
  setTimeout(resetIndicator, 100)
})

onMounted(() => {
  setTimeout(resetIndicator, 300)
})
</script>

<style scoped>
.custom-navbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 64px;
  background-color: var(--nav-bg);
  backdrop-filter: var(--nav-blur);
  z-index: 999;
  display: flex;
  align-items: center;
  padding: 0 40px;
  box-sizing: border-box;
  border-bottom: 1px solid var(--border-color);
  transition: background-color 0.3s, backdrop-filter 0.3s;
}

.navbar-title {
  color: var(--text-main);
  font-size: 22px;
  font-weight: 900;
  letter-spacing: 1px;
  margin-right: 60px;
}

.navbar-menu {
  display: flex;
  gap: 40px;
  flex: 1;
  position: relative;
}

.nav-item {
  position: relative;
  color: var(--nav-text);
  text-decoration: none;
  font-size: 15px;
  font-weight: bold;
  pointer-events: auto;
  padding: 20px 0;
  transition: color 0.3s, text-shadow 0.3s;
}

.nav-item:hover,
.nav-item.active {
  color: var(--nav-text-active);
}

.nav-indicator {
  position: absolute;
  bottom: 10px;
  height: 3px;
  background: var(--primary-color);
  box-shadow: 0 0 10px var(--primary-color);
  border-radius: 2px;
  pointer-events: none;
  transition: all 0.4s cubic-bezier(0.25, 1, 0.5, 1);
}

.settings-wrapper {
  position: relative;
  pointer-events: auto;
}

.settings-btn {
  color: var(--text-main);
  cursor: pointer;
  font-weight: bold;
  transition: color 0.3s;
}

.settings-btn:hover {
  color: var(--primary-color);
}

</style>