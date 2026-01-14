<script setup lang="ts">
/**
 * 聊天输入框组件
 * 参考图片布局：输入框在上，功能按钮在下
 * 支持多助手切换（购房、租房、学区房、验房、商业选址、租赁管理）
 */
import { ref } from 'vue'
import { Promotion, VideoPause, HomeFilled, Unlock, Collection, View, Shop, List } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 助手类型定义
interface Assistant {
  id: string
  name: string
  icon: any
  description: string
  available: boolean  // 是否可用（后期开发）
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

// Props
const props = defineProps<{
  loading?: boolean
  deepMode?: boolean  // 深度分析模式（多专家协作）- 暂时隐藏
}>()

// Emits
const emit = defineEmits<{
  send: [content: string]
  stop: []
  'update:deepMode': [value: boolean]
}>()

const inputValue = ref('')
const currentAssistant = ref('purchase')  // 当前选中的助手

// 发送消息
function handleSend() {
  const content = inputValue.value.trim()
  if (!content) return
  
  emit('send', content)
  inputValue.value = ''
}

// 停止生成
function handleStop() {
  emit('stop')
}

// 按下回车发送
function handleKeydown(e: Event | KeyboardEvent) {
  const keyEvent = e as KeyboardEvent
  if (keyEvent.key === 'Enter' && !keyEvent.shiftKey) {
    e.preventDefault()
    handleSend()
  }
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

// 获取当前助手信息
function getCurrentAssistant() {
  return assistants.find(a => a.id === currentAssistant.value)
}
</script>

<template>
  <div class="chat-input-wrapper">
    <div class="chat-input-container">
      <!-- 输入框区域 -->
      <div class="input-area">
        <el-input
          v-model="inputValue"
          type="textarea"
          :rows="1"
          :autosize="{ minRows: 1, maxRows: 6 }"
          placeholder="有问题，尽管问，shift+enter换行"
          :disabled="loading"
          class="chat-textarea"
          @keydown="handleKeydown"
        />
      </div>
      
      <!-- 底部功能栏 -->
      <div class="action-bar">
        <div class="action-left">
          <!-- 助手选择器（替代原来的多专家协作按钮） -->
          <div class="assistant-selector">
            <div 
              v-for="assistant in assistants"
              :key="assistant.id"
              class="assistant-item"
              :class="{ 
                active: currentAssistant === assistant.id,
                disabled: !assistant.available 
              }"
              :title="assistant.available ? assistant.description : '即将上线'"
              @click="selectAssistant(assistant.id)"
            >
              <el-icon :size="14"><component :is="assistant.icon" /></el-icon>
              <span>{{ assistant.name }}</span>
            </div>
          </div>
        </div>
        
        <div class="action-right">
          <!-- 停止按钮（生成中显示） -->
          <el-button
            v-if="loading"
            type="danger"
            :icon="VideoPause"
            circle
            class="stop-btn"
            @click="handleStop"
          />
          <!-- 发送按钮 -->
          <el-button
            v-else
            type="primary"
            :icon="Promotion"
            :disabled="!inputValue.trim()"
            circle
            class="send-btn"
            @click="handleSend"
          />
        </div>
      </div>
    </div>
    <div class="input-hint">
      <span>内容由AI生成，仅供参考</span>
    </div>
  </div>
</template>

<style scoped lang="scss">
.chat-input-wrapper {
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
}

.chat-input-container {
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  transition: all 0.2s;

  &:focus-within {
    border-color: #1890ff;
    box-shadow: 0 2px 12px rgba(24, 144, 255, 0.15);
  }

  // 输入框区域
  .input-area {
    padding: 12px 16px 8px;

    .chat-textarea {
      :deep(.el-textarea__inner) {
        border: none;
        box-shadow: none;
        padding: 0;
        resize: none;
        font-size: 14px;
        line-height: 1.6;
        background: transparent;

        &:focus {
          box-shadow: none;
        }

        &::placeholder {
          color: #999;
        }
      }
    }
  }

  // 底部功能栏
  .action-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 12px 12px;

    .action-left {
      display: flex;
      align-items: center;
      flex: 1;
      overflow: hidden;
    }

    .action-right {
      display: flex;
      align-items: center;
      flex-shrink: 0;
      margin-left: 8px;
    }

    // 助手选择器
    .assistant-selector {
      display: flex;
      gap: 4px;
      
      .assistant-item {
        display: flex;
        align-items: center;
        gap: 4px;
        padding: 6px 12px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 13px;
        color: #666;
        background: transparent;
        transition: all 0.2s;
        user-select: none;
        
        &:hover:not(.disabled) {
          background: #e8e8e8;
        }
        
        &.active {
          background: #e6f4ff;
          color: #1890ff;
        }
        
        &.disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
      }
    }

    // 发送按钮
    .send-btn {
      width: 32px;
      height: 32px;
      
      &:not(:disabled) {
        background: #1890ff;
        border-color: #1890ff;
      }

      &:disabled {
        background: #e5e7eb;
        border-color: #e5e7eb;
        color: #999;
      }
    }

    // 停止按钮
    .stop-btn {
      width: 32px;
      height: 32px;
      background: #ff4d4f;
      border-color: #ff4d4f;
      
      &:hover {
        background: #ff7875;
        border-color: #ff7875;
      }
    }
  }
}

.input-hint {
  text-align: center;
  margin-top: 8px;
  font-size: 12px;
  color: #999;
}
</style>
