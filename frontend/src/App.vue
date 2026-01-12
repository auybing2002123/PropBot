<script setup lang="ts">
/**
 * 根组件
 */
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// 应用初始化：尝试自动登录
onMounted(async () => {
  await authStore.init()
})
</script>

<template>
  <router-view />
</template>

<style>
/* 全局样式已在 main.ts 中导入 */
</style>
