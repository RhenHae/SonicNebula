<script setup>
// 引入免责声明底部组件
import FooterDisclaimer from '../components/FooterDisclaimer.vue'
</script>

<template>
  <div class="intro-glass-overlay">
    <div class="content-box">
      <h1 class="glitch-title">🎵 Project: SonicNebula</h1>
      <p class="subtitle">基于分布式音频处理的音乐风格测绘引擎</p>
      
      <div class="feature-grid">
        <div class="feature-card">
          <h3>🚀 分布式架构</h3>
          <p>Hadoop HDFS + Apache Spark 处理海量音频特征提取与列式存储。</p>
        </div>
        <div class="feature-card">
          <h3>🧬 信号处理</h3>
          <p>Librosa 提取 20 维 MFCC 音色特征与 BPM 节拍数据。</p>
        </div>
        <div class="feature-card">
          <h3>🌌 机器学习</h3>
          <p>K-Means 无监督聚类 + t-SNE 算法实现高维空间折叠可视化。</p>
        </div>
      </div>
    </div>

    <!-- 挂载底部组件 -->
    <FooterDisclaimer />
  </div>
</template>

<style scoped>
.intro-glass-overlay {
  width: 100vw;
  height: 100vh;
  /* 添加半透明背景色，避免浏览器渲染异常，同时与模糊配合形成毛玻璃效果 */
  background: var(--overlay-bg);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: auto;
  /* 确保覆盖层位于星云上方，但不遮挡星云（半透明+模糊） */
  position: relative;
}

.content-box {
  background: var(--island-bg);            /* 使用灵动岛背景变量（日间白透，夜间黑透） */
  padding: 50px 60px;
  border-radius: 20px;
  border: 1px solid var(--border-color);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
  text-align: center;
  max-width: 800px;
  animation: floatUp 0.8s cubic-bezier(0.16, 1, 0.3, 1);
  transition: background-color 0.3s, border-color 0.3s;
  /* 确保内容位于覆盖层之上 */
  position: relative;
  z-index: 2;
}

.glitch-title {
  color: var(--primary-color);              /* 主题色 */
  font-size: 42px;
  margin-bottom: 10px;
  font-weight: 900;
}

.subtitle {
  color: var(--text-sub);                   /* 次要文字 */
  font-size: 18px;
  margin-bottom: 40px;
  letter-spacing: 2px;
}

.feature-grid {
  display: flex;
  gap: 20px;
  text-align: left;
}

.feature-card {
  flex: 1;
  background: var(--panel-bg);               /* 卡片背景使用面板变量 */
  padding: 20px;
  border-radius: 12px;
  border-top: 2px solid var(--primary-color); /* 主题色边框 */
  transition: background-color 0.3s, border-color 0.3s;
}

.feature-card h3 {
  color: var(--text-main);                    /* 主要文字 */
  font-size: 16px;
  margin-top: 0;
}

.feature-card p {
  color: var(--text-sub);                     /* 次要文字 */
  font-size: 13px;
  line-height: 1.6;
  margin-bottom: 0;
}

/* 浮动动画 */
@keyframes floatUp {
  /* 从下方轻微浮起并淡入 */
  0% { opacity: 0; transform: translateY(30px); }
  /* 到达最终位置，保持完全可见 */
  100% { opacity: 1; transform: translateY(0); }
}
</style>