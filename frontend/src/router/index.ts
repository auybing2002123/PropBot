/**
 * 路由配置
 */
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
    // 登录页（独立布局）
    {
        path: '/login',
        name: 'Login',
        component: () => import('@/views/LoginView.vue'),
        meta: { title: '登录', requiresAuth: false }
    },
    // 主应用（需要登录）
    {
        path: '/',
        component: () => import('@/components/layout/AppLayout.vue'),
        meta: { requiresAuth: true },
        children: [
            {
                path: '',
                redirect: '/chat'
            },
            {
                path: 'chat',
                name: 'Chat',
                component: () => import('@/views/ChatView.vue'),
                meta: { title: '智能对话' }
            },
            {
                path: 'calculator',
                name: 'Calculator',
                component: () => import('@/views/CalculatorView.vue'),
                meta: { title: '购房计算器' }
            },
            {
                path: 'market',
                name: 'Market',
                component: () => import('@/views/MarketView.vue'),
                meta: { title: '市场分析' }
            },
            {
                path: 'policy',
                name: 'Policy',
                component: () => import('@/views/PolicyView.vue'),
                meta: { title: '购房政策' }
            },
            {
                path: 'profile',
                name: 'Profile',
                component: () => import('@/views/ProfileView.vue'),
                meta: { title: '我的' }
            },
            {
                path: 'help',
                name: 'Help',
                component: () => import('@/views/HelpView.vue'),
                meta: { title: '帮助中心' }
            }
        ]
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// 路由守卫
router.beforeEach(async (to, _from, next) => {
    // 设置页面标题
    const title = to.meta.title as string
    document.title = title ? `${title} - 购房决策智能助手` : '购房决策智能助手'

    // 检查是否需要登录
    const requiresAuth = to.matched.some(record => record.meta.requiresAuth !== false)

    if (requiresAuth) {
        const authStore = useAuthStore()

        // 如果未登录，跳转到登录页
        if (!authStore.isLoggedIn) {
            next({ path: '/login', query: { redirect: to.fullPath } })
            return
        }
    }

    // 如果已登录且访问登录页，跳转到首页
    if (to.path === '/login') {
        const authStore = useAuthStore()
        if (authStore.isLoggedIn) {
            next({ path: '/' })
            return
        }
    }

    next()
})

export default router
