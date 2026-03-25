<template>
  <div ref="chartRef" style="width: 100%; height: 100%;"></div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  isAlbum: { type: Boolean, required: true },
  bpmList: { type: Array, default: () =>[] }
})

const chartRef = ref(null)
let chart = null

const renderChart = () => {
  if (!chart) chart = echarts.init(chartRef.value, 'dark')
  
  const option = {
    backgroundColor: 'transparent',
    title: { text: props.isAlbum ? '曲目动能演进曲线' : '频域能量分布', textStyle: { fontSize: 14, color: '#00FFCC' }, top: 10, left: 10 },
    grid: { top: 40, bottom: 20, left: 30, right: 10 },
    xAxis: { type: 'category', show: false },
    yAxis: { type: 'value', show: true, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } } },
    series: props.isAlbum ?[{
      type: 'line', smooth: true, areaStyle: { color: 'rgba(0,255,204,0.1)' }, itemStyle: { color: '#00FFCC' },
      data: props.bpmList
    }] :[{
      type: 'bar', itemStyle: { color: '#B900FF' },
      data: Array.from({length: 15}, () => Math.random() * 100)
    }]
  }
  chart.setOption(option)
}

watch(() => props.isAlbum, renderChart)
watch(() => props.bpmList, renderChart, { deep: true })
onMounted(() => renderChart())
onUnmounted(() => chart?.dispose())
</script>