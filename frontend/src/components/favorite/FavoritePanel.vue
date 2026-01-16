<script setup lang="ts">
/**
 * 多功能浮动按钮组件
 * 主按钮：我的关注 + 小工具菜单
 */
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { 
  Star, 
  Close, 
  Delete, 
  ChatLineSquare,
  DataAnalysis,
  TrendCharts,
  Document,
  QuestionFilled,
  Plus
} from '@element-plus/icons-vue'
import { marked } from 'marked'
import { useFavoriteStore } from '@/stores/favorite'
import { useConversationStore } from '@/stores/conversation'

const router = useRouter()
const route = useRoute()
const favoriteStore = useFavoriteStore()
const conversationStore = useConversationStore()

// 关注面板是否展开
const favoriteExpanded = ref(false)

// 工具菜单是否展开
const toolsExpanded = ref(false)

// 当前展开查看的收藏ID
const expandedItemId = ref<string | null>(null)

// 收藏数量
const count = computed(() => favoriteStore.count)

// 工具菜单项
const toolMenus = [
  { path: '/calculator', name: '计算器', icon: DataAnalysis },
  { path: '/market', name: '市场分析', icon: TrendCharts },
  { path: '/policy', name: '政策查询', icon: Document },
  { path: '/help', name: '帮助中心', icon: QuestionFilled }
]

// 切换关注面板
function toggleFavorite() {
  favoriteExpanded.value = !favoriteExpanded.value
  if (favoriteExpanded.value) {
    toolsExpanded.value = false
    if (!favoriteStore.loaded) {
      favoriteStore.fetchFavorites()
    }
  }
}

// 切换工具菜单
function toggleTools() {
  toolsExpanded.value = !toolsExpanded.value
  if (toolsExpanded.value) {
    favoriteExpanded.value = false
  }
}

// 处理工具点击
function handleToolClick(path: string) {
  if (route.path === path) {
    router.push('/chat')
  } else {
    router.push(path)
  }
  toolsExpanded.value = false
}

// 关闭关注面板
function closeFavoritePanel() {
  favoriteExpanded.value = false
}

// 关闭工具菜单
function closeTools() {
  toolsExpanded.value = false
}

// 切换展开收藏项
function toggleItem(id: string) {
  expandedItemId.value = expandedItemId.value === id ? null : id
}

// 删除收藏
async function handleDelete(id: string, event: Event) {
  event.stopPropagation()
  await favoriteStore.remove(id)
}

// 跳转到原对话
async function handleJump(conversationId: string | undefined, event: Event) {
  event.stopPropagation()
  if (!conversationId) return
  
  // 加载对应对话
  await conversationStore.loadConversation(conversationId)
  router.push('/chat')
  closeFavoritePanel()
}

// 渲染 Markdown
function renderMarkdown(content: string): string {
  return marked(content, { breaks: true }) as string
}

// 格式化时间
function formatTime(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`
  
  return date.toLocaleDateString()
}

onMounted(() => {
  // 预加载收藏列表
  if (!favoriteStore.loaded) {
    favoriteStore.fetchFavorites()
  }
})
</script>

<template>
  <div class="fab-wrapper">
    <!-- 按钮组 -->
    <div class="fab-group">
      <!-- 主按钮：我的关注 -->
      <div 
        class="main-fab"
        :class="{ active: favoriteExpanded }"
        @click="toggleFavorite"
      >
        <el-icon :size="20">
          <Star />
        </el-icon>
        <span v-if="count > 0" class="fab-badge">{{ count > 99 ? '99+' : count }}</span>
      </div>
      
      <!-- 小工具按钮 -->
      <div 
        class="tools-fab"
        :class="{ active: toolsExpanded }"
        @click="toggleTools"
      >
        <el-icon :size="16">
          <Plus />
        </el-icon>
      </div>
    </div>
    
    <!-- 工具卡片 -->
    <transition name="tools-slide">
      <div v-if="toolsExpanded" class="tools-card">
        <div class="tools-header">
          <span class="tools-title">小工具</span>
          <el-button text class="close-btn" @click="closeTools">
            <el-icon><Close /></el-icon>
          </el-button>
        </div>
        <div class="tools-grid">
          <div
            v-for="tool in toolMenus"
            :key="tool.path"
            class="tool-item"
            :class="{ active: route.path === tool.path }"
            @click="handleToolClick(tool.path)"
          >
            <div class="tool-icon">
              <el-icon :size="20">
                <component :is="tool.icon" />
              </el-icon>
            </div>
            <span class="tool-name">{{ tool.name }}</span>
          </div>
        </div>
      </div>
    </transition>
    
    <!-- 关注面板 -->
    <transition name="panel-slide">
      <div v-if="favoriteExpanded" class="favorite-panel">
        <div class="panel-header">
          <span class="panel-title">我的关注</span>
          <el-button text class="close-btn" @click="closeFavoritePanel">
            <el-icon><Close /></el-icon>
          </el-button>
        </div>
        
        <div class="panel-content">
          <div v-if="favoriteStore.loading" class="loading-state">
            加载中...
          </div>
          
          <div v-else-if="favoriteStore.favorites.length === 0" class="empty-state">
            <el-icon :size="40" color="#ccc"><Star /></el-icon>
            <p>暂无关注</p>
            <p class="tip">点击对话中的星标图标关注问答</p>
          </div>
          
          <div v-else class="favorite-list">
            <div 
              v-for="item in favoriteStore.favorites"
              :key="item.id"
              class="favorite-item"
              :class="{ expanded: expandedItemId === item.id }"
            >
              <div class="item-header" @click="toggleItem(item.id)">
                <div class="item-question">{{ item.question }}</div>
                <div class="item-actions">
                  <el-button 
                    v-if="item.conversation_id"
                    text 
                    size="small"
                    title="跳转到原对话"
                    @click="handleJump(item.conversation_id, $event)"
                  >
                    <el-icon><ChatLineSquare /></el-icon>
                  </el-button>
                  <el-button 
                    text 
                    size="small"
                    title="删除"
                    @click="handleDelete(item.id, $event)"
                  >
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
              
              <div class="item-meta">
                <span class="item-time">{{ formatTime(item.created_at) }}</span>
              </div>
              
              <el-collapse-transition>
                <div v-show="expandedItemId === item.id" class="item-answer">
                  <div class="answer-content markdown-content" v-html="renderMarkdown(item.answer)"></div>
                </div>
              </el-collapse-transition>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped lang="scss">
.fab-wrapper {
  position: fixed;
  right: 32px;
  bottom: 100px;
  z-index: 200;
}

// 移动端适配
@media (max-width: 768px) {
  .fab-wrapper {
    right: 16px;
    bottom: 180px;
  }
  
  .main-fab {
    width: 44px;
    height: 44px;
  }
  
  .tools-fab {
    width: 32px;
    height: 32px;
  }
  
  .tools-card {
    width: calc(100vw - 32px);
    max-width: 280px;
    right: 0;
    bottom: 56px;
  }
  
  .favorite-panel {
    width: calc(100vw - 32px);
    max-width: 360px;
    right: 0;
    bottom: 56px;
  }
}

// 按钮组
.fab-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

// 主按钮：我的关注
.main-fab {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #fff;
  border: 1px solid #e5e7eb;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  color: #666;
  
  &:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
    color: #faad14;
  }
  
  &.active {
    background: #faad14;
    border-color: #faad14;
    color: #fff;
  }
  
  .fab-badge {
    position: absolute;
    top: -4px;
    right: -4px;
    min-width: 18px;
    height: 18px;
    padding: 0 5px;
    font-size: 11px;
    line-height: 18px;
    text-align: center;
    background: #f56c6c;
    color: #fff;
    border-radius: 9px;
  }
}

// 小工具按钮
.tools-fab {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #fff;
  border: 1px solid #e5e7eb;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  color: #999;
  
  &:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
    color: #1890ff;
  }
  
  &.active {
    background: #1890ff;
    border-color: #1890ff;
    color: #fff;
    transform: rotate(45deg);
  }
}

// 工具卡片
.tools-card {
  position: absolute;
  right: 0;
  bottom: 60px;
  width: 280px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.tools-header {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  
  .tools-title {
    font-size: 14px;
    font-weight: 500;
    color: #333;
  }
  
  .close-btn {
    padding: 4px;
    color: #999;
    
    &:hover {
      color: #666;
    }
  }
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1px;
  background: #f0f0f0;
  padding: 1px;
}

.tool-item {
  background: #fff;
  padding: 20px 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    background: #f5f7fa;
  }
  
  &.active {
    background: #e6f4ff;
    
    .tool-icon {
      color: #1890ff;
    }
  }
  
  .tool-icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #f5f7fa;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #666;
    transition: all 0.2s;
  }
  
  .tool-name {
    font-size: 12px;
    color: #666;
  }
}

// 工具卡片动画
.tools-slide-enter-active,
.tools-slide-leave-active {
  transition: all 0.25s ease;
}

.tools-slide-enter-from,
.tools-slide-leave-to {
  opacity: 0;
  transform: translateY(10px) scale(0.95);
}

// 收藏面板
.favorite-panel {
  position: absolute;
  right: 0;
  bottom: 60px;
  width: 360px;
  max-height: 500px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  
  .panel-title {
    font-size: 15px;
    font-weight: 500;
    color: #333;
  }
  
  .close-btn {
    padding: 4px;
    color: #999;
    
    &:hover {
      color: #666;
    }
  }
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.loading-state,
.empty-state {
  padding: 40px 20px;
  text-align: center;
  color: #999;
  
  p {
    margin: 8px 0 0;
  }
  
  .tip {
    font-size: 12px;
    color: #bbb;
  }
}

// 收藏列表
.favorite-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.favorite-item {
  background: #fafafa;
  border-radius: 8px;
  overflow: hidden;
  transition: background 0.2s;
  
  &:hover {
    background: #f5f5f5;
  }
  
  &.expanded {
    background: #f0f7ff;
  }
}

.item-header {
  padding: 10px 12px;
  display: flex;
  align-items: flex-start;
  gap: 8px;
  cursor: pointer;
  
  .item-question {
    flex: 1;
    font-size: 13px;
    color: #333;
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  
  .item-actions {
    display: flex;
    gap: 2px;
    opacity: 0;
    transition: opacity 0.2s;
    
    .el-button {
      padding: 4px;
      color: #999;
      
      &:hover {
        color: #1890ff;
      }
    }
  }
  
  &:hover .item-actions {
    opacity: 1;
  }
}

.item-meta {
  padding: 0 12px 8px;
  
  .item-time {
    font-size: 11px;
    color: #bbb;
  }
}

.item-answer {
  padding: 0 12px 12px;
  
  .answer-content {
    padding: 10px;
    background: #fff;
    border-radius: 6px;
    font-size: 12px;
    color: #555;
    line-height: 1.6;
    max-height: 200px;
    overflow-y: auto;
    
    :deep(p) {
      margin-bottom: 6px;
      
      &:last-child {
        margin-bottom: 0;
      }
    }
    
    :deep(ul), :deep(ol) {
      padding-left: 16px;
      margin-bottom: 6px;
    }
    
    :deep(li) {
      margin-bottom: 2px;
    }
  }
}

// 面板滑入动画
.panel-slide-enter-active,
.panel-slide-leave-active {
  transition: all 0.25s ease;
}

.panel-slide-enter-from,
.panel-slide-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}
</style>
