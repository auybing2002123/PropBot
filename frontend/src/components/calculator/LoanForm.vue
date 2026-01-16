<script setup lang="ts">
/**
 * 贷款计算表单组件
 */
import { ref, reactive } from 'vue'
import { calcLoan } from '@/api/calculator'
import { 
  DOWN_PAYMENT_OPTIONS, 
  LOAN_YEARS_OPTIONS, 
  REPAYMENT_METHOD_OPTIONS,
  CURRENT_RATES 
} from '@/types/calculator'
import type { LoanCalcParams, LoanCalcResult } from '@/types/calculator'
import ResultCard from './ResultCard.vue'

// 表单数据
const form = reactive<LoanCalcParams>({
  price: 1500000,
  down_payment_ratio: 0.3,
  years: 30,
  rate: CURRENT_RATES.commercial_first,
  method: 'equal_payment'
})

// 计算结果
const result = ref<LoanCalcResult | null>(null)
const loading = ref(false)

// 贷款类型（用于自动设置利率）
const loanType = ref<'commercial' | 'provident'>('commercial')

// 切换贷款类型时更新利率
function handleLoanTypeChange(type: 'commercial' | 'provident') {
  loanType.value = type
  if (type === 'commercial') {
    form.rate = CURRENT_RATES.commercial_first
  } else {
    form.rate = form.years > 5 ? CURRENT_RATES.provident_above_5y : CURRENT_RATES.provident_below_5y
  }
}

// 计算
async function handleCalculate() {
  loading.value = true
  try {
    result.value = await calcLoan(form)
  } catch (error) {
    console.error('贷款计算失败:', error)
  } finally {
    loading.value = false
  }
}

// 格式化金额
function formatMoney(value: number): string {
  return (value / 10000).toFixed(2) + ' 万元'
}
</script>

<template>
  <div class="loan-form">
    <el-form label-position="top">
      <el-form-item label="房屋总价">
        <el-input-number
          v-model="form.price"
          :min="100000"
          :max="100000000"
          :step="100000"
          :precision="0"
          style="width: 100%"
        />
        <span class="unit">元（{{ formatMoney(form.price) }}）</span>
      </el-form-item>
      
      <el-form-item label="首付比例">
        <el-radio-group v-model="form.down_payment_ratio">
          <el-radio-button 
            v-for="opt in DOWN_PAYMENT_OPTIONS" 
            :key="opt.value" 
            :value="opt.value"
          >
            {{ opt.label }}
          </el-radio-button>
        </el-radio-group>
      </el-form-item>
      
      <el-form-item label="贷款年限">
        <el-select v-model="form.years" style="width: 100%">
          <el-option
            v-for="opt in LOAN_YEARS_OPTIONS"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
          />
        </el-select>
      </el-form-item>
      
      <el-form-item label="贷款类型">
        <el-radio-group :model-value="loanType" @change="(val: string | number | boolean | undefined) => handleLoanTypeChange(val as 'commercial' | 'provident')">
          <el-radio-button value="commercial">商业贷款</el-radio-button>
          <el-radio-button value="provident">公积金贷款</el-radio-button>
        </el-radio-group>
      </el-form-item>
      
      <el-form-item label="年利率（%）">
        <el-input-number
          v-model="form.rate"
          :min="0.1"
          :max="10"
          :step="0.05"
          :precision="2"
          style="width: 100%"
        />
      </el-form-item>
      
      <el-form-item label="还款方式">
        <el-radio-group v-model="form.method">
          <el-radio-button 
            v-for="opt in REPAYMENT_METHOD_OPTIONS" 
            :key="opt.value" 
            :value="opt.value"
          >
            {{ opt.label }}
          </el-radio-button>
        </el-radio-group>
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
    <ResultCard v-if="result" title="贷款计算结果">
      <div class="result-grid">
        <div class="result-item">
          <span class="label">首付金额</span>
          <span class="value">{{ formatMoney(result.down_payment) }}</span>
        </div>
        <div class="result-item">
          <span class="label">贷款金额</span>
          <span class="value">{{ formatMoney(result.loan_amount) }}</span>
        </div>
        <div class="result-item highlight">
          <span class="label">月供金额</span>
          <span class="value">{{ result.monthly_payment.toFixed(2) }} 元</span>
        </div>
        <div class="result-item">
          <span class="label">支付利息</span>
          <span class="value">{{ formatMoney(result.total_interest) }}</span>
        </div>
        <div class="result-item">
          <span class="label">还款总额</span>
          <span class="value">{{ formatMoney(result.total_payment) }}</span>
        </div>
      </div>
    </ResultCard>
  </div>
</template>

<style scoped lang="scss">
.loan-form {
  .unit {
    margin-left: 8px;
    color: #999;
    font-size: 12px;
  }
  
  .result-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
    
    .result-item {
      display: flex;
      flex-direction: column;
      gap: 4px;
      
      .label {
        font-size: 12px;
        color: #999;
      }
      
      .value {
        font-size: 16px;
        font-weight: 600;
        color: #333;
      }
      
      &.highlight .value {
        color: #1890ff;
        font-size: 20px;
      }
    }
  }
}
</style>
