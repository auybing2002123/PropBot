/**
 * SSE (Server-Sent Events) 客户端
 * 用于处理流式响应
 */
import type { SSEEvent } from '@/types/chat'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api/v1'

/**
 * 创建 SSE 客户端
 * @param endpoint API 端点（不含 baseURL）
 * @param body 请求体
 */
export function createSSEClient(endpoint: string, body: object) {
    const url = `${API_BASE}${endpoint}`

    return {
        /**
         * 流式读取 SSE 事件
         */
        async *stream(): AsyncGenerator<SSEEvent> {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(body)
            })

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`)
            }

            if (!response.body) {
                throw new Error('Response body is null')
            }

            const reader = response.body.getReader()
            const decoder = new TextDecoder()
            let buffer = ''

            try {
                while (true) {
                    const { done, value } = await reader.read()

                    if (done) {
                        break
                    }

                    // 解码并添加到缓冲区
                    buffer += decoder.decode(value, { stream: true })

                    // 按行分割处理
                    const lines = buffer.split('\n')
                    // 保留最后一个可能不完整的行
                    buffer = lines.pop() || ''

                    for (const line of lines) {
                        // SSE 格式: "data: {...}"
                        if (line.startsWith('data: ')) {
                            try {
                                const jsonStr = line.slice(6) // 去掉 "data: " 前缀
                                if (jsonStr.trim()) {
                                    const data = JSON.parse(jsonStr) as SSEEvent
                                    yield data
                                }
                            } catch (e) {
                                console.warn('解析 SSE 数据失败:', line, e)
                            }
                        }
                    }
                }

                // 处理缓冲区中剩余的数据
                if (buffer.startsWith('data: ')) {
                    try {
                        const jsonStr = buffer.slice(6)
                        if (jsonStr.trim()) {
                            const data = JSON.parse(jsonStr) as SSEEvent
                            yield data
                        }
                    } catch (e) {
                        console.warn('解析剩余 SSE 数据失败:', buffer, e)
                    }
                }
            } finally {
                reader.releaseLock()
            }
        }
    }
}

/**
 * 发送聊天消息并获取流式响应
 * @param params 聊天参数
 */
export async function* streamChat(params: {
    session_id: string
    message: string
    mode?: 'standard' | 'discussion'
    conversation_id?: string
    user_id?: string
}): AsyncGenerator<SSEEvent> {
    const client = createSSEClient('/chat', params)
    yield* client.stream()
}
