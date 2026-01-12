<script setup lang="ts">
/**
 * 侧边栏组件
 * 参考 DeepSeek 风格：工具在上 → 对话记录在中 → 用户在下
 */
import { useRoute, useRouter } from 'vue-router'
import { 
  Plus, 
  DataAnalysis, 
  TrendCharts, 
  Document, 
  User
} from '@element-plus/icons-vue'
import { useChatStore } from '@/stores/chat'
import { useAuthStore } from '@/stores/auth'
import ConversationList from './ConversationList.vue'

// Props
defineProps<{
  collapsed: boolean
  isMobile?: boolean
}>()

// Emits
const emit = defineEmits<{
  (e: 'toggle'): void
  (e: 'newChat'): void
  (e: 'navigate'): void
}>()

const route = useRoute()
const router = useRouter()
const chatStore = useChatStore()
const authStore = useAuthStore()

// 工具菜单
const toolMenus = [
  { path: '/calculator', name: '计算器', icon: DataAnalysis },
  { path: '/market', name: '市场分析', icon: TrendCharts },
  { path: '/policy', name: '政策查询', icon: Document }
]

// 导航到工具页面
function navigateTo(path: string) {
  router.push(path)
  emit('navigate')
}

// 新建对话
function handleNewChat() {
  chatStore.clear()
  if (route.path !== '/chat') {
    router.push('/chat')
  }
  emit('newChat')
}

// 导航到设置/我的
function goToProfile() {
  router.push('/profile')
  emit('navigate')
}
</script>

<template>
  <aside class="app-sidebar" :class="{ collapsed }">
    <!-- Logo 区域 -->
    <div class="sidebar-header">
      <div class="logo-section">
        <span v-show="!collapsed" class="logo-text">购房决策助手</span>
      </div>
    </div>

    <!-- 工具菜单（放在最上面） -->
    <div class="sidebar-section tools-section">
      <div v-show="!collapsed" class="section-title">工具</div>
      <div class="menu-list">
        <div
          v-for="tool in toolMenus"
          :key="tool.path"
          class="menu-item"
          :class="{ active: route.path === tool.path }"
          :title="collapsed ? tool.name : ''"
          @click="navigateTo(tool.path)"
        >
          <el-icon :size="18">
            <component :is="tool.icon" />
          </el-icon>
          <span v-show="!collapsed" class="menu-name">{{ tool.name }}</span>
        </div>
      </div>
    </div>

    <!-- 对话记录（中间，可滚动） -->
    <div class="sidebar-section conversations-section">
      <div v-show="!collapsed" class="section-header">
        <span class="section-title">对话记录</span>
        <el-icon 
          class="section-action" 
          title="新建对话"
          @click="handleNewChat"
        >
          <Plus />
        </el-icon>
      </div>
      <ConversationList :collapsed="collapsed" @select="emit('navigate')" />
    </div>

    <!-- 底部用户区域 -->
    <div class="sidebar-footer">
      <div 
        class="user-item"
        :class="{ active: route.path === '/profile' }"
        :title="collapsed ? '我的' : ''"
        @click="goToProfile"
      >
        <div class="user-avatar">
          <el-icon :size="16">
            <User />
          </el-icon>
        </div>
        <span v-show="!collapsed" class="user-name">{{ authStore.nickname || authStore.username || '用户' }}</span>
      </div>
    </div>
  </aside>
</template>

<style scoped lang="scss">
.app-sidebar {
  width: 260px;
  height: 100%;
  background: #f9fafb;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  overflow: hidden;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;

  .logo-section {
    display: flex;
    align-items: center;

    .logo-text {
      font-size: 16px;
      font-weight: 600;
      color: #333;
      white-space: nowrap;
    }
  }
}

.sidebar-section {
  padding: 12px 16px;

  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
  }

  .section-title {
    font-size: 12px;
    color: #999;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .section-action {
    font-size: 20px;
    color: #666;
    cursor: pointer;
    padding: 4px;
    border-radius: 4px;
    transition: all 0.2s;

    &:hover {
      background: #e5e7eb;
      color: #1890ff;
    }
  }
}

.tools-section {
  border-bottom: 1px solid #e5e7eb;
}

.conversations-section {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.menu-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  color: #666;
  transition: all 0.2s;

  &:hover {
    background: #f3f4f6;
    color: #333;
  }

  &.active {
    background: #e5e7eb;
    color: #1890ff;
  }

  .menu-name {
    font-size: 14px;
    white-space: nowrap;
  }
}

.sidebar-footer {
  padding: 12px 8px;

  .user-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    border-radius: 8px;
    cursor: pointer;
    color: #666;
    transition: all 0.2s;

    &:hover {
      background: #f3f4f6;
      color: #333;
    }

    &.active {
      background: #e5e7eb;
      color: #1890ff;
    }

    .user-avatar {
      width: 28px;
      height: 28px;
      border-radius: 50%;
      background: #e5e7eb;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #666;
    }

    .user-name {
      font-size: 14px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }
}
</style>
