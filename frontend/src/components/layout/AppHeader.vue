<script setup lang="ts">
/**
 * 顶部导航栏组件
 * 简化版：汉堡菜单 + 标题
 */
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Fold, Expand } from '@element-plus/icons-vue'

// Props
defineProps<{
  sidebarCollapsed: boolean
  isMobile?: boolean
}>()

// Emits
const emit = defineEmits<{
  (e: 'toggleSidebar'): void
}>()

const route = useRoute()

// 页面标题映射
const pageTitles: Record<string, string> = {
  '/chat': '智能对话',
  '/calculator': '购房计算器',
  '/market': '市场分析',
  '/policy': '购房政策',
  '/profile': '我的'
}

// 当前页面标题
const pageTitle = computed(() => {
  return pageTitles[route.path] || '购房决策智能助手'
})

// 切换侧边栏
function toggleSidebar() {
  emit('toggleSidebar')
}
</script>

<template>
  <header class="app-header">
    <div class="header-left">
      <!-- 折叠/展开按钮 -->
      <el-button 
        text 
        class="toggle-btn"
        @click="toggleSidebar"
      >
        <el-icon :size="20">
          <Expand v-if="sidebarCollapsed" />
          <Fold v-else />
        </el-icon>
      </el-button>
      
      <!-- 页面标题 -->
      <span class="page-title">{{ pageTitle }}</span>
    </div>
  </header>
</template>

<style scoped lang="scss">
.app-header {
  height: 56px;
  padding: 0 16px;
  background: #ffffff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  flex-shrink: 0;
  
  .header-left {
    display: flex;
    align-items: center;
    gap: 12px;
    
    .toggle-btn {
      padding: 8px;
      color: #666;
      
      &:hover {
        color: #1890ff;
        background: #f5f7fa;
      }
    }
    
    .page-title {
      font-size: 16px;
      font-weight: 500;
      color: #333333;
    }
  }
}
</style>
