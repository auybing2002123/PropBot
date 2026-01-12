<script setup lang="ts">
/**
 * 市场分析页面
 * 优化布局，与整体风格统一
 */
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCityStore, CITY_DISTRICTS } from '@/stores/city'
import DataCard from '@/components/market/DataCard.vue'
import PriceChart from '@/components/market/PriceChart.vue'
import DistrictTable from '@/components/market/DistrictTable.vue'

const router = useRouter()
const cityStore = useCityStore()

// 当前选中区域
const currentDistrict = ref('')

// 获取区域列表
const districts = computed(() => CITY_DISTRICTS[cityStore.currentCity] || [])

// 模拟市场数据
const marketData = computed(() => {
  if (cityStore.currentCity === 'nanning') {
    return {
      avgPrice: 12500,
      priceChange: -0.5,
      volume: 850,
      inventory: 18
    }
  }
  return {
    avgPrice: 8500,
    priceChange: -0.3,
    volume: 420,
    inventory: 22
  }
})

// 跳转到对话页面咨询
function handleAskAI() {
  router.push({
    path: '/chat',
    query: { q: '现在是买房的好时机吗？市场行情怎么样？' }
  })
}
</script>

<template>
  <div class="market-view">
    <div class="market-container">
      <!-- 区域筛选 -->
      <div class="filter-bar">
        <el-select 
          v-model="currentDistrict" 
          placeholder="全部区域"
          clearable
          size="default"
        >
          <el-option
            v-for="d in districts"
            :key="d"
            :label="d"
            :value="d"
          />
        </el-select>
      </div>

      <!-- 数据卡片 -->
      <div class="data-cards">
        <DataCard 
          title="均价" 
          :value="marketData.avgPrice" 
          unit="元/㎡"
        />
        <DataCard 
          title="环比" 
          :value="marketData.priceChange" 
          unit="%" 
          :trend="marketData.priceChange < 0 ? 'down' : 'up'"
        />
        <DataCard 
          title="成交量" 
          :value="marketData.volume" 
          unit="套/月"
        />
        <DataCard 
          title="去化周期" 
          :value="marketData.inventory" 
          unit="个月"
        />
      </div>
      
      <!-- 房价走势图 -->
      <div class="section-card">
        <h3>房价走势</h3>
        <PriceChart :city="cityStore.currentCity" />
      </div>
      
      <!-- 区域对比表 -->
      <div class="section-card">
        <h3>区域对比</h3>
        <DistrictTable :city="cityStore.currentCity" />
      </div>
      
      <!-- 咨询按钮 -->
      <div class="ask-ai">
        <el-button type="primary" round @click="handleAskAI">
          咨询 AI：现在是买房好时机吗？
        </el-button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.market-view {
  height: 100%;
  overflow-y: auto;
  padding: 24px;
  background: #f5f7fa;
}

.market-container {
  max-width: 800px;
  margin: 0 auto;
}

.filter-bar {
  margin-bottom: 16px;
  
  .el-select {
    width: 140px;
  }
}

.data-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 16px;
  
  @media (max-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
  }
}

.section-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  
  h3 {
    font-size: 15px;
    font-weight: 600;
    color: #333;
    margin: 0 0 16px 0;
  }
}

.ask-ai {
  text-align: center;
  padding: 8px 0 16px;
}
</style>
