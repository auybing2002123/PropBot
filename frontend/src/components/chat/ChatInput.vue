<script setup lang="ts">
/**
 * 聊天输入框组件
 * 简洁版：只保留输入框和发送按钮
 */
import { ref } from 'vue'
import { Promotion, VideoPause } from '@element-plus/icons-vue'

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
        
        <!-- 发送/停止按钮 -->
        <div class="send-area">
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
    display: flex;
    align-items: center;
    padding: 12px 16px;
    gap: 12px;

    .chat-textarea {
      flex: 1;
      
      :deep(.el-textarea__inner) {
        border: none;
        box-shadow: none;
        padding: 0;
        resize: none;
        font-size: 14px;
        line-height: 1.6;
        background: transparent;
        min-height: 24px;

        &:focus {
          box-shadow: none;
        }

        &::placeholder {
          color: #999;
        }
      }
    }
    
    .send-area {
      flex-shrink: 0;
      display: flex;
      align-items: center;
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
