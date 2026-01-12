<script setup lang="ts">
/**
 * 聊天输入框组件
 * 参考图片布局：输入框在上，功能按钮在下
 */
import { ref } from 'vue'
import { Promotion } from '@element-plus/icons-vue'

// Props
const props = defineProps<{
  loading?: boolean
  deepMode?: boolean  // 深度分析模式（多专家协作）
}>()

// Emits
const emit = defineEmits<{
  send: [content: string]
  'update:deepMode': [value: boolean]
}>()

const inputValue = ref('')

// 发送消息
function handleSend() {
  const content = inputValue.value.trim()
  if (!content) return
  
  emit('send', content)
  inputValue.value = ''
}

// 按下回车发送
function handleKeydown(e: Event | KeyboardEvent) {
  const keyEvent = e as KeyboardEvent
  if (keyEvent.key === 'Enter' && !keyEvent.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

// 切换深度分析模式
function toggleDeepMode() {
  emit('update:deepMode', !props.deepMode)
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
          <!-- 多专家协作开关 -->
          <div 
            class="action-btn deep-mode"
            :class="{ active: props.deepMode }"
            @click="toggleDeepMode"
          >
            <el-icon :size="14">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
              </svg>
            </el-icon>
            <span>多专家协作</span>
          </div>
        </div>
        
        <div class="action-right">
          <!-- 发送按钮 -->
          <el-button
            type="primary"
            :icon="Promotion"
            :loading="loading"
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
    padding: 8px 16px 12px;

    .action-left {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .action-right {
      display: flex;
      align-items: center;
    }

    // 功能按钮通用样式
    .action-btn {
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

      &:hover {
        background: #e8e8e8;
      }

      // 多专家协作按钮
      &.deep-mode {
        &.active {
          background: #e6f4ff;
          color: #1890ff;
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
  }
}

.input-hint {
  text-align: center;
  margin-top: 8px;
  font-size: 12px;
  color: #999;
}
</style>
