<script setup lang="ts">
/**
 * 角色消息组件
 * 支持折叠展示思考过程（包含专家分析）
 * 支持解析和渲染推荐问题
 * 支持关注功能
 */
import { computed, ref, watch, onUnmounted, onMounted } from 'vue'
import { marked } from 'marked'
import { ElMessage } from 'element-plus'
import { 
  Document, 
  Loading,
  ArrowDown,
  ArrowUp,
  Check,
  Setting,
  Search,
  DataAnalysis,
  User,
  Star,
  StarFilled,
  CopyDocument,
  Share
} from '@element-plus/icons-vue'
import { useChatStore } from '@/stores/chat'
import { useFavoriteStore } from '@/stores/favorite'
import ReferenceContent from './ReferenceContent.vue'
import type { RoleId, ExpertAnalysis, ThinkingStep, Reference } from '@/types/chat'

const chatStore = useChatStore()
const favoriteStore = useFavoriteStore()

// Props
const props = defineProps<{
  messageId?: string           // 消息ID（用于收藏）
  conversationId?: string      // 对话ID（用于跳转）
  userQuestion?: string        // 用户问题（用于收藏显示）
  roleId?: RoleId
  roleName?: string
  roleIcon?: string
  roleColor?: string
  content: string
  loading?: boolean
  isSummary?: boolean
  expertAnalysis?: ExpertAnalysis[]
  showExpertAnalysis?: boolean
  // 思考过程相关
  thinkingSteps?: ThinkingStep[]
  isThinking?: boolean
  showThinking?: boolean
  // 引用来源相关
  references?: Reference[]
}>()

// Emits
const emit = defineEmits<{
  (e: 'toggleExpert'): void
  (e: 'toggleThinking'): void
  (e: 'sendQuestion', question: string): void
}>()

// 专家分析展开状态（每个专家独立控制）
const expandedExperts = ref<Set<string>>(new Set())

// 实时计时器 - 使用 store 中的开始时间
const elapsedSeconds = ref(0)
let timerInterval: ReturnType<typeof setInterval> | null = null

// 启动计时器的函数
function startTimer() {
  if (timerInterval) {
    clearInterval(timerInterval)
  }
  // 基于 store 中的开始时间计算已过去的秒数
  const updateElapsed = () => {
    if (chatStore.thinkingStartTime > 0) {
      elapsedSeconds.value = Math.floor((Date.now() - chatStore.thinkingStartTime) / 1000)
    }
  }
  updateElapsed()  // 立即更新一次
  timerInterval = setInterval(updateElapsed, 1000)
}

// 停止计时器的函数
function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}

// 组件挂载时，如果正在思考则启动计时器
onMounted(() => {
  if (props.isThinking) {
    startTimer()
  }
})

// 监听 isThinking 变化
watch(() => props.isThinking, (newVal, oldVal) => {
  if (newVal && !oldVal) {
    // 从 false 变为 true，启动计时器
    startTimer()
  } else if (!newVal && oldVal) {
    // 从 true 变为 false，停止计时
    stopTimer()
  }
})

// 组件卸载时清除计时器
onUnmounted(() => {
  if (timerInterval) {
    clearInterval(timerInterval)
  }
})

// 切换专家分析展开状态
function toggleExpertExpand(stepId: string) {
  if (expandedExperts.value.has(stepId)) {
    expandedExperts.value.delete(stepId)
  } else {
    expandedExperts.value.add(stepId)
  }
}

// 渲染 Markdown 内容（不含引用标记的处理）
const renderedContent = computed(() => {
  if (!props.content) return ''
  // 移除推荐问题部分后再渲染
  const contentWithoutQuestions = props.content.replace(/【推荐问题】[\s\S]*$/, '').trim()
  return marked(contentWithoutQuestions, { breaks: true })
})

// 是否有引用
const hasReferences = computed(() => {
  return props.references && props.references.length > 0
})

// 获取不含推荐问题的内容（用于引用渲染）
const contentWithoutQuestions = computed(() => {
  if (!props.content) return ''
  return props.content.replace(/【推荐问题】[\s\S]*$/, '').trim()
})

// 解析推荐问题
const recommendQuestions = computed(() => {
  if (!props.content || props.loading) return []
  
  const match = props.content.match(/【推荐问题】\n?([\s\S]*?)$/)
  if (!match) return []
  
  const questionsText = match[1]
  const questions = questionsText
    .split('\n')
    .map(q => q.replace(/^[-\d.、·•]\s*/, '').trim())
    .filter(q => q && q.length > 0 && q.length < 100)  // 过滤空行和过长的内容
  
  return questions.slice(0, 5)  // 最多显示5个
})

// 点击推荐问题
function handleQuestionClick(question: string) {
  emit('sendQuestion', question)
}

// 是否已收藏
const isFavorited = computed(() => {
  if (!props.messageId) return false
  return favoriteStore.isFavorited(props.messageId)
})

// 复制内容到剪贴板
async function handleCopy() {
  if (!props.content) return
  
  // 移除推荐问题部分，获取纯文本
  const cleanContent = props.content.replace(/【推荐问题】[\s\S]*$/, '').trim()
  
  try {
    await navigator.clipboard.writeText(cleanContent)
    ElMessage.success('已复制到剪贴板')
  } catch (err) {
    ElMessage.error('复制失败')
  }
}

// 收藏/取消收藏
async function handleFavorite() {
  if (!props.content || props.loading) return
  
  // 如果已收藏，则取消收藏
  if (isFavorited.value && props.messageId) {
    // 找到对应的收藏记录
    const favorite = favoriteStore.favorites.find(f => f.message_id === props.messageId)
    if (favorite) {
      await favoriteStore.remove(favorite.id)
    }
    return
  }
  
  // 否则添加收藏
  // 移除推荐问题部分
  const cleanAnswer = props.content.replace(/【推荐问题】[\s\S]*$/, '').trim()
  
  await favoriteStore.add({
    messageId: props.messageId,
    conversationId: props.conversationId,
    question: props.userQuestion || '未知问题',
    answer: cleanAnswer
  })
}

// 渲染专家分析内容
function renderExpertContent(content: string): string {
  return marked(content, { breaks: true }) as string
}

// 是否有思考过程
const hasThinkingSteps = computed(() => {
  return props.thinkingSteps && props.thinkingSteps.length > 0
})

// 思考过程耗时（秒）- 使用实时计时器
const thinkingDuration = computed(() => {
  // 正在思考时始终使用实时计时器
  if (props.isThinking) {
    return elapsedSeconds.value
  }
  // 思考完成后，优先使用实时计时器的值
  // 如果实时计时器有值，说明是刚完成的，用它
  if (elapsedSeconds.value > 0) {
    return elapsedSeconds.value
  }
  // 否则用步骤时间戳计算（历史消息）
  if (!props.thinkingSteps || props.thinkingSteps.length === 0) return 0
  const first = props.thinkingSteps[0].timestamp
  const last = props.thinkingSteps[props.thinkingSteps.length - 1].timestamp
  return Math.round((last - first) / 1000)
})

// 获取思考步骤图标
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

// 获取思考步骤颜色
function getStepColor(type: string, roleId?: string) {
  // 专家分析使用角色对应的颜色
  if (type === 'expert_analysis' && roleId) {
    const roleColors: Record<string, string> = {
      'policy_expert': '#1890ff',
      'financial_advisor': '#52c41a',
      'market_analyst': '#faad14',
      'purchase_consultant': '#722ed1'
    }
    return roleColors[roleId] || '#722ed1'
  }
  
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
    default:
      return '#999'
  }
}

// 最新的思考步骤（用于折叠时显示预览）
const latestThinkingStep = computed(() => {
  if (!props.thinkingSteps || props.thinkingSteps.length === 0) return null
  return props.thinkingSteps[props.thinkingSteps.length - 1]
})

// 获取专家分析的摘要（前100字）
function getExpertSummary(content: string): string {
  // 移除 markdown 标记，获取纯文本
  const plainText = content
    .replace(/#{1,6}\s/g, '')  // 移除标题
    .replace(/\*\*/g, '')      // 移除加粗
    .replace(/\n/g, ' ')       // 换行转空格
    .trim()
  
  if (plainText.length <= 80) return plainText
  return plainText.substring(0, 80) + '...'
}
</script>

<template>
  <div class="role-message">
    <div class="role-content">
      <!-- 思考过程（嵌入在内容上方） -->
      <div v-if="hasThinkingSteps" class="thinking-section">
        <div class="thinking-header">
          <div 
            class="thinking-toggle" 
            @click="emit('toggleThinking')"
          >
            <el-icon 
              :size="14" 
              class="thinking-icon"
              :class="{ 'is-loading': isThinking }"
            >
              <Loading v-if="isThinking" />
              <Check v-else />
            </el-icon>
            <span class="thinking-title">
              {{ isThinking ? `已深度思考 (用时${thinkingDuration}秒)` : `已深度思考 (用时${thinkingDuration}秒)` }}
            </span>
            <el-icon :size="12" class="expand-icon">
              <component :is="showThinking ? ArrowUp : ArrowDown" />
            </el-icon>
          </div>
        </div>
        
        <!-- 折叠时显示最新一条步骤预览 -->
        <div v-if="!showThinking && latestThinkingStep" class="thinking-preview">
          <el-icon :size="12" :style="{ color: getStepColor(latestThinkingStep.type, latestThinkingStep.roleId) }">
            <component :is="getStepIcon(latestThinkingStep.type)" />
          </el-icon>
          <span class="preview-text">
            {{ latestThinkingStep.type === 'expert_analysis' 
              ? `${latestThinkingStep.roleName}分析完成` 
              : latestThinkingStep.content }}
          </span>
        </div>
        
        <el-collapse-transition>
          <div v-show="showThinking" class="thinking-steps">
            <div 
              v-for="(step, index) in thinkingSteps" 
              :key="step.id"
              class="thinking-step"
              :class="{ 'is-expert': step.type === 'expert_analysis' }"
            >
              <div class="step-line">
                <div class="step-dot" :style="{ backgroundColor: getStepColor(step.type, step.roleId) }">
                  <el-icon :size="10">
                    <component :is="getStepIcon(step.type)" />
                  </el-icon>
                </div>
                <div v-if="index < (thinkingSteps?.length || 0) - 1" class="step-connector"></div>
              </div>
              <div class="step-content">
                <!-- 普通步骤 -->
                <template v-if="step.type !== 'expert_analysis'">
                  <span class="step-text">{{ step.content }}</span>
                  <span v-if="step.toolName" class="step-tool">
                    调用 {{ step.toolName }}
                  </span>
                </template>
                
                <!-- 专家分析步骤 -->
                <template v-else>
                  <div 
                    class="expert-step-header"
                    @click="toggleExpertExpand(step.id)"
                  >
                    <span 
                      class="expert-step-name"
                      :style="{ color: getStepColor(step.type, step.roleId) }"
                    >
                      {{ step.roleName }}分析完成
                    </span>
                    <el-icon :size="12" class="expert-expand-icon">
                      <component :is="expandedExperts.has(step.id) ? ArrowUp : ArrowDown" />
                    </el-icon>
                  </div>
                  <div v-if="!expandedExperts.has(step.id)" class="expert-step-summary">
                    {{ getExpertSummary(step.content) }}
                  </div>
                  <el-collapse-transition>
                    <div 
                      v-show="expandedExperts.has(step.id)" 
                      class="expert-step-content markdown-content"
                      v-html="renderExpertContent(step.content)"
                    ></div>
                  </el-collapse-transition>
                </template>
              </div>
            </div>
          </div>
        </el-collapse-transition>
      </div>
      
      <!-- 正文内容 -->
      <template v-if="loading && !hasThinkingSteps">
        <span class="loading-text">思考中...</span>
      </template>
      <template v-else-if="content">
        <!-- 有引用时使用 ReferenceContent 组件渲染 -->
        <div v-if="hasReferences" class="markdown-content">
          <ReferenceContent 
            :content="contentWithoutQuestions" 
            :references="references"
          />
        </div>
        <!-- 无引用时直接渲染 Markdown -->
        <div v-else v-html="renderedContent" class="markdown-content"></div>
        
        <!-- 推荐问题 -->
        <div v-if="recommendQuestions.length > 0" class="recommend-questions">
          <div class="recommend-label">您可能还想了解：</div>
          <div class="recommend-list">
            <el-button
              v-for="(q, index) in recommendQuestions"
              :key="index"
              size="small"
              class="recommend-btn"
              @click="handleQuestionClick(q)"
            >
              {{ q }}
            </el-button>
          </div>
        </div>
      </template>
    </div>
    
    <!-- 操作按钮栏（放在卡片外面） -->
    <div v-if="content && !loading" class="action-bar">
      <div 
        class="action-btn"
        title="复制"
        @click="handleCopy"
      >
        <el-icon :size="16"><CopyDocument /></el-icon>
      </div>
      <div 
        class="action-btn"
        :class="{ active: isFavorited }"
        :title="isFavorited ? '已收藏' : '收藏'"
        @click="handleFavorite"
      >
        <el-icon :size="16">
          <StarFilled v-if="isFavorited" />
          <Star v-else />
        </el-icon>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.role-message {
  max-width: 85%;
  
  // 操作按钮栏（在卡片外面）
  .action-bar {
    display: flex;
    align-items: center;
    gap: 4px;
    margin-top: 8px;
    padding-left: 4px;
  }
  
  .action-btn {
    width: 32px;
    height: 32px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: #999;
    transition: all 0.2s;
    
    &:hover {
      background: #f5f5f5;
      color: #666;
    }
    
    &.active {
      color: #faad14;
      
      &:hover {
        color: #d48806;
      }
    }
  }
  
  .role-content {
    background: #ffffff;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    color: #333;
    font-size: 14px;
    line-height: 1.6;
    
    .loading-text {
      color: #999;
    }
    
    // 思考过程样式
    .thinking-section {
      margin-bottom: 12px;
      padding-bottom: 12px;
      border-bottom: 1px dashed #e8e8e8;
      
      .thinking-header {
        display: flex;
        align-items: center;
      }
      
      .thinking-toggle {
        display: flex;
        align-items: center;
        gap: 6px;
        cursor: pointer;
        flex: 1;
        
        &:hover {
          .thinking-title {
            color: #1890ff;
          }
        }
        
        .thinking-icon {
          color: #1890ff;
          
          &.is-loading {
            animation: spin 1s linear infinite;
          }
        }
        
        .thinking-title {
          font-size: 13px;
          color: #666;
          transition: color 0.2s;
        }
        
        .expand-icon {
          color: #999;
        }
      }
      
      .thinking-preview {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 6px 0 0 20px;
        
        .preview-text {
          font-size: 12px;
          color: #888;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
      }
      
      .thinking-steps {
        margin-top: 8px;
        padding-left: 4px;
      }
      
      .thinking-step {
        display: flex;
        gap: 8px;
        
        &.is-expert {
          .step-content {
            padding-bottom: 12px;
          }
        }
      }
      
      .step-line {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 18px;
        
        .step-dot {
          width: 18px;
          height: 18px;
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
          min-height: 12px;
          background: #e8e8e8;
          margin: 3px 0;
        }
      }
      
      .step-content {
        flex: 1;
        padding: 1px 0 10px 0;
        
        .step-text {
          font-size: 12px;
          color: #666;
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
        
        // 专家分析步骤样式
        .expert-step-header {
          display: flex;
          align-items: center;
          gap: 6px;
          cursor: pointer;
          
          &:hover {
            .expert-step-name {
              text-decoration: underline;
            }
          }
          
          .expert-step-name {
            font-size: 12px;
            font-weight: 500;
          }
          
          .expert-expand-icon {
            color: #999;
          }
        }
        
        .expert-step-summary {
          font-size: 11px;
          color: #999;
          margin-top: 4px;
          line-height: 1.4;
        }
        
        .expert-step-content {
          margin-top: 8px;
          padding: 10px;
          background: #fafafa;
          border-radius: 6px;
          font-size: 12px;
          color: #555;
          max-height: 300px;
          overflow-y: auto;
          
          :deep(h2), :deep(h3), :deep(h4) {
            font-size: 13px;
            margin-top: 8px;
            margin-bottom: 4px;
          }
          
          :deep(p) {
            margin-bottom: 6px;
          }
          
          :deep(ul), :deep(ol) {
            padding-left: 16px;
            margin-bottom: 6px;
          }
          
          :deep(li) {
            margin-bottom: 2px;
          }
          
          :deep(table) {
            font-size: 11px;
            width: 100%;
            border-collapse: collapse;
            margin: 8px 0;
            
            th, td {
              border: 1px solid #e8e8e8;
              padding: 4px 8px;
              text-align: left;
            }
            
            th {
              background: #f5f5f5;
            }
          }
        }
      }
    }
  }
}

.markdown-content {
  :deep(p) {
    margin-bottom: 8px;
    
    &:last-child {
      margin-bottom: 0;
    }
  }
  
  :deep(ul), :deep(ol) {
    padding-left: 20px;
    margin-bottom: 8px;
  }
  
  :deep(li) {
    margin-bottom: 4px;
  }
  
  :deep(strong) {
    font-weight: 600;
  }
  
  :deep(h2), :deep(h3) {
    margin-top: 12px;
    margin-bottom: 8px;
    font-weight: 600;
  }
  
  :deep(h2) {
    font-size: 15px;
  }
  
  :deep(h3) {
    font-size: 14px;
  }
}

// 推荐问题样式
.recommend-questions {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px dashed #e8e8e8;
  
  .recommend-label {
    font-size: 12px;
    color: #999;
    margin-bottom: 8px;
  }
  
  .recommend-list {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .recommend-btn {
    font-size: 12px;
    color: #1890ff;
    background: #f0f7ff;
    border: 1px solid #d6e8fc;
    border-radius: 16px;
    padding: 6px 14px;
    height: auto;
    white-space: normal;
    text-align: left;
    line-height: 1.4;
    margin-left: 0 !important;
    
    &:hover {
      background: #e6f4ff;
      border-color: #1890ff;
    }
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
