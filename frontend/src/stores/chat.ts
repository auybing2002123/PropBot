/**
 * 对话状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { v4 as uuidv4 } from 'uuid'
import { sendMessage, clearSession } from '@/api/chat'
import { ROLE_CONFIG } from '@/types/chat'
import { useConversationStore } from './conversation'
import type { ChatMessage, RoleId, SSEEvent, ExpertAnalysis, ThinkingStep } from '@/types/chat'

export const useChatStore = defineStore('chat', () => {
    // 状态
    const sessionId = ref(uuidv4())
    const conversationId = ref<string | null>(null)
    const messages = ref<ChatMessage[]>([])
    const isLoading = ref(false)
    const currentRoleMessageId = ref<string | null>(null)

    // 深度分析模式（discussion mode）
    const deepMode = ref(false)

    // 临时存储专家分析（用于折叠展示）
    const pendingExpertAnalysis = ref<ExpertAnalysis[]>([])

    // 当前是否在处理整合结果（用于区分 content_delta 是专家分析还是最终结果）
    const isProcessingSummary = ref(false)

    // 思考过程状态
    const thinkingSteps = ref<ThinkingStep[]>([])
    const isThinking = ref(false)
    const showThinking = ref(true)  // 默认展开思考过程
    const thinkingStartTime = ref<number>(0)  // 思考开始时间戳

    /**
     * 添加用户消息
     */
    function addUserMessage(content: string): string {
        const id = uuidv4()
        messages.value.push({
            id,
            role: 'user',
            content,
            timestamp: Date.now()
        })
        return id
    }

    /**
     * 添加角色消息（loading 状态）
     */
    function addRoleMessage(roleId: RoleId, isSummary: boolean = false): string {
        const id = uuidv4()
        const config = ROLE_CONFIG[roleId]

        messages.value.push({
            id,
            role: 'assistant',
            content: '',
            roleId,
            roleName: config.name,
            roleIcon: config.icon,
            roleColor: config.color,
            loading: true,
            timestamp: Date.now(),
            isSummary,
            expertAnalysis: isSummary ? [...pendingExpertAnalysis.value] : undefined,
            showExpertAnalysis: false,
            // 把当前的思考步骤附加到消息上
            thinkingSteps: [...thinkingSteps.value],
            showThinking: true  // 默认展开
        })

        currentRoleMessageId.value = id
        return id
    }

    /**
     * 更新角色消息内容
     */
    function updateRoleMessage(id: string, content: string, isSummary: boolean = false) {
        const msg = messages.value.find(m => m.id === id)
        if (msg) {
            msg.content = content
            msg.loading = false

            // 更新思考步骤（确保包含最新的步骤）
            msg.thinkingSteps = [...thinkingSteps.value]

            // 如果是整合结果，附加专家分析
            if (isSummary && pendingExpertAnalysis.value.length > 0) {
                msg.expertAnalysis = [...pendingExpertAnalysis.value]
                msg.isSummary = true
            }
        }
    }

    /**
     * 清空临时专家分析
     */
    function clearPendingExpertAnalysis() {
        pendingExpertAnalysis.value = []
    }

    /**
     * 清空思考步骤
     */
    function clearThinkingSteps() {
        thinkingSteps.value = []
        isThinking.value = false
        thinkingStartTime.value = 0
    }

    /**
     * 切换思考过程展开状态
     */
    function toggleThinking() {
        showThinking.value = !showThinking.value
    }

    /**
     * 切换专家分析展开状态
     */
    function toggleExpertAnalysis(messageId: string) {
        const msg = messages.value.find(m => m.id === messageId)
        if (msg) {
            msg.showExpertAnalysis = !msg.showExpertAnalysis
        }
    }

    /**
     * 切换消息的思考过程展开状态
     */
    function toggleMessageThinking(messageId: string) {
        const msg = messages.value.find(m => m.id === messageId)
        if (msg) {
            msg.showThinking = !msg.showThinking
        }
    }

    /**
     * 发送消息并处理流式响应
     */
    async function send(content: string, userId?: string) {
        if (isLoading.value || !content.trim()) {
            return
        }

        isLoading.value = true
        addUserMessage(content)
        clearPendingExpertAnalysis()  // 清空之前的专家分析
        clearThinkingSteps()  // 清空之前的思考步骤
        isProcessingSummary.value = false  // 重置整合状态
        // 在清空后设置思考状态和开始时间
        isThinking.value = true
        thinkingStartTime.value = Date.now()

        // 立即创建消息框，不等 thinking_start 事件
        const msgId = uuidv4()
        messages.value.push({
            id: msgId,
            role: 'assistant',
            content: '',
            roleName: '智能助手',
            roleIcon: 'ChatDotRound',
            roleColor: '#409eff',
            loading: true,
            timestamp: Date.now(),
            thinkingSteps: [],
            showThinking: false
        })
        currentRoleMessageId.value = msgId

        try {
            const generator = sendMessage({
                session_id: sessionId.value,
                message: content,
                mode: deepMode.value ? 'discussion' : 'standard',
                conversation_id: conversationId.value || undefined,
                user_id: userId
            })

            for await (const event of generator) {
                handleSSEEvent(event)
            }
        } catch (error) {
            console.error('发送消息失败:', error)
            messages.value.push({
                id: uuidv4(),
                role: 'assistant',
                content: '抱歉，服务暂时不可用，请稍后重试。',
                timestamp: Date.now()
            })
        } finally {
            isLoading.value = false
            isThinking.value = false
            isProcessingSummary.value = false  // 重置整合状态
            currentRoleMessageId.value = null
            clearPendingExpertAnalysis()
        }
    }

    /**
     * 处理 SSE 事件
     */
    function handleSSEEvent(event: SSEEvent) {
        switch (event.type) {
            case 'conversation_created':
                if (event.conversation_id) {
                    conversationId.value = event.conversation_id
                    // 添加新对话到列表
                    const conversationStore = useConversationStore()
                    conversationStore.addConversation({
                        id: event.conversation_id,
                        title: event.title || '新对话',
                        created_at: new Date().toISOString(),
                        updated_at: new Date().toISOString(),
                        message_count: 1
                    })
                }
                break

            case 'thinking_start':
                // 消息框已在 send() 中创建，这里只更新状态
                isThinking.value = true
                showThinking.value = false  // 默认折叠思考过程
                break

            case 'thinking_step':
                if (event.content) {
                    const step: ThinkingStep = {
                        id: uuidv4(),
                        type: event.step_type || 'planning',
                        content: event.content,
                        timestamp: Date.now(),
                        roleId: event.role as RoleId | undefined,
                        roleName: event.role ? ROLE_CONFIG[event.role as RoleId]?.name : undefined,
                        status: 'done'
                    }
                    thinkingSteps.value.push(step)

                    // 同步到当前消息
                    if (currentRoleMessageId.value) {
                        const msg = messages.value.find(m => m.id === currentRoleMessageId.value)
                        if (msg) {
                            if (!msg.thinkingSteps) msg.thinkingSteps = []
                            msg.thinkingSteps.push(step)
                        }
                    }
                }
                break

            case 'tool_call':
                if (event.tool_name) {
                    // 工具名称映射为中文（含详细描述）
                    const toolNameMap: Record<string, { name: string; desc: string }> = {
                        'search_policy': { name: '政策检索', desc: '正在检索相关政策文档...' },
                        'search_faq': { name: 'FAQ检索', desc: '正在查找常见问题解答...' },
                        'search_guide': { name: '流程指南检索', desc: '正在检索购房流程指南...' },
                        'search_news': { name: '新闻检索', desc: '正在搜索最新房产资讯...' },
                        'calc_loan': { name: '贷款计算', desc: '正在计算贷款方案...' },
                        'calc_monthly_payment': { name: '月供计算', desc: '正在计算月供金额...' },
                        'calc_tax': { name: '税费计算', desc: '正在计算购房税费...' },
                        'calc_total_cost': { name: '总成本计算', desc: '正在计算购房总成本...' },
                        'query_market': { name: '市场查询', desc: '正在查询市场数据...' },
                        'query_price_trend': { name: '价格走势查询', desc: '正在分析价格走势...' },
                        'generate_report': { name: '报告生成', desc: '正在生成分析报告...' }
                    }
                    const toolInfo = toolNameMap[event.tool_name] || {
                        name: event.tool_name,
                        desc: `正在调用 ${event.tool_name}...`
                    }

                    const step: ThinkingStep = {
                        id: uuidv4(),
                        type: 'tool_call',
                        content: toolInfo.desc,
                        timestamp: Date.now(),
                        toolName: toolInfo.name,
                        toolArgs: event.tool_args,
                        status: 'running'
                    }
                    thinkingSteps.value.push(step)

                    // 同步到当前消息
                    if (currentRoleMessageId.value) {
                        const msg = messages.value.find(m => m.id === currentRoleMessageId.value)
                        if (msg) {
                            if (!msg.thinkingSteps) msg.thinkingSteps = []
                            msg.thinkingSteps.push(step)
                        }
                    }
                }
                break

            case 'tool_result':
                if (event.tool_name) {
                    const toolNameMap: Record<string, string> = {
                        'search_policy': '政策检索',
                        'search_faq': 'FAQ检索',
                        'search_guide': '流程指南检索',
                        'search_news': '新闻检索',
                        'calc_loan': '贷款计算',
                        'calc_monthly_payment': '月供计算',
                        'calc_tax': '税费计算',
                        'calc_total_cost': '总成本计算',
                        'query_market': '市场查询',
                        'query_price_trend': '价格走势查询',
                        'generate_report': '报告生成'
                    }
                    const toolDisplayName = toolNameMap[event.tool_name] || event.tool_name

                    const step: ThinkingStep = {
                        id: uuidv4(),
                        type: 'tool_result',
                        content: `${toolDisplayName} 完成`,
                        timestamp: Date.now(),
                        toolName: toolDisplayName,
                        status: 'done'
                    }
                    thinkingSteps.value.push(step)

                    // 同步到当前消息
                    if (currentRoleMessageId.value) {
                        const msg = messages.value.find(m => m.id === currentRoleMessageId.value)
                        if (msg) {
                            if (!msg.thinkingSteps) msg.thinkingSteps = []
                            msg.thinkingSteps.push(step)
                        }
                    }
                }
                break

            case 'role_start':
                if (event.role) {
                    const isSummary = event.is_summary || false
                    // 设置当前是否在处理整合结果
                    isProcessingSummary.value = isSummary

                    if (isSummary && currentRoleMessageId.value) {
                        // 整合结果：更新现有消息的角色信息
                        const msg = messages.value.find(m => m.id === currentRoleMessageId.value)
                        if (msg) {
                            const config = ROLE_CONFIG[event.role as RoleId]
                            msg.roleId = event.role as RoleId
                            msg.roleName = config.name
                            msg.roleIcon = config.icon
                            msg.roleColor = config.color
                            msg.isSummary = true
                            msg.expertAnalysis = [...pendingExpertAnalysis.value]
                            msg.content = ''  // 清空内容，准备接收流式内容
                        }
                    }
                    // 非整合结果不创建消息框，只在思考过程中展示
                }
                break

            case 'content_delta':
                // 流式内容增量 - 更新消息内容（单专家和整合结果都需要流式显示）
                if (event.delta && currentRoleMessageId.value) {
                    const msg = messages.value.find(m => m.id === currentRoleMessageId.value)
                    if (msg) {
                        // 如果还没设置角色信息，从事件中获取
                        if (event.role && !msg.roleId) {
                            const config = ROLE_CONFIG[event.role as RoleId]
                            if (config) {
                                msg.roleId = event.role as RoleId
                                msg.roleName = config.name
                                msg.roleIcon = config.icon
                                msg.roleColor = config.color
                            }
                        }
                        // 追加内容增量
                        msg.content = (msg.content || '') + event.delta
                        msg.loading = false  // 有内容了就不显示 loading
                    }
                }
                break

            case 'role_result':
                if (event.content) {
                    const isSummary = event.is_summary || false

                    if (!isSummary && event.role) {
                        // 非整合结果（单专家或多专家中的某个专家）
                        const config = ROLE_CONFIG[event.role as RoleId]

                        // 检查是否有多个专家（通过 pendingExpertAnalysis 判断）
                        // 如果已经有专家分析了，说明是多专家场景
                        const isMultiExpert = pendingExpertAnalysis.value.length > 0 ||
                            thinkingSteps.value.some(s => s.type === 'expert_analysis')

                        if (isMultiExpert) {
                            // 多专家场景：添加摘要到思考步骤（不是完整内容）
                            const summary = event.content.length > 100
                                ? event.content.substring(0, 100) + '...'
                                : event.content
                            const step: ThinkingStep = {
                                id: uuidv4(),
                                type: 'expert_analysis',
                                content: summary,
                                timestamp: Date.now(),
                                roleId: event.role as RoleId,
                                roleName: config?.name || event.role,
                                status: 'done'
                            }
                            thinkingSteps.value.push(step)

                            // 同步到当前消息的思考步骤
                            if (currentRoleMessageId.value) {
                                const msg = messages.value.find(m => m.id === currentRoleMessageId.value)
                                if (msg) {
                                    if (!msg.thinkingSteps) msg.thinkingSteps = []
                                    msg.thinkingSteps.push(step)
                                }
                            }
                        }
                        // 单专家场景：内容已通过 content_delta 流式显示，不需要再添加到思考步骤

                        // 添加到待整合的专家分析列表（完整内容，用于折叠展示）
                        pendingExpertAnalysis.value.push({
                            roleId: event.role as RoleId,
                            roleName: config?.name || event.role,
                            roleIcon: config?.icon || 'User',
                            roleColor: config?.color || '#409eff',
                            content: event.content
                        })
                    }

                    if (isSummary && currentRoleMessageId.value) {
                        // 整合结果：更新当前消息的内容和角色
                        const msg = messages.value.find(m => m.id === currentRoleMessageId.value)
                        if (msg && event.role) {
                            const config = ROLE_CONFIG[event.role as RoleId]
                            if (config) {
                                msg.roleId = event.role as RoleId
                                msg.roleName = config.name
                                msg.roleIcon = config.icon
                                msg.roleColor = config.color
                            }
                            msg.content = event.content
                            msg.isSummary = true
                            msg.expertAnalysis = [...pendingExpertAnalysis.value]
                            msg.loading = false
                        }
                    }
                }
                break

            case 'discussion':
                // 深度分析模式：多角色讨论事件
                if (event.from && event.content) {
                    const config = ROLE_CONFIG[event.from as RoleId]
                    const step: ThinkingStep = {
                        id: uuidv4(),
                        type: 'expert_analysis',
                        content: `【第${event.round || 1}轮讨论】${event.content}`,
                        timestamp: Date.now(),
                        roleId: event.from as RoleId,
                        roleName: config?.name || event.from,
                        status: 'done'
                    }
                    thinkingSteps.value.push(step)

                    // 同步到当前消息
                    if (currentRoleMessageId.value) {
                        const msg = messages.value.find(m => m.id === currentRoleMessageId.value)
                        if (msg) {
                            if (!msg.thinkingSteps) msg.thinkingSteps = []
                            msg.thinkingSteps.push(step)
                        }
                    }
                }
                break

            case 'error':
                console.error('SSE 错误:', event.code, event.message)
                isThinking.value = false
                if (currentRoleMessageId.value) {
                    updateRoleMessage(
                        currentRoleMessageId.value,
                        event.message || '处理失败，请重试'
                    )
                }
                break

            case 'done':
                isThinking.value = false

                if (currentRoleMessageId.value) {
                    const msg = messages.value.find(m => m.id === currentRoleMessageId.value)

                    // 如果消息还是 loading 状态且没有内容，说明流式输出可能失败了
                    // 尝试从 pendingExpertAnalysis 恢复
                    if (msg && msg.loading && !msg.content && pendingExpertAnalysis.value.length > 0) {
                        const lastExpert = pendingExpertAnalysis.value[pendingExpertAnalysis.value.length - 1]
                        msg.roleId = lastExpert.roleId
                        msg.roleName = lastExpert.roleName
                        msg.roleIcon = lastExpert.roleIcon
                        msg.roleColor = lastExpert.roleColor
                        msg.content = lastExpert.content
                        msg.loading = false
                    }

                    // 确保 loading 状态被清除
                    if (msg && msg.loading) {
                        msg.loading = false
                    }

                    if (msg && msg.thinkingSteps) {
                        // 更新"XX正在分析..."步骤为"XX分析完成"
                        // 但如果已经有"XX分析完成"的步骤，则删除"XX正在分析..."步骤（避免重复）
                        const roleNames = ['财务顾问', '政策专家', '市场分析师', '购房顾问']

                        // 先检查哪些角色已经有"分析完成"的步骤
                        const completedRoles = new Set<string>()
                        msg.thinkingSteps.forEach(step => {
                            for (const roleName of roleNames) {
                                if (step.content === `${roleName}分析完成`) {
                                    completedRoles.add(roleName)
                                    break
                                }
                            }
                        })

                        // 更新或删除"正在分析..."步骤
                        msg.thinkingSteps = msg.thinkingSteps.filter(step => {
                            for (const roleName of roleNames) {
                                if (step.content === `${roleName}正在分析...`) {
                                    if (completedRoles.has(roleName)) {
                                        // 已有"分析完成"，删除"正在分析..."
                                        return false
                                    } else {
                                        // 没有"分析完成"，更新为"分析完成"
                                        step.content = `${roleName}分析完成`
                                    }
                                    break
                                }
                            }
                            return true
                        })

                        // 同步更新全局思考步骤
                        const globalCompletedRoles = new Set<string>()
                        thinkingSteps.value.forEach(step => {
                            for (const roleName of roleNames) {
                                if (step.content === `${roleName}分析完成`) {
                                    globalCompletedRoles.add(roleName)
                                    break
                                }
                            }
                        })

                        thinkingSteps.value = thinkingSteps.value.filter(step => {
                            for (const roleName of roleNames) {
                                if (step.content === `${roleName}正在分析...`) {
                                    if (globalCompletedRoles.has(roleName)) {
                                        return false
                                    } else {
                                        step.content = `${roleName}分析完成`
                                    }
                                    break
                                }
                            }
                            return true
                        })
                    }
                }
                break
        }
    }

    /**
     * 设置深度分析模式
     */
    function setDeepMode(value: boolean) {
        deepMode.value = value
    }

    /**
     * 清除当前会话
     */
    async function clear() {
        try {
            await clearSession(sessionId.value)
        } catch (error) {
            console.warn('清除会话失败:', error)
        }

        messages.value = []
        sessionId.value = uuidv4()
        conversationId.value = null
        currentRoleMessageId.value = null
        clearPendingExpertAnalysis()
        clearThinkingSteps()
    }

    /**
     * 加载历史对话
     */
    function loadConversation(convId: string, historyMessages: ChatMessage[]) {
        conversationId.value = convId
        messages.value = historyMessages
    }

    return {
        // 状态
        sessionId,
        conversationId,
        messages,
        isLoading,
        deepMode,
        // 思考过程状态
        thinkingSteps,
        isThinking,
        showThinking,
        thinkingStartTime,
        // 方法
        addUserMessage,
        addRoleMessage,
        updateRoleMessage,
        toggleExpertAnalysis,
        toggleMessageThinking,
        toggleThinking,
        setDeepMode,
        send,
        clear,
        loadConversation
    }
})
