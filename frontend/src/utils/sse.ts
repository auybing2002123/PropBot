/**
 * SSE (Server-Sent Events) 客户端
 * 用于处理流式响应，支持取消
 */
import type { SSEEvent } from '@/types/chat'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api/v1'

/**
 * SSE 客户端接口
 */
export interface SSEClient {
    stream(): AsyncGenerator<SSEEvent>
    abort(): void
    isAborted(): boolean
}

/**
 * 创建 SSE 客户端
 * @param endpoint API 端点（不含 baseURL）
 * @param body 请求体
 */
export function createSSEClient(endpoint: string, body: object): SSEClient {
    const url = `${API_BASE}${endpoint}`
    const abortController = new AbortController()
    let aborted = false

    return {
        /**
         * 中断 SSE 连接
         */
        abort() {
            aborted = true
            abortController.abort()
        },

        /**
         * 检查是否已中断
         */
        isAborted() {
            return aborted
        },

        /**
         * 流式读取 SSE 事件
         */
        async *stream(): AsyncGenerator<SSEEvent> {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(body),
                signal: abortController.signal
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
                    // 检查是否已中断
                    if (aborted) {
                        break
                    }

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
                        // 再次检查是否已中断
                        if (aborted) {
                            return
                        }

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

                // 处理缓冲区中剩余的数据（如果未中断）
                if (!aborted && buffer.startsWith('data: ')) {
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
            } catch (e) {
                // 如果是中断导致的错误，静默处理
                if (aborted || (e instanceof Error && e.name === 'AbortError')) {
                    return
                }
                throw e
            } finally {
                reader.releaseLock()
            }
        }
    }
}

/**
 * 发送聊天消息并获取流式响应（带取消支持）
 * @param params 聊天参数
 * @returns SSE 客户端，可调用 abort() 取消
 */
export function createChatClient(params: {
    session_id: string
    message: string
    mode?: 'standard' | 'discussion'
    conversation_id?: string
    user_id?: string
}): SSEClient {
    return createSSEClient('/chat', params)
}
