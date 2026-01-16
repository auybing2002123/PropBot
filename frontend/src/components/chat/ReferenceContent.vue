<script setup lang="ts">
/**
 * 引用内容渲染组件
 * 解析内容中的 [1]、[2] 等引用标记，鼠标悬停显示引用详情
 * 支持 Markdown 渲染
 * 移动端支持点击显示
 */
import { computed, ref, reactive, onBeforeUnmount, onMounted } from 'vue'
import { marked } from 'marked'
import { Document, DataAnalysis, Link, QuestionFilled, Close } from '@element-plus/icons-vue'
import type { Reference } from '@/types/chat'

const props = defineProps<{
  content: string
  references?: Reference[]
}>()

// 引用类型图标映射
const typeIconMap: Record<string, any> = {
  policy: Document,
  faq: QuestionFilled,
  guide: Document,
  database: DataAnalysis,
  web: Link,
  knowledge: Document
}

// 引用类型名称映射
const typeNameMap: Record<string, string> = {
  policy: '政策文档',
  faq: '常见问题',
  guide: '购房指南',
  database: '数据库',
  web: '联网搜索',
  knowledge: '知识库'
}

// 检测是否为移动端
const isMobile = ref(false)

onMounted(() => {
  isMobile.value = window.innerWidth < 768
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  clearHideTimer()
})

function handleResize() {
  isMobile.value = window.innerWidth < 768
}

// 根据引用 ID 获取引用信息
function getReference(id: number): Reference | undefined {
  return props.references?.find(ref => ref.id === id)
}

// 渲染 Markdown 内容为 HTML
function renderMarkdown(text: string): string {
  if (!text) return ''
  return marked(text, { breaks: true }) as string
}

// 渲染带引用标记的 HTML 内容
const renderedHtml = computed(() => {
  if (!props.content) return ''
  
  // 先渲染 Markdown
  let html = marked(props.content, { breaks: true }) as string
  
  // 如果没有引用，直接返回
  if (!props.references?.length) {
    return html
  }
  
  // 将 [1]、[2] 等标记替换为可交互的 span
  html = html.replace(/\[(\d+)\]/g, (match, num) => {
    const refId = parseInt(num)
    const refItem = props.references?.find(r => r.id === refId)
    if (refItem) {
      return `<span class="ref-tag" data-ref-id="${refId}">${match}</span>`
    }
    return match
  })
  
  return html
})

// 当前激活的引用（鼠标悬停时显示）
const activeRef = ref<Reference | null>(null)
const tooltipStyle = reactive({
  top: '0px',
  left: '0px',
  transform: 'translate(-50%, -100%)'
})

// 延迟隐藏定时器
let hideTimer: ReturnType<typeof setTimeout> | null = null
// 标记鼠标是否在 tooltip 上
const isMouseOnTooltip = ref(false)

// 清除隐藏定时器
function clearHideTimer() {
  if (hideTimer) {
    clearTimeout(hideTimer)
    hideTimer = null
  }
}

// 延迟隐藏 tooltip
function scheduleHide() {
  clearHideTimer()
  hideTimer = setTimeout(() => {
    if (!isMouseOnTooltip.value) {
      activeRef.value = null
    }
  }, 100) // 100ms 延迟，给用户时间移动到 tooltip
}

// 显示 tooltip
function showTooltip(target: HTMLElement, refItem: Reference) {
  activeRef.value = refItem
  const rect = target.getBoundingClientRect()
  
  if (isMobile.value) {
    // 移动端：居中显示
    tooltipStyle.top = '50%'
    tooltipStyle.left = '50%'
    tooltipStyle.transform = 'translate(-50%, -50%)'
  } else {
    // 桌面端：在元素附近显示
    const tooltipHeight = 300
    
    if (rect.top > tooltipHeight + 20) {
      tooltipStyle.top = `${rect.top - 10}px`
      tooltipStyle.transform = 'translate(-50%, -100%)'
    } else {
      tooltipStyle.top = `${rect.bottom + 10}px`
      tooltipStyle.transform = 'translate(-50%, 0)'
    }
    tooltipStyle.left = `${rect.left + rect.width / 2}px`
  }
}

// 鼠标悬停处理（桌面端）
function handleMouseOver(e: MouseEvent) {
  if (isMobile.value) return
  
  const target = e.target as HTMLElement
  if (target.classList.contains('ref-tag')) {
    clearHideTimer()
    const refId = parseInt(target.dataset.refId || '0')
    const refItem = getReference(refId)
    if (refItem) {
      showTooltip(target, refItem)
    }
  }
}

function handleMouseOut(e: MouseEvent) {
  if (isMobile.value) return
  
  const target = e.target as HTMLElement
  if (target.classList.contains('ref-tag')) {
    scheduleHide()
  }
}

// 点击处理（移动端和桌面端都支持）
function handleClick(e: MouseEvent) {
  const target = e.target as HTMLElement
  if (target.classList.contains('ref-tag')) {
    e.preventDefault()
    e.stopPropagation()
    
    const refId = parseInt(target.dataset.refId || '0')
    const refItem = getReference(refId)
    if (refItem) {
      // 如果点击的是同一个引用，则关闭
      if (activeRef.value?.id === refItem.id) {
        activeRef.value = null
      } else {
        showTooltip(target, refItem)
      }
    }
  }
}

// 关闭 tooltip（移动端用）
function closeTooltip() {
  activeRef.value = null
}

// Tooltip 鼠标事件处理
function handleTooltipMouseEnter() {
  if (isMobile.value) return
  isMouseOnTooltip.value = true
  clearHideTimer()
}

function handleTooltipMouseLeave() {
  if (isMobile.value) return
  isMouseOnTooltip.value = false
  scheduleHide()
}
</script>

<template>
  <div class="reference-content">
    <!-- 渲染带引用标记的 Markdown 内容 -->
    <div 
      class="markdown-body"
      v-html="renderedHtml"
      @mouseover="handleMouseOver"
      @mouseout="handleMouseOut"
      @click="handleClick"
    ></div>
    
    <!-- 引用详情 Tooltip（使用 Teleport 避免被裁剪） -->
    <Teleport to="body">
      <!-- 移动端遮罩层 -->
      <div 
        v-if="activeRef && isMobile" 
        class="ref-overlay"
        @click="closeTooltip"
      ></div>
      
      <div 
        v-if="activeRef" 
        class="ref-tooltip"
        :class="{ 'is-mobile': isMobile }"
        :style="tooltipStyle"
        @mouseenter="handleTooltipMouseEnter"
        @mouseleave="handleTooltipMouseLeave"
      >
        <!-- 移动端关闭按钮 -->
        <button 
          v-if="isMobile" 
          class="ref-close-btn"
          @click="closeTooltip"
        >
          <el-icon :size="18"><Close /></el-icon>
        </button>
        
        <div class="ref-header">
          <el-icon :size="16" class="ref-icon">
            <component :is="typeIconMap[activeRef.type] || Document" />
          </el-icon>
          <span class="ref-type">{{ typeNameMap[activeRef.type] || '知识库' }}</span>
        </div>
        <div class="ref-title">{{ activeRef.title }}</div>
        <div class="ref-content-text" v-html="renderMarkdown(activeRef.content)"></div>
        <div v-if="activeRef.source" class="ref-source">
          来源：{{ activeRef.source }}
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped lang="scss">
.reference-content {
  .markdown-body {
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
    
    // 引用标记样式
    :deep(.ref-tag) {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 20px;
      height: 18px;
      padding: 0 4px;
      margin: 0 1px;
      font-size: 12px;
      font-weight: 500;
      color: #1890ff;
      background: #e6f4ff;
      border-radius: 4px;
      cursor: pointer;
      vertical-align: middle;
      transition: all 0.2s;
      
      &:hover {
        background: #bae0ff;
        color: #0958d9;
      }
    }
  }
}
</style>

<style lang="scss">
// 移动端遮罩层
.ref-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 9998;
}

// Tooltip 样式（全局，因为使用了 Teleport）
.ref-tooltip {
  position: fixed;
  z-index: 9999;
  max-width: 450px;
  min-width: 300px;
  padding: 14px 16px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  
  // 移动端样式
  &.is-mobile {
    width: calc(100vw - 32px);
    max-width: none;
    min-width: auto;
    max-height: 70vh;
    border-radius: 12px;
    padding: 16px;
    padding-top: 40px;
    
    .ref-content-text {
      max-height: calc(70vh - 160px);
    }
  }
  
  // 关闭按钮
  .ref-close-btn {
    position: absolute;
    top: 10px;
    right: 10px;
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f5f5f5;
    border: none;
    border-radius: 50%;
    cursor: pointer;
    color: #666;
    transition: all 0.2s;
    
    &:hover {
      background: #e8e8e8;
      color: #333;
    }
    
    &:active {
      background: #d9d9d9;
    }
  }
  
  .ref-header {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 10px;
    padding-bottom: 10px;
    border-bottom: 1px solid #f0f0f0;
    
    .ref-icon {
      color: #1890ff;
    }
    
    .ref-type {
      font-size: 12px;
      color: #666;
    }
  }
  
  .ref-title {
    font-size: 14px;
    font-weight: 500;
    color: #333;
    margin-bottom: 10px;
    line-height: 1.5;
  }
  
  .ref-content-text {
    font-size: 13px;
    color: #666;
    line-height: 1.7;
    max-height: 320px;
    overflow-y: auto;
    margin-bottom: 10px;
    padding-right: 4px;
    
    // 滚动条样式
    &::-webkit-scrollbar {
      width: 6px;
    }
    
    &::-webkit-scrollbar-thumb {
      background: #d9d9d9;
      border-radius: 3px;
    }
    
    &::-webkit-scrollbar-track {
      background: transparent;
    }
    
    // Markdown 渲染样式
    :deep(h1), :deep(h2), :deep(h3), :deep(h4) {
      font-size: 13px;
      font-weight: 600;
      margin: 8px 0 4px 0;
      color: #333;
    }
    
    :deep(p) {
      margin: 4px 0;
    }
    
    :deep(ul), :deep(ol) {
      padding-left: 16px;
      margin: 4px 0;
    }
    
    :deep(li) {
      margin: 2px 0;
    }
    
    :deep(strong) {
      font-weight: 600;
      color: #333;
    }
    
    :deep(code) {
      background: #f5f5f5;
      padding: 1px 4px;
      border-radius: 3px;
      font-size: 12px;
    }
  }
  
  .ref-source {
    font-size: 12px;
    color: #999;
    padding-top: 10px;
    border-top: 1px solid #f0f0f0;
  }
}
</style>
