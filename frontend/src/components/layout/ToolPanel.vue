<script setup lang="ts">
/**
 * 右侧工具栏组件
 * 固定在右侧边缘的浮动小条，鼠标靠近自动展开
 */
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  DataAnalysis, 
  TrendCharts, 
  Document,
  QuestionFilled
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

// 是否展开
const expanded = ref(false)

// 工具菜单
const toolMenus = [
  { path: '/calculator', name: '计算器', icon: DataAnalysis },
  { path: '/market', name: '市场分析', icon: TrendCharts },
  { path: '/policy', name: '政策查询', icon: Document },
  { path: '/help', name: '帮助中心', icon: QuestionFilled }
]

// 导航到工具页面（toggle：再次点击返回主页）
function navigateTo(path: string) {
  if (route.path === path) {
    // 已在当前页面，返回主页
    router.push('/chat')
  } else {
    router.push(path)
  }
}
</script>

<template>
  <div 
    class="tool-bar-wrapper"
    @mouseenter="expanded = true"
    @mouseleave="expanded = false"
  >
    <aside class="tool-bar" :class="{ expanded }">
      <div
        v-for="tool in toolMenus"
        :key="tool.path"
        class="tool-item"
        :class="{ active: route.path === tool.path }"
        :title="tool.name"
        @click="navigateTo(tool.path)"
      >
        <el-icon :size="18">
          <component :is="tool.icon" />
        </el-icon>
      </div>
    </aside>
  </div>
</template>

<style scoped lang="scss">
.tool-bar-wrapper {
  position: fixed;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  z-index: 100;
  padding: 8px 0 8px 8px;  // 左侧留出触发区域
}

.tool-bar {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-right: none;
  border-radius: 8px 0 0 8px;
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 4px;
  gap: 4px;
  transform: translateX(calc(100% - 8px));  // 默认只露出一点
  transition: transform 0.2s ease;
  
  &.expanded {
    transform: translateX(0);  // 展开
  }
}

.tool-item {
  width: 36px;
  height: 36px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #666;
  transition: all 0.2s;

  &:hover {
    background: #f0f0f0;
    color: #333;
  }

  &.active {
    background: #e6f4ff;
    color: #1890ff;
  }
}
</style>
