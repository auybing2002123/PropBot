# 需求文档

## 简介

本文档定义了购房决策智能助手的核心 Agent 系统需求，包括伪多 Agent 引擎、角色系统、工具调用和对话 API。系统采用"一个大脑，多个人格"的架构，对外表现为多智能体协作，内部实现为单 Agent + 多角色 + 多工具。

## 术语表

- **Agent_Engine**: 伪多 Agent 引擎，负责意图识别、角色调度、工具调用和结果整合
- **Role**: 专业角色，包含特定的系统提示词和可用工具集
- **Tool**: Agent 可调用的功能模块，如贷款计算、政策检索等
- **Intent_Recognizer**: 意图识别器，分析用户输入确定需要哪些角色
- **LLM_Client**: 大语言模型客户端，封装 DeepSeek API 调用
- **Chat_API**: 对话接口，处理用户消息并返回 Agent 响应
- **Calculator_API**: 计算器接口，提供直接的财务计算功能

## 需求列表

### 需求 1: LLM 客户端封装

**用户故事:** 作为开发者，我需要一个统一的 LLM 客户端，以便轻松调用 DeepSeek API 并支持工具调用。

#### 验收标准

1. LLM_Client 应能调用 DeepSeek API，支持 messages 和可选的 tools 参数
2. LLM_Client 应支持 tool_choice 参数用于函数调用
3. 当 API 调用失败时，LLM_Client 应返回描述性错误信息
4. LLM_Client 应使用 async/await 进行非阻塞 API 调用
5. LLM_Client 应从环境配置读取 API 密钥

### 需求 2: 工具基础框架

**用户故事:** 作为开发者，我需要一个工具框架，以便轻松定义和注册新工具。

#### 验收标准

1. Tool_Base 应定义 name、description 和 parameters schema
2. Tool_Base 应提供 execute 方法用于工具执行
3. Tool_Base 应能转换为 OpenAI 函数调用 schema 格式
4. Tool_Registry 应能按名称注册和检索工具
5. 当工具执行时，Tool_Base 应验证输入参数

### 需求 3: 财务计算工具

**用户故事:** 作为用户，我需要计算贷款和成本，以便了解我的财务状况。

#### 验收标准

1. 当调用 calc_loan 时，工具应根据房价、首付比例、年限和利率计算贷款金额、月供、总利息
2. 当调用 calc_loan 时，工具应支持等额本息和等额本金两种还款方式
3. 当调用 calc_tax 时，工具应根据房价、面积、房龄、是否首套计算契税、增值税、个税、中介费
4. 当调用 calc_total_cost 时，工具应汇总首付、贷款利息、税费和其他费用
5. 当调用 assess_pressure 时，工具应计算月供收入比并返回压力等级（低/中/高）

### 需求 4: 市场查询工具

**用户故事:** 作为用户，我需要查询市场数据，以便了解房地产市场行情。

#### 验收标准

1. 当调用 query_market 时，工具应返回指定城市和区域的均价、成交量、库存量
2. 当调用 query_price_trend 时，工具应返回指定城市和区域的历史房价数据
3. 当调用 compare_districts 时，工具应返回多个区域的对比数据
4. 当调用 judge_timing 时，工具应根据市场数据返回时机评分和建议

### 需求 5: 政策检索工具

**用户故事:** 作为用户，我需要搜索政策信息，以便了解限购限贷政策。

#### 验收标准

1. 当调用 search_policy 时，工具应从知识库返回相关政策文档
2. 当调用 search_faq 时，工具应从知识库返回相关 FAQ 条目
3. Policy_Tool 应使用向量相似度搜索进行语义匹配
4. 当提供 city 参数时，Policy_Tool 应按城市过滤结果

### 需求 6: 角色定义

**用户故事:** 作为系统，我需要预定义的角色，以便为不同类型的问题提供专业回答。

#### 验收标准

1. Role_System 应定义 Financial_Advisor（财务顾问）角色，配备贷款和税费计算工具
2. Role_System 应定义 Policy_Expert（政策专家）角色，配备政策搜索工具
3. Role_System 应定义 Market_Analyst（市场分析师）角色，配备市场查询工具
4. Role_System 应定义 Purchase_Consultant（购房顾问）角色，用于整合结果
5. 当加载角色时，Role_System 应提供角色专属的系统提示词和可用工具列表

### 需求 7: 意图识别

**用户故事:** 作为系统，我需要识别用户意图，以便将问题路由到合适的角色。

#### 验收标准

1. 当用户输入包含财务关键词时，Intent_Recognizer 应返回 Financial_Advisor 角色
2. 当用户输入包含政策关键词时，Intent_Recognizer 应返回 Policy_Expert 角色
3. 当用户输入包含市场关键词时，Intent_Recognizer 应返回 Market_Analyst 角色
4. 当用户输入需要多个角色时，Intent_Recognizer 应返回所有需要的角色
5. 如果关键词匹配失败，Intent_Recognizer 应使用 LLM 进行意图分类

### 需求 8: Agent 引擎核心

**用户故事:** 作为用户，我需要智能回答，以便获得专业的购房建议。

#### 验收标准

1. 当处理用户输入时，Agent_Engine 应首先识别需要的角色
2. 当执行角色时，Agent_Engine 应使用系统提示词和用户输入构建角色专属提示
3. 当 LLM 返回工具调用时，Agent_Engine 应执行工具并将结果反馈给 LLM
4. 当需要多个角色时，Agent_Engine 应执行每个角色并整合结果
5. Agent_Engine 应维护对话上下文以支持多轮对话

### 需求 9: 对话 API

**用户故事:** 作为前端，我需要对话 API，以便发送用户消息并接收 Agent 响应。

#### 验收标准

1. Chat_API 应在请求体中接受 session_id 和 message
2. Chat_API 应在响应中返回角色信息和内容
3. Chat_API 应支持使用 Server-Sent Events 的流式响应
4. 当处理开始时，Chat_API 应发送 role_start 事件，包含角色名称和图标
5. 当处理完成时，Chat_API 应发送 done 事件

### 需求 10: 计算器 API

**用户故事:** 作为前端，我需要计算器 API，以便直接调用财务计算而无需对话。

#### 验收标准

1. Calculator_API 应提供 POST /api/v1/calc/loan 端点用于贷款计算
2. Calculator_API 应提供 POST /api/v1/calc/tax 端点用于税费计算
3. Calculator_API 应提供 POST /api/v1/calc/total_cost 端点用于总成本计算
4. Calculator_API 应使用 Pydantic 模型验证请求参数
5. Calculator_API 应以统一响应格式返回结果，包含 code、message 和 data

### 需求 11: 错误处理

**用户故事:** 作为用户，我需要友好的错误提示，以便了解出了什么问题。

#### 验收标准

1. 当 LLM API 调用失败时，系统应返回错误码和用户友好的提示信息
2. 当工具执行失败时，系统应记录错误详情并向用户返回通用错误
3. 系统不应向前端暴露堆栈跟踪或敏感错误详情
4. 当缺少必需参数时，系统应返回验证错误并说明字段名称
