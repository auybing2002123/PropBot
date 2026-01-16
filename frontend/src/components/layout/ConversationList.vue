<script setup lang="ts">
/**
 * 对话记录列表组件
 */
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ChatDotRound, Delete } from '@element-plus/icons-vue'
import { useChatStore } from '@/stores/chat'
import { useConversationStore, type Conversation } from '@/stores/conversation'
import { ElMessageBox, ElMessage } from 'element-plus'

// Props
defineProps<{
  collapsed: boolean
}>()

// Emits
const emit = defineEmits<{
  (e: 'select'): void
}>()

const router = useRouter()
const chatStore = useChatStore()
const conversationStore = useConversationStore()

// 悬停的对话 ID
const hoverConvId = ref<string | null>(null)

// 按时间分组的对话列表
const groupedConversations = computed(() => {
  const conversations = conversationStore.conversations
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000)
  const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)

  const groups: { title: string; items: Conversation[] }[] = [
    { title: '今天', items: [] },
    { title: '昨天', items: [] },
    { title: '最近7天', items: [] },
    { title: '更早', items: [] }
  ]

  conversations.forEach(conv => {
    const convDate = new Date(conv.updated_at)
    if (convDate >= today) {
      groups[0].items.push(conv)
    } else if (convDate >= yesterday) {
      groups[1].items.push(conv)
    } else if (convDate >= weekAgo) {
      groups[2].items.push(conv)
    } else {
      groups[3].items.push(conv)
    }
  })

  // 过滤掉空分组
  return groups.filter(g => g.items.length > 0)
})

// 当前选中的对话 ID
const currentConvId = computed(() => chatStore.conversationId)

// 加载对话列表
onMounted(async () => {
  await conversationStore.loadConversations()
})

// 选择对话
async function selectConversation(convId: string) {
  // 如果当前不在聊天页面，或者选择了不同的对话，则加载对话
  const isOnChatPage = router.currentRoute.value.path === '/chat'
  const isSameConversation = convId === currentConvId.value
  
  // 如果在聊天页面且是同一个对话，不做任何操作
  if (isOnChatPage && isSameConversation) return
  
  // 加载对话内容
  await conversationStore.loadConversation(convId)
  
  // 如果不在聊天页面，跳转过去
  if (!isOnChatPage) {
    router.push('/chat')
  }
  emit('select')
}

// 删除对话
async function deleteConversation(convId: string, event: Event) {
  event.stopPropagation()
  
  try {
    await ElMessageBox.confirm('确定要删除这个对话吗？', '删除确认', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await conversationStore.deleteConversation(convId)
    ElMessage.success('删除成功')
    
    // 如果删除的是当前对话，清空聊天
    if (convId === currentConvId.value) {
      chatStore.clear()
    }
  } catch {
    // 用户取消
  }
}

// 获取对话标题（截取前20个字符）
function getConvTitle(conv: { title?: string; id: string }): string {
  if (conv.title) {
    return conv.title.length > 20 ? conv.title.slice(0, 20) + '...' : conv.title
  }
  return '新对话'
}
</script>

<template>
  <div class="conversation-list">
    <template v-if="groupedConversations.length > 0">
      <div 
        v-for="group in groupedConversations" 
        :key="group.title"
        class="conv-group"
      >
        <div v-show="!collapsed" class="group-title">{{ group.title }}</div>
        <div class="group-items">
          <div
            v-for="conv in group.items"
            :key="conv.id"
            class="conv-item"
            :class="{ active: conv.id === currentConvId }"
            :title="collapsed ? getConvTitle(conv) : ''"
            @click="selectConversation(conv.id)"
            @mouseenter="hoverConvId = conv.id"
            @mouseleave="hoverConvId = null"
          >
            <el-icon v-if="collapsed" :size="18">
              <ChatDotRound />
            </el-icon>
            <template v-else>
              <span class="conv-title">{{ getConvTitle(conv) }}</span>
              <div 
                class="conv-actions"
                @click.stop
              >
                <el-icon 
                  :size="20" 
                  class="action-icon"
                  title="删除"
                  @click="deleteConversation(conv.id, $event)"
                >
                  <Delete />
                </el-icon>
              </div>
            </template>
          </div>
        </div>
      </div>
    </template>
    <div v-else class="empty-tip">
      <span v-show="!collapsed">暂无对话记录</span>
    </div>
  </div>
</template>

<style scoped lang="scss">
.conversation-list {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;

  &::-webkit-scrollbar {
    width: 4px;
  }

  &::-webkit-scrollbar-thumb {
    background: #d1d5db;
    border-radius: 2px;
  }
}

.conv-group {
  margin-bottom: 8px;

  .group-title {
    font-size: 11px;
    color: #9ca3af;
    padding: 4px 0;
    text-transform: uppercase;
  }
}

.group-items {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.conv-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 6px;
  cursor: pointer;
  color: #4b5563;
  transition: all 0.2s;
  position: relative;

  &:hover {
    background: #f3f4f6;
  }

  &.active {
    background: #e5e7eb;
    color: #1890ff;
  }

  .conv-icon {
    flex-shrink: 0;
  }

  .conv-title {
    flex: 1;
    font-size: 13px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    min-width: 0;
  }

  .conv-actions {
    display: flex;
    gap: 4px;
    flex-shrink: 0;
    opacity: 0;
    transition: opacity 0.2s;
    
    .action-icon {
      padding: 4px;
      border-radius: 4px;
      color: #9ca3af;
      
      &:hover {
        background: #e5e7eb;
        color: #ef4444;
      }
    }
  }

  &:hover .conv-actions {
    opacity: 1;
  }
}

.empty-tip {
  padding: 20px;
  text-align: center;
  color: #9ca3af;
  font-size: 13px;
}
</style>
