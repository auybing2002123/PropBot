/**
 * 对话 API
 */
import api from './index'
import { createSSEClient, type SSEClient } from '@/utils/sse'
import type { ChatParams } from '@/types/chat'

/**
 * 创建对话客户端（支持取消）
 * @param params 对话参数
 * @returns SSE 客户端，可调用 abort() 取消
 */
export function createChatClient(params: ChatParams): SSEClient {
    return createSSEClient('/chat', params)
}

/**
 * 清除会话上下文
 * @param sessionId 会话 ID
 */
export async function clearSession(sessionId: string): Promise<{ session_id: string }> {
    return api.delete(`/chat/${sessionId}`)
}
