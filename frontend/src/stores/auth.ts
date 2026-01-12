/**
 * 用户认证状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { register, login, getCurrentUser } from '@/api/auth'
import type { UserInfo } from '@/types/api'

// localStorage 键名
const USER_ID_KEY = 'user_id'
const USERNAME_KEY = 'username'
const NICKNAME_KEY = 'nickname'

export const useAuthStore = defineStore('auth', () => {
    // 状态
    const userId = ref<string | null>(localStorage.getItem(USER_ID_KEY))
    const username = ref<string | null>(localStorage.getItem(USERNAME_KEY))
    const nickname = ref<string | null>(localStorage.getItem(NICKNAME_KEY))
    const isLoading = ref(false)

    // 计算属性
    const isLoggedIn = computed(() => !!userId.value)

    /**
     * 用户注册
     */
    async function registerUser(
        usernameVal: string,
        password: string,
        nicknameVal?: string
    ): Promise<boolean> {
        isLoading.value = true
        try {
            const user = await register(usernameVal, password, nicknameVal)
            saveUserInfo(user)
            return true
        } catch (error) {
            console.error('注册失败:', error)
            throw error
        } finally {
            isLoading.value = false
        }
    }

    /**
     * 用户登录
     */
    async function loginUser(usernameVal: string, password: string): Promise<boolean> {
        isLoading.value = true
        try {
            const user = await login(usernameVal, password)
            saveUserInfo(user)
            return true
        } catch (error) {
            console.error('登录失败:', error)
            throw error
        } finally {
            isLoading.value = false
        }
    }

    /**
     * 保存用户信息到状态和 localStorage
     */
    function saveUserInfo(user: UserInfo) {
        userId.value = user.user_id
        username.value = user.username
        nickname.value = user.nickname

        localStorage.setItem(USER_ID_KEY, user.user_id)
        if (user.username) {
            localStorage.setItem(USERNAME_KEY, user.username)
        }
        if (user.nickname) {
            localStorage.setItem(NICKNAME_KEY, user.nickname)
        }
    }

    /**
     * 获取用户信息
     */
    async function fetchUserInfo(): Promise<UserInfo | null> {
        if (!userId.value) {
            return null
        }

        try {
            const user = await getCurrentUser(userId.value)
            saveUserInfo(user)
            return user
        } catch (error) {
            console.error('获取用户信息失败:', error)
            clearAuth()
            return null
        }
    }

    /**
     * 清除认证信息
     */
    function clearAuth() {
        userId.value = null
        username.value = null
        nickname.value = null
        localStorage.removeItem(USER_ID_KEY)
        localStorage.removeItem(USERNAME_KEY)
        localStorage.removeItem(NICKNAME_KEY)
    }

    /**
     * 初始化：验证已保存的登录状态
     */
    async function init(): Promise<boolean> {
        if (userId.value) {
            const user = await fetchUserInfo()
            return !!user
        }
        return false
    }

    return {
        // 状态
        userId,
        username,
        nickname,
        isLoading,
        // 计算属性
        isLoggedIn,
        // 方法
        registerUser,
        loginUser,
        fetchUserInfo,
        clearAuth,
        init
    }
})
