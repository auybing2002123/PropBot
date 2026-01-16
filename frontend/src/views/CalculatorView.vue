<script setup lang="ts">
/**
 * 计算器页面
 * 优化布局，与聊天页面风格统一
 */
import { ref } from 'vue'
import LoanForm from '@/components/calculator/LoanForm.vue'
import TaxForm from '@/components/calculator/TaxForm.vue'
import TotalCostForm from '@/components/calculator/TotalCostForm.vue'

const activeTab = ref('loan')
</script>

<template>
  <div class="calculator-view">
    <div class="calculator-container">
      <!-- 使用 v-show 保持组件实例，避免切换时重新渲染 -->
      <el-tabs v-model="activeTab" class="calculator-tabs">
        <el-tab-pane label="贷款计算" name="loan" lazy>
          <LoanForm />
        </el-tab-pane>
        <el-tab-pane label="税费计算" name="tax" lazy>
          <TaxForm />
        </el-tab-pane>
        <el-tab-pane label="总成本" name="total" lazy>
          <TotalCostForm />
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<style scoped lang="scss">
.calculator-view {
  height: 100%;
  overflow-y: auto;
  padding: 24px;
  background: #f5f7fa;
}

.calculator-container {
  max-width: 600px;
  margin: 0 auto;
}

.calculator-tabs {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);

  :deep(.el-tabs__header) {
    margin-bottom: 20px;
  }

  :deep(.el-tabs__nav-wrap::after) {
    height: 1px;
    background: #e5e7eb;
  }

  :deep(.el-tabs__item) {
    font-size: 14px;
    color: #666;
    
    &.is-active {
      color: #1890ff;
      font-weight: 500;
    }
  }

  :deep(.el-tabs__active-bar) {
    background-color: #1890ff;
  }
}
</style>
