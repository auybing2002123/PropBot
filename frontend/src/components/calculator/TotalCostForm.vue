<script setup lang="ts">
/**
 * 总成本计算表单组件
 */
import { reactive, computed } from 'vue'
import ResultCard from './ResultCard.vue'

// 表单数据
const form = reactive({
  price: 1500000,        // 房屋总价
  down_payment: 450000,  // 首付
  total_interest: 800000, // 贷款利息
  taxes: 50000,          // 税费
  decoration: 150000,    // 装修
  furniture: 50000,      // 家具家电
  other_fees: 20000      // 其他费用
})

// 计算结果
const result = computed(() => {
  const initial_cost = form.down_payment + form.taxes
  const loan_cost = (form.price - form.down_payment) + form.total_interest
  const other_cost = form.decoration + form.furniture + form.other_fees
  const total_cost = form.price + form.total_interest + form.taxes + form.decoration + form.furniture + form.other_fees
  
  return {
    initial_cost,
    loan_cost,
    other_cost,
    total_cost
  }
})

// 格式化金额
function formatMoney(value: number): string {
  return (value / 10000).toFixed(2) + ' 万元'
}
</script>

<template>
  <div class="total-cost-form">
    <el-form label-position="top">
      <el-divider content-position="left">房屋信息</el-divider>
      
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
      
      <el-form-item label="首付金额（元）">
        <el-input-number
          v-model="form.down_payment"
          :min="0"
          :max="form.price"
          :step="10000"
          :precision="0"
          style="width: 100%"
        />
      </el-form-item>
      
      <el-form-item label="贷款总利息（元）">
        <el-input-number
          v-model="form.total_interest"
          :min="0"
          :max="10000000"
          :step="10000"
          :precision="0"
          style="width: 100%"
        />
      </el-form-item>
      
      <el-form-item label="税费总额（元）">
        <el-input-number
          v-model="form.taxes"
          :min="0"
          :max="1000000"
          :step="1000"
          :precision="0"
          style="width: 100%"
        />
      </el-form-item>
      
      <el-divider content-position="left">其他费用</el-divider>
      
      <el-form-item label="装修费用（元）">
        <el-input-number
          v-model="form.decoration"
          :min="0"
          :max="5000000"
          :step="10000"
          :precision="0"
          style="width: 100%"
        />
      </el-form-item>
      
      <el-form-item label="家具家电（元）">
        <el-input-number
          v-model="form.furniture"
          :min="0"
          :max="1000000"
          :step="5000"
          :precision="0"
          style="width: 100%"
        />
      </el-form-item>
      
      <el-form-item label="其他费用（元）">
        <el-input-number
          v-model="form.other_fees"
          :min="0"
          :max="500000"
          :step="1000"
          :precision="0"
          style="width: 100%"
        />
      </el-form-item>
    </el-form>
    
    <!-- 计算结果 -->
    <ResultCard title="购房总成本">
      <div class="result-list">
        <div class="result-item">
          <span class="label">初期投入（首付+税费）</span>
          <span class="value">{{ formatMoney(result.initial_cost) }}</span>
        </div>
        <div class="result-item">
          <span class="label">贷款成本（本金+利息）</span>
          <span class="value">{{ formatMoney(result.loan_cost) }}</span>
        </div>
        <div class="result-item">
          <span class="label">其他成本（装修+家具+其他）</span>
          <span class="value">{{ formatMoney(result.other_cost) }}</span>
        </div>
        <div class="result-item total">
          <span class="label">购房总成本</span>
          <span class="value">{{ formatMoney(result.total_cost) }}</span>
        </div>
      </div>
    </ResultCard>
  </div>
</template>

<style scoped lang="scss">
.total-cost-form {
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
        margin-top: 8px;
        padding-top: 16px;
        border-top: 2px solid #1890ff;
        border-bottom: none;
        
        .label, .value {
          font-weight: 600;
          color: #1890ff;
          font-size: 18px;
        }
      }
    }
  }
}
</style>
