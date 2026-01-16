<script setup lang="ts">
/**
 * 房价走势图组件
 */
import { ref, onMounted, watch, computed } from 'vue'
import * as echarts from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { 
  GridComponent, 
  TooltipComponent, 
  LegendComponent 
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import type { CityCode } from '@/stores/city'

// 注册 ECharts 组件
echarts.use([LineChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer])

const props = defineProps<{
  city: CityCode
}>()

const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

// 模拟数据
const chartData = computed(() => {
  if (props.city === 'nanning') {
    return {
      years: ['2019', '2020', '2021', '2022', '2023', '2024'],
      prices: [11500, 12000, 13500, 14000, 13000, 12500]
    }
  }
  return {
    years: ['2019', '2020', '2021', '2022', '2023', '2024'],
    prices: [7500, 8000, 9000, 9500, 9000, 8500]
  }
})

// 初始化图表
function initChart() {
  if (!chartRef.value) return
  
  chartInstance = echarts.init(chartRef.value)
  updateChart()
}

// 更新图表
function updateChart() {
  if (!chartInstance) return
  
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: '{b}年<br/>均价: {c} 元/㎡'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: chartData.value.years,
      axisLine: { lineStyle: { color: '#e4e7ed' } },
      axisLabel: { color: '#666' }
    },
    yAxis: {
      type: 'value',
      name: '元/㎡',
      nameTextStyle: { color: '#999' },
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: '#ebeef5' } },
      axisLabel: { color: '#666' }
    },
    series: [{
      type: 'line',
      smooth: true,
      data: chartData.value.prices,
      itemStyle: { color: '#1890ff' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(24, 144, 255, 0.3)' },
          { offset: 1, color: 'rgba(24, 144, 255, 0.05)' }
        ])
      }
    }]
  }
  
  chartInstance.setOption(option)
}

// 监听城市变化
watch(() => props.city, () => {
  updateChart()
})

// 监听窗口大小变化
function handleResize() {
  chartInstance?.resize()
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})
</script>

<template>
  <div ref="chartRef" class="price-chart"></div>
</template>

<style scoped>
.price-chart {
  width: 100%;
  height: 250px;
}
</style>
