<script setup lang="ts">
/**
 * 城市选择器组件
 */
import { useCityStore, SUPPORTED_CITIES } from '@/stores/city'
import type { CityCode } from '@/stores/city'

const cityStore = useCityStore()

// 切换城市
function handleCityChange(city: CityCode) {
  cityStore.setCity(city)
}
</script>

<template>
  <el-select
    :model-value="cityStore.currentCity"
    placeholder="选择城市"
    size="small"
    style="width: 100px"
    @change="handleCityChange"
  >
    <el-option
      v-for="city in SUPPORTED_CITIES"
      :key="city.value"
      :label="city.label"
      :value="city.value"
    />
  </el-select>
</template>
