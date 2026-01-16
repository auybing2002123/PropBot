/**
 * 对话历史 API
 */
import api from './index'
import type {
    Conversation,
    ConversationDetail,
    ConversationListData,
    MessageListData
} from '@/types/api'

/**
 * 获取对话列表
 * @param userId 用户 ID（可选）
 * @param limit 返回数量
 * @param offset 偏移量
 */
export async function listConversations(
    userId?: string,
    limit: number = 20,
    offset: number = 0
): Promise<ConversationListData> {
    return api.get('/conversations', {
        params: { user_id: userId, limit, offset }
    })
}

/**
 * 创建新对话
 * @param userId 用户 ID（可选）
 * @param title 对话标题（可选）
 */
export async function createConversation(
    userId?: string,
    title?: string
): Promise<Conversation> {
    return api.post('/conversations', { user_id: userId, title })
}

/**
 * 获取对话详情
 * @param conversationId 对话 ID
 * @param includeMessages 是否包含消息列表
 */
export async function getConversation(
    conversationId: string,
    includeMessages: boolean = true
): Promise<ConversationDetail> {
    return api.get(`/conversations/${conversationId}`, {
        params: { include_messages: includeMessages }
    })
}

/**
 * 更新对话标题
 * @param conversationId 对话 ID
 * @param title 新标题
 */
export async function updateConversation(
    conversationId: string,
    title: string
): Promise<Conversation> {
    return api.put(`/conversations/${conversationId}`, { title })
}

/**
 * 删除对话
 * @param conversationId 对话 ID
 */
export async function deleteConversation(conversationId: string): Promise<{ deleted: boolean }> {
    return api.delete(`/conversations/${conversationId}`)
}

/**
 * 获取对话消息列表
 * @param conversationId 对话 ID
 * @param limit 返回数量
 * @param offset 偏移量
 */
export async function getMessages(
    conversationId: string,
    limit: number = 50,
    offset: number = 0
): Promise<MessageListData> {
    return api.get(`/conversations/${conversationId}/messages`, {
        params: { limit, offset }
    })
}
