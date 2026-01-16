<script setup lang="ts">
/**
 * 侧边栏组件
 * 参考 DeepSeek 风格：对话记录在上 → 用户在下
 * 包含助手选择器
 */
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Plus, User, HomeFilled, Unlock, Collection, View, Shop, List } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useChatStore } from '@/stores/chat'
import { useAuthStore } from '@/stores/auth'
import ConversationList from './ConversationList.vue'

// 助手类型定义
interface Assistant {
  id: string
  name: string
  icon: any
  description: string
  available: boolean
}

// 可用的助手列表
const assistants: Assistant[] = [
  { id: 'purchase', name: '购房助手', icon: HomeFilled, description: '买房决策、贷款计算、政策咨询', available: true },
  { id: 'rental', name: '租房助手', icon: Unlock, description: '租房找房、租金估算、合同审查', available: false },
  { id: 'school', name: '学区房', icon: Collection, description: '学区匹配、学校查询、房源推荐', available: false },
  { id: 'inspection', name: '验房助手', icon: View, description: '收房验房、问题识别、维权指导', available: false },
  { id: 'commercial', name: '商业选址', icon: Shop, description: '商铺投资、人流分析、租金回报', available: false },
  { id: 'management', name: '租赁管理', icon: List, description: '租客管理、收租提醒、合同管理', available: false },
]

// 当前选中的助手
const currentAssistant = ref('purchase')

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

// 切换助手
function selectAssistant(id: string) {
  const assistant = assistants.find(a => a.id === id)
  if (assistant?.available) {
    currentAssistant.value = id
  } else if (assistant) {
    ElMessage.info(`${assistant.name}即将上线，敬请期待`)
  }
}
</script>

<template>
  <aside class="app-sidebar" :class="{ collapsed }">
    <!-- Logo 区域 -->
    <div class="sidebar-header">
      <div class="logo-section">
        <span v-show="!collapsed" class="logo-text">购房AI助手</span>
      </div>
    </div>
    
    <!-- 助手选择区域 -->
    <div class="sidebar-section assistant-section">
      <div v-show="!collapsed" class="section-header">
        <span class="section-title">智能助手</span>
      </div>
      <div class="assistant-list">
        <div 
          v-for="assistant in assistants"
          :key="assistant.id"
          class="assistant-item"
          :class="{ 
            active: currentAssistant === assistant.id,
            disabled: !assistant.available 
          }"
          :title="collapsed ? assistant.name : (assistant.available ? assistant.description : '即将上线')"
          @click="selectAssistant(assistant.id)"
        >
          <el-icon :size="16"><component :is="assistant.icon" /></el-icon>
          <span v-show="!collapsed" class="assistant-name">{{ assistant.name }}</span>
          <span v-show="!collapsed && !assistant.available" class="coming-soon">即将上线</span>
        </div>
      </div>
    </div>

    <!-- 对话记录（可滚动） -->
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

// 助手选择区域
.assistant-section {
  padding-bottom: 8px;
  
  .assistant-list {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
  
  .assistant-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    border-radius: 8px;
    cursor: pointer;
    color: #666;
    transition: all 0.2s;
    
    &:hover:not(.disabled) {
      background: #f3f4f6;
      color: #333;
    }
    
    &.active {
      background: #e6f4ff;
      color: #1890ff;
    }
    
    &.disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
    
    .assistant-name {
      flex: 1;
      font-size: 14px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    
    .coming-soon {
      font-size: 10px;
      color: #999;
      background: #f0f0f0;
      padding: 2px 6px;
      border-radius: 4px;
    }
  }
}

.conversations-section {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 0;
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
