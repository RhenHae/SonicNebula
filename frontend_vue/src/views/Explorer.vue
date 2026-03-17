<script setup>
import { store } from '../store.js'
import axios from 'axios'

const warpToRandom = async () => {
  try {
    // 假设后端提供了一个随机歌曲的极简接口 (稍后我们在后端实现)
    // 目前你可以先用前端模拟，为了解耦，这里暂时保持 UI 框架
    alert("曲速跃迁！(后端接口待接入)")
  } catch (err) {
    console.error(err)
  }
}
</script>

<template>
  <div class="view-container">
    <div class="island-wrapper">
      <div class="giant-island">
        <div class="island-leading">
          <div class="waveform-box"><div v-for="i in 8" :key="i" class="wave-bar" :style="{animationDelay: i*0.1+'s'}"></div></div>
          <div class="art-placeholder">🎵</div>
        </div>
        <div class="island-body">
          <div class="info-header">
            <span class="ai-badge">🤖 AI 嗅探发现</span>
            <span class="card-tag">{{ store.activeSong.genre }}</span>
            <span class="cosmic-coord">X:{{ store.activeSong.x.toFixed(1) }} Y:{{ store.activeSong.y.toFixed(1) }}</span>
          </div>
          <h4 class="song-title">{{ store.activeSong.title }}</h4>
          <p class="artist-name">{{ store.activeSong.artist }} // {{ store.activeSong.bpm.toFixed(0) }} BPM</p>
        </div>
        <div class="island-trailing">
          <button class="action-btn warp-btn" @click="warpToRandom">✨ 曲速跃迁</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.view-container { width: 100vw; height: 100vh; position: relative; pointer-events: none; }
.island-wrapper { position: absolute; bottom: 30px; left: 50%; transform: translateX(-50%); width: 80vw; height: 120px; z-index: 100; pointer-events: auto; }
.giant-island { width: 100%; height: 100%; background: var(--island-bg); backdrop-filter: blur(25px); border: 1px solid var(--border-color); border-radius: 24px; display: flex; align-items: center; padding: 0 40px; box-sizing: border-box; box-shadow: 0 20px 40px rgba(0,0,0,0.5); }
.island-leading { display: flex; align-items: center; gap: 20px; width: 20%; }
.waveform-box { display: flex; align-items: flex-end; gap: 3px; height: 30px; }
.wave-bar { width: 3px; background: #00FFCC; animation: waveMove 1s infinite ease-in-out; }
@keyframes waveMove { 0%, 100% { height: 5px; } 50% { height: 25px; } }
.art-placeholder { width: 60px; height: 60px; background: linear-gradient(135deg, #1e3c72, #2a5298); border-radius: 12px; display: flex; justify-content: center; align-items: center; font-size: 24px; }
.island-body { flex: 1; display: flex; flex-direction: column; justify-content: center; }
.info-header { display: flex; gap: 12px; margin-bottom: 4px; align-items: center; }
.ai-badge { font-size: 10px; background: #FF003C; color: #fff; padding: 2px 6px; border-radius: 4px; }
.card-tag { font-size: 10px; border: 1px solid #00FFCC; color: #00FFCC; padding: 2px 6px; border-radius: 4px; }
.cosmic-coord { font-size: 10px; color: var(--text-sub); font-family: monospace; }
.song-title { margin: 0; font-size: 24px; font-weight: bold; color: var(--text-main); }
.artist-name { margin: 4px 0 0; color: var(--text-sub); font-size: 14px; }
.bpm-mark { color: #555; font-size: 11px; margin-left: 10px; }
.island-trailing { width: 20%; display: flex; justify-content: flex-end; }
.action-btn { background: rgba(255,255,255,0.05); color: var(--text-main); border: 1px solid rgba(255,255,255,0.2); padding: 12px 24px; border-radius: 30px; cursor: pointer; font-weight: bold; transition: 0.3s; }
.action-btn:hover { border-color: #00FFCC; color: #00FFCC; background: rgba(0,255,204,0.1); }
</style>