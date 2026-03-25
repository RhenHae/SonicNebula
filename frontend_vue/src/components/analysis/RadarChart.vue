<template>
  <div ref="chartRef" style="width: 100%; height: 100%;"></div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  currentVector: { type: Array, required: true },
  avgVector: { type: Array, required: true },
  genreName: { type: String, required: true }
})

const chartRef = ref(null)
let chart = null

const renderChart = () => {
  if (!chart) chart = echarts.init(chartRef.value, 'dark')
  
  const option = {
    backgroundColor: 'transparent',
    
    // 💡 核心修复：掌控 Tooltip 的命运
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(15, 15, 20, 0.95)',
      borderColor: 'rgba(0, 255, 204, 0.3)',
      textStyle: { color: '#fff', fontSize: 12 },
      // 重要：强制 Tooltip 直接挂载在 body 上，脱离 ECharts 容器的层级限制，彻底解决被导航栏遮挡的 Bug
      appendToBody: true,
      
      // 1. 强制将其固定在鼠标的右下方，偏移 15px 避免挡住准星，彻底解决遮挡导航栏的 Bug
      position: function (point) {
        return [point[0] + 15, point[1] + 15]
      },
      
      // 2. 自定义格式化器，扼杀所有冗长的小数点
      formatter: function (params) {
        // params.name 是 "当前特征" 或 "[Jazz] 均值参考"
        let res = `<div style="margin-bottom:8px;font-weight:bold;color:#00FFCC;">${params.name}</div>`
        
        // 这里的指标必须和下面的 radar.indicator 一致
        const indicators =['能量', '明暗', '质心', '粗糙度', '中频', '高频']
        
        // 遍历数组，保留 1 位小数
        for (let i = 0; i < params.value.length; i++) {
          // 如果数据是空的（比如还没加载），显示 N/A
          const val = params.value[i] !== undefined ? parseFloat(params.value[i]).toFixed(1) : 'N/A'
          res += `<div style="display:flex; justify-content:space-between; width:150px; margin-bottom:4px;">
                    <span style="color:#aaa;">${indicators[i]}</span>
                    <span style="font-family:monospace; font-weight:bold;">${val}</span>
                  </div>`
        }
        return res
      }
    },
    
    legend: { show: false }, // 隐藏图例防误触
    
    radar: {
      indicator:[ 
        { name: '能量' }, { name: '明暗' }, { name: '质心' }, 
        { name: '粗糙度' }, { name: '中频' }, { name: '高频' } 
      ],
      axisName: { show: false }, // 隐藏多边形周围的文字
      center:['50%', '50%'], 
      radius: '75%', 
      
      splitArea: { show: false }, 
      axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.15)' } }, 
      splitLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.15)' } }
    },
    
    series:[{
      type: 'radar',
      data:[
        { 
          value: props.currentVector, 
          name: '当前特征', 
          itemStyle: { color: '#00FFCC' }, 
          areaStyle: { color: 'rgba(0, 255, 204, 0.4)' } 
        },
        { 
          value: props.avgVector, 
          name: `[${props.genreName}] 均值参考`, 
          itemStyle: { color: 'gray' }, 
          lineStyle: { type: 'dashed', width: 1.5 } 
        }
      ]
    }]
  }
  
  chart.setOption(option)
}

watch(() => props.currentVector, renderChart, { deep: true })
onMounted(() => renderChart())
onUnmounted(() => chart?.dispose())
</script>