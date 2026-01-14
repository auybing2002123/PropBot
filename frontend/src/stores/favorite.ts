/**
 * 关注 Store
 * 管理用户关注的问答对
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { addFavorite, getFavorites, deleteFavorite, type Favorite, type FavoriteListResponse } from '@/api/favorite'
import { useAuthStore } from './auth'
import { ElMessage } from 'element-plus'

export const useFavoriteStore = defineStore('favorite', () => {
    // 状态
    const favorites = ref<Favorite[]>([])
    const total = ref(0)
    const loading = ref(false)
    const loaded = ref(false)

    // 计算属性
    const count = computed(() => favorites.value.length)

    // 获取收藏列表
    async function fetchFavorites(page = 1) {
        const authStore = useAuthStore()
        if (!authStore.userId) return

        loading.value = true
        try {
            // 注意：响应拦截器已经解包，res 直接是 data
            const res = await getFavorites(authStore.userId, page) as unknown as FavoriteListResponse
            if (res && res.items) {
                favorites.value = res.items
                total.value = res.total
                loaded.value = true
            }
        } catch (e) {
            console.error('获取收藏列表失败:', e)
        } finally {
            loading.value = false
        }
    }

    // 添加收藏
    async function add(data: {
        messageId?: string
        conversationId?: string
        question: string
        answer: string
    }) {
        const authStore = useAuthStore()
        if (!authStore.userId) {
            ElMessage.warning('请先登录')
            return false
        }

        try {
            // 注意：响应拦截器已经解包，res 直接是 Favorite 对象
            const res = await addFavorite({
                user_id: authStore.userId,
                message_id: data.messageId,
                conversation_id: data.conversationId,
                question: data.question,
                answer: data.answer
            }) as unknown as Favorite

            if (res && res.id) {
                // 添加到列表头部
                favorites.value.unshift(res)
                total.value++
                ElMessage.success('关注成功')
                return true
            }
        } catch (e) {
            console.error('添加收藏失败:', e)
            ElMessage.error('关注失败')
        }
        return false
    }

    // 删除收藏
    async function remove(favoriteId: string) {
        const authStore = useAuthStore()
        if (!authStore.userId) return false

        try {
            // 注意：响应拦截器已经解包，成功时不会抛异常
            await deleteFavorite(favoriteId, authStore.userId)
            favorites.value = favorites.value.filter(f => f.id !== favoriteId)
            total.value--
            ElMessage.success('已取消关注')
            return true
        } catch (e) {
            console.error('删除收藏失败:', e)
            ElMessage.error('取消关注失败')
        }
        return false
    }

    // 检查是否已收藏（通过 messageId）
    function isFavorited(messageId: string) {
        return favorites.value.some(f => f.message_id === messageId)
    }

    // 清空（登出时调用）
    function clear() {
        favorites.value = []
        total.value = 0
        loaded.value = false
    }

    return {
        favorites,
        total,
        loading,
        loaded,
        count,
        fetchFavorites,
        add,
        remove,
        isFavorited,
        clear
    }
})
