<script setup>
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

    <FooterDisclaimer />
  </div>
</template>

<style scoped>
/* 背景遮罩层：半透明 + 毛玻璃，确保星空透出 */
.intro-glass-overlay {
  width: 100vw;
  height: 100vh;
  background: var(--overlay-bg);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: auto;
  position: relative;
}

/* 内容卡片：使用主题变量，背景随主题切换 */
.content-box {
  background: var(--island-bg);
  padding: 50px 60px;
  border-radius: 20px;
  border: 1px solid var(--border-color);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
  text-align: center;
  max-width: 800px;
  animation: floatUp 0.8s cubic-bezier(0.16, 1, 0.3, 1);
  transition: background-color 0.3s, border-color 0.3s;
  position: relative;
  z-index: 2;
}

/* 主标题：使用主题色 */
.glitch-title {
  color: var(--primary-color);
  font-size: 42px;
  margin-bottom: 10px;
  font-weight: 900;
}

/* 副标题：使用次要文字色 */
.subtitle {
  color: var(--text-sub);
  font-size: 18px;
  margin-bottom: 40px;
  letter-spacing: 2px;
}

/* 特性网格布局 */
.feature-grid {
  display: flex;
  gap: 20px;
  text-align: left;
}

/* 特性卡片：背景和边框随主题变化 */
.feature-card {
  flex: 1;
  background: var(--panel-bg);
  padding: 20px;
  border-radius: 12px;
  border-top: 2px solid var(--primary-color);
  transition: background-color 0.3s, border-color 0.3s;
}

.feature-card h3 {
  color: var(--text-main);
  font-size: 16px;
  margin-top: 0;
}

.feature-card p {
  color: var(--text-sub);
  font-size: 13px;
  line-height: 1.6;
  margin-bottom: 0;
}

/* 卡片浮现动画 */
@keyframes floatUp {
  0% { opacity: 0; transform: translateY(60px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>