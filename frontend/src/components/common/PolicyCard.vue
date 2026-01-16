<script setup lang="ts">
/**
 * 政策卡片组件
 */
import { useRouter } from 'vue-router'
import { Flag } from '@element-plus/icons-vue'

const props = defineProps<{
  title: string
  summary: string[]
  source: string
  updateTime: string
}>()

const router = useRouter()

// 跳转到对话页面咨询
function handleAskAI() {
  router.push({
    path: '/chat',
    query: { q: `请详细介绍一下${props.title}` }
  })
}
</script>

<template>
  <div class="policy-card">
    <div class="card-header">
      <el-icon :size="18" class="flag-icon">
        <Flag />
      </el-icon>
      <h3 class="title">{{ title }}</h3>
    </div>
    
    <div class="card-content">
      <div class="summary-title">【政策要点】</div>
      <ul class="summary-list">
        <li v-for="(item, index) in summary" :key="index">{{ item }}</li>
      </ul>
    </div>
    
    <div class="card-footer">
      <div class="meta">
        <span class="source">来源：{{ source }}</span>
        <span class="time">更新时间：{{ updateTime }}</span>
      </div>
      <el-button size="small" type="primary" text @click="handleAskAI">
        咨询 AI
      </el-button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.policy-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  
  .card-header {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    margin-bottom: 12px;
    
    .flag-icon {
      color: #1890ff;
      margin-top: 2px;
    }
    
    .title {
      font-size: 16px;
      font-weight: 600;
      color: #333;
      margin: 0;
      line-height: 1.4;
    }
  }
  
  .card-content {
    margin-bottom: 12px;
    
    .summary-title {
      font-size: 14px;
      font-weight: 500;
      color: #333;
      margin-bottom: 8px;
    }
    
    .summary-list {
      padding-left: 20px;
      margin: 0;
      
      li {
        font-size: 14px;
        color: #666;
        line-height: 1.8;
      }
    }
  }
  
  .card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 12px;
    border-top: 1px solid #ebeef5;
    
    .meta {
      display: flex;
      flex-direction: column;
      gap: 2px;
      
      .source, .time {
        font-size: 12px;
        color: #999;
      }
    }
  }
}
</style>
