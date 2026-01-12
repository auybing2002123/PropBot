<script setup lang="ts">
/**
 * 计算结果卡片组件
 */
import { DataLine } from '@element-plus/icons-vue'

defineProps<{
  title: string
}>()
</script>

<template>
  <div class="result-card">
    <div class="card-header">
      <el-icon :size="18">
        <DataLine />
      </el-icon>
      <span class="title">{{ title }}</span>
    </div>
    <div class="card-content">
      <slot />
    </div>
  </div>
</template>

<style scoped lang="scss">
.result-card {
  margin-top: 24px;
  background: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
  
  .card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
    
    .el-icon {
      color: #1890ff;
    }
    
    .title {
      font-size: 16px;
      font-weight: 600;
      color: #333;
    }
  }
  
  .card-content {
    background: #fff;
    border-radius: 8px;
    padding: 16px;
  }
}
</style>
