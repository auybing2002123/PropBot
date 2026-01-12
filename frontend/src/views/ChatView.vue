<script setup lang="ts">
/**
 * 对话页面
 * 参考 DeepSeek 风格的美观设计
 */
import { ref, nextTick, onMounted, onUnmounted, watch } from 'vue'
import { useChatStore } from '@/stores/chat'
import { useAuthStore } from '@/stores/auth'
import RoleMessage from '@/components/chat/RoleMessage.vue'
import ChatInput from '@/components/chat/ChatInput.vue'
import { 
  Coin, 
  Document, 
  TrendCharts, 
  QuestionFilled 
} from '@element-plus/icons-vue'

const chatStore = useChatStore()
const authStore = useAuthStore()
const messageListRef = ref<HTMLElement | null>(null)

// 用户是否手动滚动（用于判断是否暂停自动滚动）
const userScrolledUp = ref(false)

// 快捷功能卡片
const quickCards = [
  { 
    icon: Coin, 
    title: '贷款计算', 
    desc: '计算月供、利息、还款方案',
    query: '我想买一套100万的房子，首付30%，贷款30年，帮我算一下月供是多少？'
  },
  { 
    icon: Document, 
    title: '政策解读', 
    desc: '限购、公积金、税费政策',
    query: '南宁现在的限购政策是什么？外地人可以买房吗？'
  },
  { 
    icon: TrendCharts, 
    title: '市场分析', 
    desc: '房价走势、区域对比',
    query: '南宁目前的房价走势如何？哪个区域比较有投资价值？'
  },
  { 
    icon: QuestionFilled, 
    title: '购房咨询', 
    desc: '首套房、二手房、流程指南',
    query: '我是首次购房，需要准备哪些材料？购房流程是怎样的？'
  }
]

// 发送消息
async function handleSend(content: string) {
  await chatStore.send(content, authStore.userId || undefined)
  await nextTick()
  scrollToBottom()
}

// 点击快捷卡片
function handleQuickCard(query: string) {
  handleSend(query)
}

// 滚动到底部
function scrollToBottom() {
  if (messageListRef.value) {
    messageListRef.value.scrollTop = messageListRef.value.scrollHeight
  }
}

// 检测用户是否在底部附近（阈值 100px）
function isNearBottom(): boolean {
  if (!messageListRef.value) return true
  const { scrollTop, scrollHeight, clientHeight } = messageListRef.value
  return scrollHeight - scrollTop - clientHeight < 100
}

// 处理滚动事件，检测用户是否手动往上滚动
function handleScroll() {
  if (!chatStore.isLoading) {
    // 不在加载中，重置状态
    userScrolledUp.value = false
    return
  }
  // 加载中时，检测用户是否滚离底部
  userScrolledUp.value = !isNearBottom()
}

// 监听消息数量变化，自动滚动（新消息时重置用户滚动状态）
watch(() => chatStore.messages.length, () => {
  userScrolledUp.value = false  // 新消息时重置，自动滚动到底部
  nextTick(() => scrollToBottom())
})

// 监听最后一条消息的内容变化（流式输出时滚动）
watch(
  () => {
    const msgs = chatStore.messages
    if (msgs.length === 0) return ''
    const lastMsg = msgs[msgs.length - 1]
    return lastMsg.content
  },
  () => {
    // 只在加载中且用户没有手动往上滚动时自动滚动
    if (chatStore.isLoading && !userScrolledUp.value) {
      nextTick(() => scrollToBottom())
    }
  }
)

onMounted(() => {
  scrollToBottom()
})

// 页面卸载时停止生成
onUnmounted(() => {
  if (chatStore.isLoading) {
    chatStore.stopGeneration()
  }
})
</script>

<template>
  <div class="chat-view">
    <!-- 消息列表 -->
    <div ref="messageListRef" class="message-list" @scroll="handleScroll">
      <!-- 欢迎消息 -->
      <div v-if="chatStore.messages.length === 0" class="welcome-container">
        <div class="welcome-content">
          <!-- 欢迎语 -->
          <h1 class="welcome-title">Hi，{{ authStore.nickname || '欢迎使用' }}</h1>
          <p class="welcome-subtitle">我是你的购房决策助手，有什么可以帮你的？</p>
          
          <!-- 快捷功能卡片 -->
          <div class="quick-cards">
            <div 
              v-for="card in quickCards" 
              :key="card.title"
              class="quick-card"
              @click="handleQuickCard(card.query)"
            >
              <el-icon class="card-icon" :size="20">
                <component :is="card.icon" />
              </el-icon>
              <div class="card-content">
                <div class="card-title">{{ card.title }}</div>
                <div class="card-desc">{{ card.desc }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 消息列表 -->
      <template v-else>
        <div class="messages-container">
          <template v-for="msg in chatStore.messages" :key="msg.id">
            <div
              class="message-item"
              :class="{ 'user-message': msg.role === 'user' }"
            >
              <!-- 用户消息 -->
              <div v-if="msg.role === 'user'" class="user-bubble">
                {{ msg.content }}
              </div>
              
              <!-- AI 角色消息 -->
              <RoleMessage
                v-else
                :role-id="msg.roleId"
                :role-name="msg.roleName"
                :role-icon="msg.roleIcon"
                :role-color="msg.roleColor"
                :content="msg.content"
                :loading="msg.loading"
                :is-summary="msg.isSummary"
                :expert-analysis="msg.expertAnalysis"
                :show-expert-analysis="msg.showExpertAnalysis"
                :thinking-steps="msg.thinkingSteps"
                :is-thinking="msg.loading && chatStore.isThinking"
                :show-thinking="msg.showThinking"
                @toggle-expert="chatStore.toggleExpertAnalysis(msg.id)"
                @toggle-thinking="chatStore.toggleMessageThinking(msg.id)"
              />
            </div>
          </template>
        </div>
      </template>
    </div>
    
    <!-- 输入区域 -->
    <div class="input-area">
      <ChatInput 
        :loading="chatStore.isLoading"
        :deep-mode="chatStore.deepMode"
        @send="handleSend"
        @stop="chatStore.stopGeneration"
        @update:deep-mode="chatStore.setDeepMode"
      />
    </div>
  </div>
</template>

<style scoped lang="scss">
.chat-view {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  padding-bottom: 0;
}

// 欢迎页面样式
.welcome-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100%;
  padding: 24px;
}

.welcome-content {
  text-align: center;
  max-width: 700px;
  width: 100%;

  .welcome-title {
    font-size: 28px;
    font-weight: 600;
    color: #333;
    margin-bottom: 8px;
  }

  .welcome-subtitle {
    font-size: 16px;
    color: #666;
    margin-bottom: 40px;
  }
}

// 快捷功能卡片
.quick-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  
  @media (max-width: 600px) {
    grid-template-columns: 1fr;
  }
}

.quick-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;

  &:hover {
    border-color: #1890ff;
    box-shadow: 0 4px 12px rgba(24, 144, 255, 0.1);
    transform: translateY(-2px);
  }

  .card-icon {
    color: #1890ff;
    flex-shrink: 0;
    margin-top: 2px;
  }

  .card-content {
    flex: 1;
    min-width: 0;

    .card-title {
      font-size: 14px;
      font-weight: 500;
      color: #333;
      margin-bottom: 4px;
    }

    .card-desc {
      font-size: 12px;
      color: #999;
    }
  }
}

// 消息列表样式
.messages-container {
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
}

.message-item {
  margin-bottom: 20px;
  
  &.user-message {
    display: flex;
    justify-content: flex-end;
  }
}

.user-bubble {
  background: #1890ff;
  color: #ffffff;
  padding: 12px 16px;
  border-radius: 16px 16px 4px 16px;
  max-width: 70%;
  word-break: break-word;
  font-size: 14px;
  line-height: 1.6;
}

// 输入区域
.input-area {
  background: #f5f7fa;
  padding: 16px 24px 24px;
}
</style>
