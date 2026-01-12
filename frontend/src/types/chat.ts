/**
 * 对话相关类型定义
 */

// 角色 ID
export type RoleId = 'financial_advisor' | 'policy_expert' | 'market_analyst' | 'purchase_consultant'

// 角色配置
export interface RoleConfig {
    name: string
    icon: string
    color: string
}

// 角色配置映射
export const ROLE_CONFIG: Record<RoleId, RoleConfig> = {
    financial_advisor: {
        name: '财务顾问',
        icon: 'Money',
        color: '#52c41a'
    },
    policy_expert: {
        name: '政策专家',
        icon: 'Document',
        color: '#1890ff'
    },
    market_analyst: {
        name: '市场分析师',
        icon: 'TrendCharts',
        color: '#faad14'
    },
    purchase_consultant: {
        name: '购房顾问',
        icon: 'CircleCheck',
        color: '#722ed1'
    }
}

// 思考步骤
export interface ThinkingStep {
    id: string
    type: 'planning' | 'role_dispatch' | 'tool_call' | 'tool_result' | 'synthesizing' | 'expert_analysis'
    content: string
    timestamp: number
    roleId?: RoleId
    roleName?: string
    toolName?: string
    toolArgs?: string
    status?: 'running' | 'done' | 'error'
}

// 聊天消息
export interface ChatMessage {
    id: string
    role: 'user' | 'assistant'
    content: string
    roleId?: RoleId
    roleName?: string
    roleIcon?: string
    roleColor?: string
    loading?: boolean
    timestamp?: number
    // 折叠展示相关
    isSummary?: boolean           // 是否是整合结果
    expertAnalysis?: ExpertAnalysis[]  // 专家分析（折叠内容）
    showExpertAnalysis?: boolean  // 是否展开专家分析
    // 思考过程相关
    thinkingSteps?: ThinkingStep[]  // 思考步骤
    showThinking?: boolean          // 是否展开思考过程
}

// 专家分析（用于折叠展示）
export interface ExpertAnalysis {
    roleId: RoleId
    roleName: string
    roleIcon: string
    roleColor: string
    content: string
}

// 聊天请求参数
export interface ChatParams {
    session_id: string
    message: string
    mode?: 'standard' | 'discussion'
    conversation_id?: string
    user_id?: string
}

// SSE 事件类型
export type SSEEventType =
    | 'conversation_created'
    | 'thinking_start'    // 开始思考
    | 'thinking_step'     // 思考步骤
    | 'tool_call'         // 工具调用
    | 'tool_result'       // 工具结果
    | 'role_start'
    | 'role_result'
    | 'content_delta'     // 流式内容增量
    | 'discussion'
    | 'error'
    | 'done'

// SSE 事件
export interface SSEEvent {
    type: SSEEventType
    role?: string
    name?: string
    icon?: string
    content?: string
    delta?: string        // 流式内容增量
    code?: number
    message?: string
    conversation_id?: string
    title?: string        // 对话标题
    from?: string
    round?: number
    is_summary?: boolean  // 是否是整合结果
    after_tool?: boolean  // 是否是工具调用后的内容
    // 思考过程相关
    step_type?: 'planning' | 'role_dispatch' | 'tool_call' | 'tool_result' | 'synthesizing'
    tool_name?: string
    tool_args?: string
}

// 快捷问题
export interface QuickQuestion {
    text: string
    query: string
}

// 默认快捷问题
export const DEFAULT_QUICK_QUESTIONS: QuickQuestion[] = [
    { text: '贷款怎么算', query: '我想了解房贷怎么计算，月供是多少？' },
    { text: '限购政策', query: '南宁现在还限购吗？外地人能买几套房？' },
    { text: '现在能买吗', query: '现在是买房的好时机吗？市场行情怎么样？' }
]
