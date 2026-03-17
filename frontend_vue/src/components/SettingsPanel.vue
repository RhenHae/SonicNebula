<!-- src/components/SettingsPanel.vue -->
<template>
  <transition name="fade">
    <div v-if="show" class="settings-panel">
      <h4>{{ t('set_title') }}</h4>
      <div class="set-item">
        <span>{{ t('lang') }}</span>
        <div class="toggle-group">
          <span :class="{ active: store.lang === 'zh' }" @click="store.lang = 'zh'">ZH</span>
          <span :class="{ active: store.lang === 'en' }" @click="store.lang = 'en'">EN</span>
        </div>
      </div>
      <div class="set-item">
        <span>{{ t('theme') }}</span>
        <div class="toggle-group">
          <span :class="{ active: store.theme === 'dark' }" @click="store.theme = 'dark'">Dark</span>
          <span :class="{ active: store.theme === 'light' }" @click="store.theme = 'light'">Light</span>
        </div>
      </div>
      <div class="set-item">
        <span>{{ t('engine') }}</span>
        <label class="switch">
          <!-- 关键修改：将 v-model 绑定改为 store.qualityMode -->
          <input type="checkbox" v-model="store.qualityMode" />
          <span class="slider round"></span>
        </label>
      </div>
      <div class="set-item" style="flex-direction: column; align-items: flex-start; gap: 8px;">
        <span>{{ t('filter') }}</span>
        <select v-model="store.currentFilter" class="custom-select">
          <option value="default">乐动星云 (Nebula)</option>
          <option value="star">深邃星体 (Star)</option>
          <option value="cyberpunk">霓虹赛博 (Neon)</option>
          <option value="synthwave">合成器波 (Synthwave)</option>
          <option value="dreamy">梦幻粉紫 (Dreamy)</option>
          <option value="starry_night">星空致敬 (Starry Night)</option>
        </select>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { store } from '../store.js'

defineProps({
  show: Boolean
})

const dict = {
  zh: { set_title: '引擎偏好控制', lang: '界面语言', theme: '界面主题', engine: '粒子呼吸引擎', filter: '色彩滤镜' },
  en: { set_title: 'Engine Preferences', lang: 'Language', theme: 'Theme', engine: 'Particle Engine', filter: 'Color Filter' }
}
const t = (key) => dict[store.lang][key]
</script>

<style scoped>
/* 设置面板样式 */
.settings-panel {
  position: absolute;
  top: 65px;
  right: 0;
  background: var(--panel-bg);
  border: 1px solid var(--border-color);
  padding: 20px;
  border-radius: 12px;
  backdrop-filter: blur(15px);
  width: 300px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
  z-index: 1000;
}
/* 标题样式 */
.settings-panel h4 {
  margin: 0 0 20px 0;
  color: var(--primary-color);
  font-size: 16px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 10px;
}
/* 每项设置的样式 */
.set-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  font-size: 14px;
  font-weight: bold;
}
/* 切换按钮组样式 */
.toggle-group {
  display: flex;
  background: rgba(100,100,100,0.2);
  border-radius: 20px;
  padding: 2px;
}
/* 切换按钮样式 */
.toggle-group span {
  padding: 4px 10px;
  font-size: 12px;
  cursor: pointer;
  border-radius: 16px;
  color: var(--text-sub);
  transition: 0.3s;
}
/* 激活状态的按钮样式 */
.toggle-group span.active {
  background: var(--primary-color);
  color: #fff;
  font-weight: bold;
}
/* 开关组件样式 */
.switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}
/* 隐藏默认的 checkbox */
.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}
/* 自定义滑块样式 */
.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #555;
  border-radius: 24px;
  transition: .4s;
}
/* 滑块圆点样式 */
.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  border-radius: 50%;
  transition: .4s;
}
/* 当 checkbox 被选中时，改变滑块背景色和位置 */
input:checked + .slider {
  background-color: var(--primary-color);
}
/* 当 checkbox 被选中时，滑块圆点向右移动 */
input:checked + .slider:before {
  transform: translateX(20px);
}
/* 圆形滑块 */
.custom-select {
  width: 100%;
  padding: 8px;
  background: rgba(0,0,0,0.05);
  color: var(--primary-color);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  outline: none;
  font-family: monospace;
}
/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>