/**
 * API 响应类型定义
 */

// 统一响应格式
export interface ApiResponse<T = unknown> {
    code: number
    message: string
    data: T
}

// 分页响应
export interface PaginatedData<T> {
    items: T[]
    total: number
}

// 用户信息
export interface UserInfo {
    user_id: string
    username: string | null
    nickname: string | null
    created_at: string | null
}

// 对话信息
export interface Conversation {
    id: string
    user_id: string | null
    title: string | null
    created_at: string
    updated_at: string
}

// 消息信息
export interface Message {
    id: string
    role: 'user' | 'assistant'
    content: string
    metadata?: Record<string, unknown>
    created_at: string
}

// 对话详情（含消息）
export interface ConversationDetail extends Conversation {
    messages: Message[]
}

// 对话列表响应
export interface ConversationListData {
    conversations: Conversation[]
    total: number
}

// 消息列表响应
export interface MessageListData {
    messages: Message[]
    total: number
}
