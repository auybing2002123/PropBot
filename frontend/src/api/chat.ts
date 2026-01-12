/**
 * 对话 API
 */
import api from './index'
import { createSSEClient } from '@/utils/sse'
import type { SSEEvent, ChatParams } from '@/types/chat'

/**
 * 发送对话消息（流式响应）
 * @param params 对话参数
 */
export async function* sendMessage(params: ChatParams): AsyncGenerator<SSEEvent> {
    const client = createSSEClient('/chat', params)
    yield* client.stream()
}

/**
 * 清除会话上下文
 * @param sessionId 会话 ID
 */
export async function clearSession(sessionId: string): Promise<{ session_id: string }> {
    return api.delete(`/chat/${sessionId}`)
}
