<template>
  <div class="native-nebula-wrapper">
    <canvas ref="canvasRef" class="star-canvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { store } from '../store.js'

// ==========================================
// ⚙️ 1. 引擎核心物理与渲染配置 (消灭魔法数字)
// ==========================================
const ENGINE_CONFIG = {
  STARS_COUNT_HIGH: 2000,       // 性能模式下的星星数量
  STARS_COUNT_LOW: 600,         // 节能模式下的星星数量
  GALAXY_RADIUS: 2500,          // 星系物理半径
  FOCAL_LENGTH: 1000,           // 相机透视焦距
  ROTATION_SPEED: 0.0006,       // 星系自转角速度
  FOLLOW_SPEED: 0.05,           // 阻尼跟随系数
  REPEL_STRENGTH: 10,          // 鼠标斥力绝对强度
  REPEL_RADIUS: 125,            // 鼠标力场影响半径
  EDGE_FADE_THRESHOLD: -300,    // 边缘渐隐触发距离
  BREATH_SPEED_BASE: 0.015,     // 基础呼吸速度
  BREATH_SPEED_VAR: 0.02        // 呼吸速度随机方差
}

// 预计算力场半径的平方，极大降低帧循环中的开方运算开销
const REPEL_RADIUS_SQ = ENGINE_CONFIG.REPEL_RADIUS * ENGINE_CONFIG.REPEL_RADIUS

// 🎨 色彩光谱字典
const colorPalettes = {
  default:['#ffffff', '#ffe68f', '#ffb56b', '#d4a5ff', '#a5c8ff', '#c2e0ff', '#ffd1a0', '#f0f0f0', '#e0b0ff', '#b0d0ff'],
  star:['#8dd3c7', '#ffffb3', '#bebada', '#fb8072', '#80b1d3', '#fdb462', '#b3de69', '#fccde5', '#d9d9d9', '#bc80bd', '#ccebc5'],
  cyberpunk:['#FF003C', '#FF8A00', '#00F0FF', '#B900FF', '#FCEE0A', '#00FF9D', '#FFFFFF', '#0B0B1F', '#FF44AA', '#7DF9FF'],
  synthwave:['#1a1a2e', '#0b0b1f', '#01fdf6', '#b967ff', '#ff00c3', '#f70676', '#ffb347', '#8a2be2', '#fe59d2', '#ffe77b'],
  dreamy:['#ffb6c1', '#dda0dd', '#e0b0ff', '#b0e0e6', '#afeeee', '#f0f8ff', '#fff0f5', '#d8bfd8', '#b0c4de', '#e6e6fa'],
  starry_night:['#0b1c3a', '#1d2b53', '#2c3e6b', '#3f5185', '#5a6b9e', '#7f8fb2', '#a5b4d4', '#f7e05e', '#ffb347', '#f8f087']
}

// ==========================================
// 🚀 2. 渲染器上下文与状态
// ==========================================
const route = useRoute()
const canvasRef = ref(null)
let animationId = null
let stars =[]

let mouseX = -1000, mouseY = -1000
const handleMouseMove = (e) => {
  mouseX = e.clientX
  mouseY = e.clientY
}

const initEngine = () => {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d', { alpha: false }) // 关闭 alpha 混合提升底图性能

  let width, height, centerX, centerY

  const resize = () => {
    width = canvas.width = window.innerWidth
    height = canvas.height = window.innerHeight
    centerX = width / 2
    centerY = height / 2
  }
  resize()
  window.addEventListener('resize', resize)
  window.addEventListener('mousemove', handleMouseMove)

  // 🌌 构造星系粒子组
  const buildGalaxy = () => {
    stars =[]
    const palette = colorPalettes[store.currentFilter] || colorPalettes.default
    
    // 始终生成最大数量的星星，渲染时再根据模式截断，避免切换模式时重新生成数组导致的卡顿
    for (let i = 0; i < ENGINE_CONFIG.STARS_COUNT_HIGH; i++) {
      const r = ENGINE_CONFIG.GALAXY_RADIUS * Math.cbrt(Math.random())
      const theta = Math.random() * 2 * Math.PI
      const phi = Math.acos(2 * Math.random() - 1)
      
      stars.push({
        origX: r * Math.sin(phi) * Math.cos(theta),
        origY: r * Math.sin(phi) * Math.sin(theta) * 0.4, // Y轴压扁形成星系盘
        origZ: r * Math.cos(phi),
        baseSize: Math.random() * 1.5 + 0.8,
        color: palette[Math.floor(Math.random() * palette.length)],
        baseAlpha: Math.random() * 0.5 + 0.3,
        pulsePhase: Math.random() * Math.PI * 2,
        pulseSpeed: ENGINE_CONFIG.BREATH_SPEED_BASE + Math.random() * ENGINE_CONFIG.BREATH_SPEED_VAR,
        posX: centerX,
        posY: centerY,
        initialized: false
      })
    }
  }
  buildGalaxy()
  
  // 监听滤镜变化，重新染色
  watch(() => store.currentFilter, () => buildGalaxy())

  let angleY = 0
  let globalOffsetX = 0

  // ==========================================
  // 🎥 3. 核心 60fps 渲染循环
  // ==========================================
  const render = () => {
    // 拖影底色
    ctx.fillStyle = 'rgba(5, 5, 10, 0.2)'
    ctx.fillRect(0, 0, width, height)

    // 分析页：镜头平滑左移 25%
    const targetOffsetX = route.path === '/analysis' ? -width * 0.25 : 0
    globalOffsetX += (targetOffsetX - globalOffsetX) * 0.05 

    // 自转更新
    if (store.qualityMode) {
      angleY += ENGINE_CONFIG.ROTATION_SPEED 
    }
    
    const cosY = Math.cos(angleY)
    const sinY = Math.sin(angleY)

    // 🌟 降级策略：节能模式下只渲染前 600 颗星星
    const renderLimit = store.qualityMode ? ENGINE_CONFIG.STARS_COUNT_HIGH : ENGINE_CONFIG.STARS_COUNT_LOW

    for (let i = 0; i < renderLimit; i++) {
      const star = stars[i]

      // 3D 旋转矩阵计算
      const rotX = star.origX * cosY - star.origZ * sinY
      const rotZ = star.origZ * cosY + star.origX * sinY
      
      // 遮挡剔除：转到背面的星星不渲染
      if (rotZ > 0) {
        star.initialized = false
        continue
      }

      // 透视投影
      const distFromCamera = rotZ + ENGINE_CONFIG.GALAXY_RADIUS + 500
      const scale = ENGINE_CONFIG.FOCAL_LENGTH / distFromCamera 

      let targetX = centerX + rotX * scale + globalOffsetX
      let targetY = centerY + star.origY * scale

      // ⚡️ 性能优化：使用距离平方 (distSq) 避免每帧进行 2000 次开方运算！
      const dx = targetX - mouseX
      const dy = targetY - mouseY
      const distSq = dx * dx + dy * dy
      
      if (distSq < REPEL_RADIUS_SQ && distSq > 0.01) {
        const dist = Math.sqrt(distSq) // 只有进入引力圈，才进行耗时的开方运算
        const force = (ENGINE_CONFIG.REPEL_RADIUS - dist) / ENGINE_CONFIG.REPEL_RADIUS
        targetX += (dx / dist) * force * ENGINE_CONFIG.REPEL_STRENGTH
        targetY += (dy / dist) * force * ENGINE_CONFIG.REPEL_STRENGTH
      }

      // 平滑跟随插值
      if (!star.initialized) {
        star.posX = targetX
        star.posY = targetY
        star.initialized = true
      } else {
        star.posX += (targetX - star.posX) * ENGINE_CONFIG.FOLLOW_SPEED
        star.posY += (targetY - star.posY) * ENGINE_CONFIG.FOLLOW_SPEED
      }

      // 边缘平滑消隐
      let edgeFade = 1.0
      if (rotZ > ENGINE_CONFIG.EDGE_FADE_THRESHOLD) {
        edgeFade = Math.abs(rotZ) / Math.abs(ENGINE_CONFIG.EDGE_FADE_THRESHOLD)
      }

      // 呼吸闪烁 (仅性能模式下更新相位)
      let currentAlpha = star.baseAlpha
      if (store.qualityMode) {
        star.pulsePhase += star.pulseSpeed
        currentAlpha += Math.sin(star.pulsePhase) * 0.3
      }
      currentAlpha = currentAlpha * edgeFade

      // 原生 Canvas 渲染
      ctx.beginPath()
      ctx.arc(star.posX, star.posY, Math.max(0.1, star.baseSize * scale * 2), 0, Math.PI * 2)
      ctx.fillStyle = star.color
      ctx.globalAlpha = Math.max(0, Math.min(1, currentAlpha))

      // ⚡️ 性能降级：仅在开启性能模式、且距离镜头近(scale>0.2)、且透明度高时才渲染高耗能的阴影发光
      if (store.qualityMode && scale > 0.2 && currentAlpha > 0.1) {
        ctx.shadowBlur = 8 * scale
        ctx.shadowColor = star.color
      } else {
        ctx.shadowBlur = 0
      }
      ctx.fill()
    }

    animationId = requestAnimationFrame(render)
  }

  render()
}

onMounted(() => initEngine())
onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
  window.removeEventListener('mousemove', handleMouseMove)
})
</script>

<style scoped>
.native-nebula-wrapper {
  position: absolute; top: 0; left: 0; width: 100vw; height: 100vh; z-index: 1;
  background-color: #05050a;
}
.star-canvas { display: block; width: 100%; height: 100%; }
</style>