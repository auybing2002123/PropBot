<script setup lang="ts">
/**
 * 数据卡片组件
 */
import { computed } from 'vue'
import { Bottom, Top } from '@element-plus/icons-vue'

const props = defineProps<{
  title: string
  value: number
  unit: string
  trend?: 'up' | 'down'
}>()

// 格式化数值
const formattedValue = computed(() => {
  if (props.value >= 10000) {
    return (props.value / 10000).toFixed(1) + '万'
  }
  return props.value.toLocaleString()
})

// 趋势颜色
const trendColor = computed(() => {
  if (props.trend === 'down') return '#52c41a'  // 下跌用绿色（对买家有利）
  if (props.trend === 'up') return '#ff4d4f'    // 上涨用红色
  return '#333'
})
</script>

<template>
  <div class="data-card">
    <div class="card-title">{{ title }}</div>
    <div class="card-value" :style="{ color: trend ? trendColor : '#333' }">
      <el-icon v-if="trend === 'down'" :size="16">
        <Bottom />
      </el-icon>
      <el-icon v-else-if="trend === 'up'" :size="16">
        <Top />
      </el-icon>
      <span>{{ formattedValue }}</span>
      <span class="unit">{{ unit }}</span>
    </div>
  </div>
</template>

<style scoped lang="scss">
.data-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  
  .card-title {
    font-size: 12px;
    color: #999;
    margin-bottom: 8px;
  }
  
  .card-value {
    display: flex;
    align-items: baseline;
    gap: 4px;
    font-size: 24px;
    font-weight: 600;
    
    .el-icon {
      align-self: center;
    }
    
    .unit {
      font-size: 12px;
      font-weight: 400;
      color: #999;
    }
  }
}
</style>
