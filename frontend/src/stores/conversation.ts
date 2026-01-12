/**
 * 对话记录状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useChatStore } from './chat'
import { useAuthStore } from './auth'
import {
    listConversations,
    getConversation,
    deleteConversation as apiDeleteConversation
} from '@/api/conversation'
import type { ChatMessage } from '@/types/chat'

// 对话记录类型
export interface Conversation {
    id: string
    title?: string
    created_at: string
    updated_at: string
    message_count: number
}

export const useConversationStore = defineStore('conversation', () => {
    // 对话列表
    const conversations = ref<Conversation[]>([])
    // 加载状态
    const loading = ref(false)

    /**
     * 加载对话列表
     */
    async function loadConversations() {
        loading.value = true
        try {
            // 获取当前用户 ID
            const authStore = useAuthStore()
            const userId = authStore.userId || undefined

            const res = await listConversations(userId)
            if (res && res.conversations) {
                conversations.value = res.conversations.map((conv: any) => ({
                    id: conv.id,
                    title: conv.title || getDefaultTitle(conv),
                    created_at: conv.created_at,
                    updated_at: conv.updated_at,
                    message_count: conv.message_count || 0
                }))
            }
        } catch (error) {
            console.error('加载对话列表失败:', error)
        } finally {
            loading.value = false
        }
    }

    /**
     * 获取默认标题
     */
    function getDefaultTitle(conv: any): string {
        // 如果有第一条消息，用它作为标题
        if (conv.first_message) {
            const msg = conv.first_message
            return msg.length > 20 ? msg.slice(0, 20) + '...' : msg
        }
        return '新对话'
    }

    /**
     * 加载对话详情并切换到该对话
     */
    async function loadConversation(convId: string) {
        const chatStore = useChatStore()

        try {
            const res = await getConversation(convId, true)
            if (res && res.messages) {
                // 转换消息格式
                const messages: ChatMessage[] = res.messages.map((msg: any) => ({
                    id: msg.id,
                    role: msg.role,
                    content: msg.content,
                    roleId: msg.role_id,
                    roleName: msg.role_name,
                    roleIcon: msg.role_icon,
                    roleColor: msg.role_color,
                    timestamp: new Date(msg.created_at).getTime(),
                    isSummary: msg.is_summary,
                    thinkingSteps: msg.thinking_steps || [],
                    showThinking: false
                }))

                chatStore.loadConversation(convId, messages)
            }
        } catch (error) {
            console.error('加载对话详情失败:', error)
        }
    }

    /**
     * 删除对话
     */
    async function deleteConversation(convId: string) {
        try {
            const res = await apiDeleteConversation(convId)
            if (res && res.deleted) {
                // 从列表中移除
                conversations.value = conversations.value.filter(c => c.id !== convId)
            }
        } catch (error) {
            console.error('删除对话失败:', error)
            throw error
        }
    }

    /**
     * 添加新对话到列表
     */
    function addConversation(conv: Conversation) {
        // 添加到列表开头
        conversations.value.unshift(conv)
    }

    /**
     * 更新对话标题
     */
    function updateConversationTitle(convId: string, title: string) {
        const conv = conversations.value.find(c => c.id === convId)
        if (conv) {
            conv.title = title
            conv.updated_at = new Date().toISOString()
        }
    }

    return {
        conversations,
        loading,
        loadConversations,
        loadConversation,
        deleteConversation,
        addConversation,
        updateConversationTitle
    }
})
