<template>
  <div ref="chartRef" style="width: 100%; height: 100%;"></div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({ mfccVector: { type: Array, required: true } })
const chartRef = ref(null)
let chart = null

const renderChart = () => {
  if (!chart) chart = echarts.init(chartRef.value, 'dark')
  const data = props.mfccVector.map((val, idx) => [idx, 0, val])
  const option = {
    backgroundColor: 'transparent', tooltip: { show: false },
    grid: { top: 0, bottom: 0, left: 0, right: 0 },
    xAxis: { type: 'category', show: false }, yAxis: { type: 'category', show: false },
    visualMap: { show: false, min: -50, max: 50, inRange: { color:['#0d0887', '#66bd63', '#f46d43', '#a50026'] } },
    series: [{ type: 'heatmap', data: data }]
  }
  chart.setOption(option)
}

watch(() => props.mfccVector, renderChart, { deep: true })
onMounted(() => renderChart())
onUnmounted(() => chart?.dispose())
</script>