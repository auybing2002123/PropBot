<script setup lang="ts">
/**
 * 整体布局组件
 * ChatGPT 风格：左侧边栏 + 右侧内容区
 * 桌面端：侧边栏默认展开，通过宽度过渡实现流畅动画
 * 手机端：侧边栏默认隐藏，通过抽屉展示
 */
import { ref, computed, onMounted, onUnmounted } from 'vue'
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'

// 移动端断点
const MOBILE_BREAKPOINT = 768

// 是否是移动端
const isMobile = ref(false)

// 桌面端侧边栏是否折叠
const sidebarCollapsed = ref(false)

// 移动端抽屉是否打开
const drawerOpen = ref(false)

// 是否显示遮罩层：仅移动端抽屉打开时显示
const showOverlay = computed(() => {
  return isMobile.value && drawerOpen.value
})

// 响应式处理
function handleResize() {
  const wasMobile = isMobile.value
  isMobile.value = window.innerWidth < MOBILE_BREAKPOINT
  
  // 切换到移动端时，关闭抽屉
  if (!wasMobile && isMobile.value) {
    drawerOpen.value = false
  }
  // 切换到桌面端时，关闭抽屉，恢复默认展开
  if (wasMobile && !isMobile.value) {
    drawerOpen.value = false
    sidebarCollapsed.value = false
  }
}

// 切换侧边栏
function toggleSidebar() {
  if (isMobile.value) {
    // 移动端：切换抽屉
    drawerOpen.value = !drawerOpen.value
  } else {
    // 桌面端：切换折叠状态
    sidebarCollapsed.value = !sidebarCollapsed.value
  }
}

// 关闭抽屉
function closeDrawer() {
  drawerOpen.value = false
}

// 新建对话回调
function handleNewChat() {
  closeDrawer()
}

// 导航后关闭抽屉
function handleNavigate() {
  closeDrawer()
}

onMounted(() => {
  handleResize()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<template>
  <div class="app-layout" :class="{ 'is-mobile': isMobile, 'sidebar-collapsed': sidebarCollapsed }">
    <!-- 遮罩层（仅移动端抽屉打开时显示） -->
    <transition name="fade">
      <div 
        v-if="showOverlay" 
        class="sidebar-overlay"
        @click="closeDrawer"
      />
    </transition>
    
    <!-- 桌面端侧边栏（始终渲染，通过宽度控制） -->
    <div v-if="!isMobile" class="sidebar-wrapper" :class="{ collapsed: sidebarCollapsed }">
      <AppSidebar 
        :collapsed="false"
        :is-mobile="false"
        class="sidebar"
        @toggle="toggleSidebar"
        @new-chat="handleNewChat"
        @navigate="handleNavigate"
      />
    </div>
    
    <!-- 移动端侧边栏（抽屉模式） -->
    <transition name="drawer-slide">
      <div v-if="isMobile && drawerOpen" class="sidebar-drawer">
        <AppSidebar 
          :collapsed="false"
          :is-mobile="true"
          class="sidebar"
          @toggle="toggleSidebar"
          @new-chat="handleNewChat"
          @navigate="handleNavigate"
        />
      </div>
    </transition>
    
    <!-- 主内容区 -->
    <div class="app-content">
      <AppHeader 
        :sidebar-collapsed="isMobile || sidebarCollapsed"
        :is-mobile="isMobile"
        @toggle-sidebar="toggleSidebar"
      />
      <main class="app-main">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style scoped lang="scss">
.app-layout {
  width: 100%;
  height: 100%;
  display: flex;
  background: #f5f7fa;
  position: relative;
}

// 桌面端侧边栏容器（通过宽度过渡实现动画）
.sidebar-wrapper {
  width: 260px;
  height: 100%;
  flex-shrink: 0;
  overflow: hidden;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  
  &.collapsed {
    width: 0;
  }
  
  .sidebar {
    width: 260px;
    height: 100%;
  }
}

.app-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
  position: relative;
  z-index: 1;
}

.app-main {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

// 遮罩层
.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
}

// 移动端抽屉模式
.sidebar-drawer {
  position: fixed;
  top: 0;
  left: 0;
  height: 100%;
  z-index: 1001;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
  
  .sidebar {
    width: 260px;
    height: 100%;
  }
}

// 移动端布局调整
.is-mobile {
  .app-content {
    width: 100%;
  }
}

// 遮罩层淡入淡出动画
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

// 移动端抽屉滑动动画
.drawer-slide-enter-active,
.drawer-slide-leave-active {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.drawer-slide-enter-from,
.drawer-slide-leave-to {
  transform: translateX(-100%);
}

.drawer-slide-enter-to,
.drawer-slide-leave-from {
  transform: translateX(0);
}
</style>
