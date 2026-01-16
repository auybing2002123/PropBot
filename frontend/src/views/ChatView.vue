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

const chatStore = useChatStore()
const authStore = useAuthStore()
const messageListRef = ref<HTMLElement | null>(null)

// 用户是否手动滚动（用于判断是否暂停自动滚动）
const userScrolledUp = ref(false)

// 引导问题列表（具体问题，点击直接发送）
const suggestQuestions = [
  '100万的房子首付30%月供多少？',
  '南宁外地人可以买几套房？',
  '青秀区和良庆区哪个更值得买？',
  '公积金贷款最多能贷多少？',
  '买二手房需要交哪些税费？',
  '首套房契税怎么算？',
  '南宁最新的购房政策有哪些？',
  '月收入1万能买多少钱的房？',
  '等额本息和等额本金哪个划算？',
  '我想在南宁买150万的房子，月入1.5万，现在是好时机吗'
]

// 发送消息
async function handleSend(content: string) {
  await chatStore.send(content, authStore.userId || undefined)
  await nextTick()
  scrollToBottom()
}

// 获取某条 AI 消息之前的用户问题
function getPreviousUserQuestion(messageId: string): string {
  const messages = chatStore.messages
  const index = messages.findIndex(m => m.id === messageId)
  if (index <= 0) return ''
  
  // 向前查找最近的用户消息
  for (let i = index - 1; i >= 0; i--) {
    if (messages[i].role === 'user') {
      return messages[i].content
    }
  }
  return ''
}

// 点击引导问题
function handleSuggestQuestion(question: string) {
  handleSend(question)
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
          <p class="welcome-subtitle">我是你的购房AI助手，有什么可以帮你的？</p>
          
          <!-- 引导问题标签 -->
          <div class="suggest-questions">
            <div 
              v-for="question in suggestQuestions" 
              :key="question"
              class="suggest-tag"
              @click="handleSuggestQuestion(question)"
            >
              {{ question }}
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
                :message-id="msg.id"
                :conversation-id="chatStore.conversationId || undefined"
                :user-question="getPreviousUserQuestion(msg.id)"
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
                :references="msg.references"
                @toggle-expert="chatStore.toggleExpertAnalysis(msg.id)"
                @toggle-thinking="chatStore.toggleMessageThinking(msg.id)"
                @send-question="handleSend"
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
  background: #ffffff;
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

// 引导问题标签 - 横向滚动的3行布局
.suggest-questions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px 16px;
  max-width: 100%;
  padding: 4px 0;
}

.suggest-tag {
  padding: 10px 20px;
  background: #f5f5f5;
  border-radius: 20px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  border: 1px solid #e8e8e8;
  
  &:hover {
    background: #ebebeb;
    border-color: #d9d9d9;
  }
}

// 移动端适配
@media (max-width: 768px) {
  .message-list {
    padding: 16px;
  }
  
  .welcome-container {
    padding: 16px;
    // 保持垂直居中
  }
  
  .welcome-content {
    .welcome-title {
      font-size: 24px;
    }
    
    .welcome-subtitle {
      font-size: 14px;
      margin-bottom: 32px;
    }
  }
  
  // 移动端问题：横向滚动的3行布局
  .suggest-questions {
    display: grid;
    grid-template-rows: repeat(3, auto);
    grid-auto-flow: column;
    grid-auto-columns: max-content;
    gap: 8px 10px;
    overflow-x: auto;
    overflow-y: hidden;
    flex-wrap: nowrap;
    justify-content: flex-start;
    padding: 4px 0;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
    
    &::-webkit-scrollbar {
      display: none;
    }
  }
  
  .suggest-tag {
    padding: 8px 14px;
    font-size: 13px;
    border-radius: 16px;
  }
  
  .input-area {
    padding: 12px 16px 16px;
  }
  
  .user-bubble {
    max-width: 85%;
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
  background: #ffffff;
  padding: 16px 24px 24px;
}
</style>
