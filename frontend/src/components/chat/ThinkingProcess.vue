<script setup lang="ts">
/**
 * 思考过程组件
 * 展示 AI 的执行步骤
 * - 折叠时：只显示最新一条执行步骤
 * - 展开时：显示全部步骤（包括专家分析）
 */
import { computed, ref, watch, onUnmounted } from 'vue'
import { 
  Loading, 
  Check, 
  Search, 
  Setting,
  Document,
  DataAnalysis,
  ArrowDown,
  ArrowUp,
  User
} from '@element-plus/icons-vue'
import type { ThinkingStep } from '@/types/chat'

const props = defineProps<{
  steps: ThinkingStep[]
  isThinking: boolean
  expanded: boolean
}>()

const emit = defineEmits<{
  (e: 'toggle'): void
}>()

// 实时计时器
const elapsedSeconds = ref(0)
let timerInterval: ReturnType<typeof setInterval> | null = null

// 监听 isThinking 变化，启动/停止计时器
watch(() => props.isThinking, (newVal) => {
  if (newVal) {
    // 开始思考，启动计时器
    elapsedSeconds.value = 0
    timerInterval = setInterval(() => {
      elapsedSeconds.value++
    }, 1000)
  } else {
    // 停止思考，清除计时器
    if (timerInterval) {
      clearInterval(timerInterval)
      timerInterval = null
    }
  }
}, { immediate: true })

// 组件卸载时清除计时器
onUnmounted(() => {
  if (timerInterval) {
    clearInterval(timerInterval)
  }
})

// 计算思考用时 - 使用实时计时器
const thinkingDuration = computed(() => {
  // 正在思考时使用实时计时
  if (props.isThinking) {
    return elapsedSeconds.value
  }
  // 思考完成后使用步骤时间戳计算
  if (props.steps.length === 0) return elapsedSeconds.value
  const lastStep = props.steps[props.steps.length - 1]
  const firstStep = props.steps[0]
  if (lastStep && firstStep) {
    return Math.max(elapsedSeconds.value, Math.round((lastStep.timestamp - firstStep.timestamp) / 1000))
  }
  return elapsedSeconds.value
})

// 获取步骤图标
function getStepIcon(type: string) {
  switch (type) {
    case 'planning':
      return DataAnalysis
    case 'role_dispatch':
      return Document
    case 'tool_call':
      return Setting
    case 'tool_result':
      return Check
    case 'synthesizing':
      return Search
    case 'expert_analysis':
      return User
    default:
      return Loading
  }
}

// 获取步骤颜色
function getStepColor(type: string) {
  switch (type) {
    case 'planning':
      return '#1890ff'
    case 'role_dispatch':
      return '#52c41a'
    case 'tool_call':
      return '#faad14'
    case 'tool_result':
      return '#52c41a'
    case 'synthesizing':
      return '#722ed1'
    case 'expert_analysis':
      return '#eb2f96'
    default:
      return '#999'
  }
}

// 最新的步骤（用于折叠时显示）
const latestStep = computed(() => {
  if (props.steps.length === 0) return null
  return props.steps[props.steps.length - 1]
})
</script>

<template>
  <div class="thinking-process" :class="{ 'is-thinking': isThinking }">
    <!-- 折叠状态：只显示最新步骤 -->
    <div v-if="!expanded" class="thinking-collapsed" @click="emit('toggle')">
      <div class="thinking-header">
        <el-icon 
          :size="16" 
          class="thinking-icon"
          :class="{ 'is-loading': isThinking }"
        >
          <Loading v-if="isThinking" />
          <Check v-else />
        </el-icon>
        <span class="thinking-title">
          {{ isThinking ? `已深度思考 (用时${thinkingDuration}秒)` : `已深度思考 (用时${thinkingDuration}秒)` }}
        </span>
        <el-icon :size="14" class="expand-icon">
          <ArrowDown />
        </el-icon>
      </div>
      <!-- 折叠时显示最新一条步骤 -->
      <div v-if="latestStep" class="thinking-preview">
        <el-icon :size="12" :style="{ color: getStepColor(latestStep.type) }">
          <component :is="getStepIcon(latestStep.type)" />
        </el-icon>
        <span class="preview-text">{{ latestStep.content }}</span>
      </div>
    </div>
    
    <!-- 展开状态：显示所有步骤 -->
    <div v-else class="thinking-expanded">
      <div class="thinking-header" @click="emit('toggle')">
        <el-icon 
          :size="16" 
          class="thinking-icon"
          :class="{ 'is-loading': isThinking }"
        >
          <Loading v-if="isThinking" />
          <Check v-else />
        </el-icon>
        <span class="thinking-title">
          {{ isThinking ? `已深度思考 (用时${thinkingDuration}秒)` : `已深度思考 (用时${thinkingDuration}秒)` }}
        </span>
        <el-icon :size="14" class="expand-icon">
          <ArrowUp />
        </el-icon>
      </div>
      
      <div class="thinking-steps">
        <div 
          v-for="(step, index) in steps" 
          :key="step.id"
          class="thinking-step"
          :class="{ 
            'is-latest': index === steps.length - 1 && isThinking,
            'is-expert': step.type === 'expert_analysis'
          }"
        >
          <div class="step-line">
            <div class="step-dot" :style="{ backgroundColor: getStepColor(step.type) }">
              <el-icon :size="10">
                <component :is="getStepIcon(step.type)" />
              </el-icon>
            </div>
            <div v-if="index < steps.length - 1" class="step-connector"></div>
          </div>
          <div class="step-content">
            <div class="step-header">
              <span v-if="step.roleName" class="step-role">{{ step.roleName }}</span>
              <span class="step-text">{{ step.content }}</span>
            </div>
            <span v-if="step.toolName" class="step-tool">
              调用 {{ step.toolName }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.thinking-process {
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 12px;
  overflow: hidden;
  border: 1px solid #e8e8e8;
  
  &.is-thinking {
    border-color: #1890ff;
    background: #f0f7ff;
  }
}

.thinking-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  cursor: pointer;
  
  &:hover {
    background: rgba(0, 0, 0, 0.02);
  }
  
  .thinking-icon {
    color: #1890ff;
    
    &.is-loading {
      animation: spin 1s linear infinite;
    }
  }
  
  .thinking-title {
    flex: 1;
    font-size: 13px;
    font-weight: 500;
    color: #333;
  }
  
  .expand-icon {
    color: #999;
  }
}

.thinking-preview {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 12px 10px 12px;
  
  .preview-text {
    font-size: 12px;
    color: #666;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.thinking-steps {
  padding: 0 12px 12px 12px;
  border-top: 1px dashed #e8e8e8;
  margin-top: 4px;
  padding-top: 12px;
}

.thinking-step {
  display: flex;
  gap: 10px;
  
  &.is-latest .step-text {
    color: #1890ff;
  }
  
  &.is-expert {
    .step-content {
      background: #fdf2f8;
      border-radius: 6px;
      padding: 8px 10px;
      margin-bottom: 8px;
    }
    
    .step-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 4px;
    }
    
    .step-role {
      font-weight: 500;
      color: #eb2f96;
    }
    
    .step-text {
      font-size: 12px;
      color: #666;
      line-height: 1.5;
      white-space: pre-wrap;
      max-height: 100px;
      overflow-y: auto;
    }
  }
}

.step-line {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 20px;
  
  .step-dot {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    flex-shrink: 0;
  }
  
  .step-connector {
    width: 2px;
    flex: 1;
    min-height: 16px;
    background: #e8e8e8;
    margin: 4px 0;
  }
}

.step-content {
  flex: 1;
  padding: 2px 0 12px 0;
  
  .step-header {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .step-role {
    font-size: 12px;
    font-weight: 500;
    color: #333;
  }
  
  .step-text {
    font-size: 12px;
    color: #555;
    line-height: 1.4;
  }
  
  .step-tool {
    display: inline-block;
    font-size: 11px;
    color: #faad14;
    background: #fffbe6;
    padding: 1px 6px;
    border-radius: 4px;
    margin-left: 6px;
  }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
