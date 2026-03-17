<!-- src/components/MouseGlow.vue -->
<template>
  <div
    class="mouse-glow"
    :style="{ left: x + 'px', top: y + 'px' }"
  ></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const x = ref(-1000)
const y = ref(-1000)

const handleMouseMove = (e) => {
  x.value = e.clientX
  y.value = e.clientY
}

onMounted(() => {
  window.addEventListener('mousemove', handleMouseMove)
})

onUnmounted(() => {
  window.removeEventListener('mousemove', handleMouseMove)
})
</script>

<style scoped>
.mouse-glow {
  position: absolute;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, var(--primary-faint) 0%, rgba(138,43,226,0.05) 40%, transparent 70%);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  pointer-events: none;
  z-index: 2;
  transition: top 0.1s ease-out, left 0.1s ease-out;
}
</style>