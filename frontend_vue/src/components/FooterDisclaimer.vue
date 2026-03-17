<template>
  <footer class="disclaimer-footer">
    <span>本项目仅供学术研究与大数据学习使用，音频版权归原作者所有</span>
    <span class="divider">|</span>
    <span>© 2026 SonicNebula 版权所有</span>
    <span class="divider">|</span>
    <span>蜀ICP备XXXXXXX号</span>
  </footer>
</template>

<script setup>
// 纯展示组件，无需逻辑
</script>

<style scoped>
.disclaimer-footer {
  position: absolute; /* 绝对定位，永远吸附在所在容器的底部 */
  bottom: 0;
  left: 0;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px; /* 控制文字段落之间的间距 */
  color: var(--text-sub);
  font-size: 12px;
  padding: 12px 0;
  /* 去掉生硬的 border-top，使用微弱的背景渐变让它自然融入 */
  background: linear-gradient(to top, rgba(0,0,0,0.4) 0%, transparent 100%);
  pointer-events: auto;
  z-index: 10;
  letter-spacing: 0.5px;
}

/* 竖线分隔符降低透明度，增加精致感 */
.divider {
  opacity: 0.3;
  font-size: 10px;
}

/* 适配亮色主题 */
.theme-light .disclaimer-footer {
  background: linear-gradient(to top, rgba(0,0,0,0.4) 0%, transparent 100%);
}
</style>