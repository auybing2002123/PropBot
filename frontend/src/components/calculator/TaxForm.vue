<script setup lang="ts">
/**
 * 税费计算表单组件
 */
import { ref, reactive } from 'vue'
import { calcTax } from '@/api/calculator'
import type { TaxCalcParams, TaxCalcResult } from '@/types/calculator'
import ResultCard from './ResultCard.vue'

// 表单数据
const form = reactive<TaxCalcParams>({
  price: 1500000,
  area: 100,
  is_first_home: true,
  house_age_years: 5
})

// 计算结果
const result = ref<TaxCalcResult | null>(null)
const loading = ref(false)

// 计算
async function handleCalculate() {
  loading.value = true
  try {
    result.value = await calcTax(form)
  } catch (error) {
    console.error('税费计算失败:', error)
  } finally {
    loading.value = false
  }
}

// 格式化金额
function formatMoney(value: number): string {
  if (value >= 10000) {
    return (value / 10000).toFixed(2) + ' 万元'
  }
  return value.toFixed(2) + ' 元'
}
</script>

<template>
  <div class="tax-form">
    <el-form label-position="top">
      <el-form-item label="房屋总价（元）">
        <el-input-number
          v-model="form.price"
          :min="100000"
          :max="100000000"
          :step="100000"
          :precision="0"
          style="width: 100%"
        />
      </el-form-item>
      
      <el-form-item label="房屋面积（平方米）">
        <el-input-number
          v-model="form.area"
          :min="10"
          :max="1000"
          :step="10"
          :precision="0"
          style="width: 100%"
        />
      </el-form-item>
      
      <el-form-item label="是否首套房">
        <el-radio-group v-model="form.is_first_home">
          <el-radio-button :value="true">首套房</el-radio-button>
          <el-radio-button :value="false">二套房</el-radio-button>
        </el-radio-group>
      </el-form-item>
      
      <el-form-item label="房龄（年）">
        <el-input-number
          v-model="form.house_age_years"
          :min="0"
          :max="50"
          :step="1"
          :precision="0"
          style="width: 100%"
        />
        <span class="hint">新房填 0，满2年可免增值税</span>
      </el-form-item>
      
      <el-form-item>
        <el-button 
          type="primary" 
          :loading="loading" 
          style="width: 100%"
          @click="handleCalculate"
        >
          计算
        </el-button>
      </el-form-item>
    </el-form>
    
    <!-- 计算结果 -->
    <ResultCard v-if="result" title="税费计算结果">
      <div class="result-list">
        <div class="result-item">
          <span class="label">契税</span>
          <span class="value">{{ formatMoney(result.deed_tax) }}</span>
        </div>
        <div class="result-item">
          <span class="label">增值税</span>
          <span class="value">{{ formatMoney(result.vat) }}</span>
        </div>
        <div class="result-item">
          <span class="label">个人所得税</span>
          <span class="value">{{ formatMoney(result.income_tax) }}</span>
        </div>
        <div class="result-item">
          <span class="label">中介费</span>
          <span class="value">{{ formatMoney(result.agent_fee) }}</span>
        </div>
        <div class="result-item total">
          <span class="label">税费总计</span>
          <span class="value">{{ formatMoney(result.total) }}</span>
        </div>
      </div>
    </ResultCard>
  </div>
</template>

<style scoped lang="scss">
.tax-form {
  .hint {
    display: block;
    margin-top: 4px;
    font-size: 12px;
    color: #999;
  }
  
  .result-list {
    .result-item {
      display: flex;
      justify-content: space-between;
      padding: 12px 0;
      border-bottom: 1px solid #ebeef5;
      
      &:last-child {
        border-bottom: none;
      }
      
      .label {
        color: #666;
      }
      
      .value {
        font-weight: 500;
        color: #333;
      }
      
      &.total {
        .label, .value {
          font-weight: 600;
          color: #1890ff;
          font-size: 16px;
        }
      }
    }
  }
}
</style>
