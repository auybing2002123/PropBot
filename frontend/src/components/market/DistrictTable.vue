<script setup lang="ts">
/**
 * 区域对比表组件
 */
import { computed } from 'vue'
import { Bottom, Top } from '@element-plus/icons-vue'
import type { CityCode } from '@/stores/city'

const props = defineProps<{
  city: CityCode
}>()

// 模拟区域数据
const tableData = computed(() => {
  if (props.city === 'nanning') {
    return [
      { district: '青秀区', avgPrice: 15000, change: -0.5, volume: 320 },
      { district: '良庆区', avgPrice: 12000, change: -0.3, volume: 280 },
      { district: '西乡塘区', avgPrice: 10500, change: -0.8, volume: 150 },
      { district: '江南区', avgPrice: 11000, change: -0.6, volume: 180 },
      { district: '兴宁区', avgPrice: 9800, change: -1.0, volume: 120 }
    ]
  }
  return [
    { district: '城中区', avgPrice: 9500, change: -0.2, volume: 150 },
    { district: '鱼峰区', avgPrice: 8800, change: -0.4, volume: 120 },
    { district: '柳南区', avgPrice: 8000, change: -0.5, volume: 80 },
    { district: '柳北区', avgPrice: 7500, change: -0.3, volume: 70 }
  ]
})
</script>

<template>
  <el-table :data="tableData" stripe style="width: 100%">
    <el-table-column prop="district" label="区域" width="100" />
    <el-table-column prop="avgPrice" label="均价(元/㎡)" width="110">
      <template #default="{ row }">
        {{ row.avgPrice.toLocaleString() }}
      </template>
    </el-table-column>
    <el-table-column prop="change" label="环比" width="90">
      <template #default="{ row }">
        <span :style="{ color: row.change < 0 ? '#52c41a' : '#ff4d4f' }">
          <el-icon v-if="row.change < 0" :size="12"><Bottom /></el-icon>
          <el-icon v-else :size="12"><Top /></el-icon>
          {{ Math.abs(row.change) }}%
        </span>
      </template>
    </el-table-column>
    <el-table-column prop="volume" label="成交(套)" />
  </el-table>
</template>
