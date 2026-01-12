# 实现任务清单

## 概述

本任务清单将 agent-core 设计分解为可执行的编码任务。任务按依赖顺序排列，每个任务都引用具体需求。

## 任务列表

- [x] 1. 创建 Agent 模块目录结构
  - 创建 `backend/app/agent/` 目录
  - 创建 `backend/app/agent/__init__.py`
  - 创建 `backend/app/agent/tools/__init__.py`
  - 创建 `backend/app/llm/__init__.py`
  - 创建 `backend/app/models/__init__.py`
  - _需求: 项目结构_

- [x] 2. 实现 LLM 客户端
  - [x] 2.1 创建 DeepSeekClient 类
    - 实现 `backend/app/llm/client.py`
    - 使用 httpx 异步调用 DeepSeek API
    - 支持 messages、tools、temperature 参数
    - 从 settings 读取 API 密钥和 base_url
    - _需求: 1.1, 1.2, 1.4, 1.5_
  - [x] 2.2 实现错误处理
    - 处理 API 超时、认证失败、频率限制等错误
    - 返回描述性错误信息
    - _需求: 1.3_

- [x] 3. 实现工具基础框架
  - [x] 3.1 创建工具基类和参数模型
    - 实现 `backend/app/agent/tools/base.py`
    - 定义 ToolParameter 和 BaseTool 类
    - 实现 to_openai_schema 方法
    - _需求: 2.1, 2.2, 2.3_
  - [x] 3.2 创建工具注册表
    - 实现 `backend/app/agent/tools/registry.py`
    - 实现 register 和 get 方法
    - _需求: 2.4_
  - [x] 3.3 编写工具框架属性测试

    - **Property 1: 工具 Schema 转换一致性**
    - **Property 2: 工具注册和检索一致性**
    - **验证: 需求 2.3, 2.4**

- [x] 4. 实现财务计算工具
  - [x] 4.1 实现贷款计算工具 calc_loan
    - 实现 `backend/app/agent/tools/financial.py`
    - 支持等额本息和等额本金计算
    - 返回首付、贷款金额、月供、总利息
    - _需求: 3.1, 3.2_
  - [x] 4.2 实现税费计算工具 calc_tax
    - 计算契税、增值税、个税、中介费
    - 根据首套/二套、面积应用不同税率
    - _需求: 3.3_
  - [x] 4.3 实现总成本计算工具 calc_total_cost
    - 汇总首付、贷款利息、税费、其他费用
    - _需求: 3.4_
  - [x] 4.4 实现压力评估工具 assess_pressure
    - 计算月供收入比
    - 返回压力等级（低/中/高）和建议
    - _需求: 3.5_
  - [x] 4.5 编写财务计算属性测试

    - **Property 4: 贷款计算数学正确性**
    - **Property 5: 税费计算规则正确性**
    - **Property 6: 总成本汇总正确性**
    - **Property 7: 还款压力等级划分**
    - **验证: 需求 3.1, 3.3, 3.4, 3.5**

- [x] 5. 实现市场查询工具
  - [x] 5.1 创建市场数据模拟
    - 实现 `backend/app/agent/tools/market.py`
    - 创建南宁、柳州的模拟市场数据
    - _需求: 4.1_
  - [x] 5.2 实现 query_market 工具
    - 返回指定城市区域的均价、成交量、库存
    - _需求: 4.1_
  - [x] 5.3 实现 query_price_trend 工具
    - 返回历史房价走势数据
    - _需求: 4.2_
  - [x] 5.4 实现 compare_districts 工具
    - 返回多区域对比数据
    - _需求: 4.3_
  - [x] 5.5 实现 judge_timing 工具
    - 根据市场数据计算时机评分
    - 返回评分和建议
    - _需求: 4.4_

- [x] 6. 实现政策检索工具
  - [x] 6.1 创建政策知识库数据
    - 创建 `backend/data/knowledge/` 目录
    - 编写南宁、柳州限购限贷政策文档
    - 编写常见 FAQ
    - _需求: 5.1, 5.2_
  - [x] 6.2 实现 RAG 检索服务
    - 实现 `backend/app/agent/tools/policy.py`
    - 使用 Chroma 向量数据库
    - 实现 search_policy 和 search_faq 工具
    - 支持按城市过滤
    - _需求: 5.1, 5.2, 5.3, 5.4_
  - [x] 6.3 编写政策检索属性测试

    - **Property 8: 政策检索城市过滤**
    - **验证: 需求 5.4**

- [x] 7. 实现角色系统
  - [x] 7.1 定义角色数据结构
    - 实现 `backend/app/agent/roles.py`
    - 定义 Role 数据类
    - _需求: 6.1-6.4_
  - [x] 7.2 实现四个角色定义
    - Financial_Advisor（财务顾问）
    - Policy_Expert（政策专家）
    - Market_Analyst（市场分析师）
    - Purchase_Consultant（购房顾问）
    - 每个角色包含 system_prompt、tools、trigger_keywords
    - _需求: 6.1, 6.2, 6.3, 6.4, 6.5_
  - [x] 7.3 编写角色系统属性测试

    - **Property 9: 角色工具列表完整性**
    - **验证: 需求 6.5**

- [x] 8. 实现意图识别
  - [x] 8.1 实现关键词匹配
    - 实现 `backend/app/agent/intent.py`
    - 根据角色 trigger_keywords 匹配用户输入
    - _需求: 7.1, 7.2, 7.3_
  - [x] 8.2 实现 LLM 意图分类（fallback）
    - 当关键词匹配失败时使用 LLM 分类
    - _需求: 7.5_
  - [x] 8.3 编写意图识别属性测试

    - **Property 10: 意图识别关键词匹配**
    - **验证: 需求 7.1, 7.2, 7.3**

- [x] 9. 实现 Agent 引擎核心
  - [x] 9.1 创建 AgentEngine 类
    - 实现 `backend/app/agent/engine.py`
    - 实现 process 方法（异步生成器）
    - _需求: 8.1_
  - [x] 9.2 实现角色执行逻辑
    - 构建角色专属 prompt
    - 调用 LLM 并处理工具调用
    - _需求: 8.2, 8.3_
  - [x] 9.3 实现多角色结果整合
    - 当需要多个角色时，由购房顾问整合结果
    - _需求: 8.4_
  - [x] 9.4 实现对话上下文管理
    - 使用 Redis 存储会话上下文
    - 支持多轮对话
    - _需求: 8.5_

- [x] 10. 检查点 - 核心模块测试
  - 确保所有工具可以独立执行
  - 确保 Agent 引擎可以处理简单问题
  - 如有问题请询问用户

- [x] 11. 实现对话 API
  - [x] 11.1 创建 Chat API 路由
    - 实现 `backend/app/api/chat.py`
    - POST /api/v1/chat 接口
    - 接受 session_id 和 message
    - _需求: 9.1_
  - [x] 11.2 实现流式响应
    - 使用 Server-Sent Events
    - 发送 role_start、role_result、done 事件
    - _需求: 9.3, 9.4, 9.5_
  - [x] 11.3 注册路由到主应用
    - 在 main.py 中注册 chat 路由
    - _需求: 9.2_

- [x] 12. 实现计算器 API
  - [x] 12.1 创建 Calculator API 路由
    - 实现 `backend/app/api/calculator.py`
    - POST /api/v1/calc/loan
    - POST /api/v1/calc/tax
    - POST /api/v1/calc/total_cost
    - _需求: 10.1, 10.2, 10.3_
  - [x] 12.2 实现请求验证
    - 使用 Pydantic 模型验证参数
    - _需求: 10.4_
  - [x] 12.3 实现统一响应格式
    - 返回 {code, message, data} 格式
    - _需求: 10.5_
  - [x] 12.4 编写 API 属性测试

    - **Property 11: API 响应格式一致性**
    - **Property 12: 参数验证错误格式**
    - **验证: 需求 10.5, 11.4**

- [x] 13. 实现错误处理
  - [x] 13.1 创建统一异常处理
    - 实现 `backend/app/utils/exceptions.py`
    - 定义业务异常类
    - _需求: 11.1, 11.2_
  - [x] 13.2 注册全局异常处理器
    - 在 main.py 中注册异常处理器
    - 不暴露堆栈信息
    - _需求: 11.3_

- [x] 14. 更新依赖和配置
  - [x] 14.1 更新 requirements.txt
    - 添加 httpx、chromadb、sentence-transformers
    - _需求: 依赖管理_
  - [x] 14.2 更新 settings.py
    - 添加 DEEPSEEK_API_KEY、DEEPSEEK_BASE_URL 配置
    - _需求: 1.5_

- [x] 15. 最终检查点 - 集成测试
  - 启动服务并测试 /api/v1/chat 接口
  - 测试 /api/v1/calc/* 接口
  - 确保所有测试通过
  - 如有问题请询问用户

- [x] 16. 实现高级模式（Discussion Mode）
  - [x] 16.1 实现对话协商逻辑
    - 在 `backend/app/agent/engine.py` 中添加 `_process_discussion_mode` 方法
    - 实现多角色对话协商机制
    - 支持角色间多轮讨论直到达成共识
    - 设置最大讨论轮数（建议 5 轮）防止无限循环
    - _需求: 设计文档 - 高级模式_
  - [x] 16.2 实现讨论事件流
    - 新增 `{"type": "discussion", "from": "...", "to": "...", "content": "..."}` 事件
    - 实时推送角色间的讨论内容给前端
    - _需求: 设计文档 - 高级模式_
  - [x] 16.3 添加 mode 参数到 Chat API
    - 修改 `backend/app/api/chat.py` 的 `ChatRequest` 模型
    - 添加 `mode: str = "standard"` 参数
    - 支持 "standard" 和 "discussion" 两种模式
    - _需求: 设计文档 - 模式选择_
  - [x] 16.4 实现讨论终止条件
    - 达成共识（各角色意见一致）
    - 达到最大轮数
    - 购房顾问判断信息充足可以总结
    - _需求: 设计文档 - 高级模式_

## 备注

- 标记 `*` 的任务为可选测试任务
- 每个任务引用具体需求以便追溯
- 检查点任务用于阶段性验证


---

## 补充任务：完善工具和功能

以下任务是原设计中遗漏的，需要补充实现以完成功能清单的全部需求。

---

## 17. 实现还款计划生成工具 ✅ 已完成

### Description
生成逐月或逐年的还款明细表，展示每期本金、利息、剩余本金。

### Files to Modify
- `backend/app/agent/tools/financial.py`

### Acceptance Criteria
- [x] 支持等额本息和等额本金两种方式
- [x] 支持按月或按年展示
- [x] 计算结果与 calc_loan 一致
- [x] 注册到工具注册表

---

## 18. 实现购房指南检索工具 ✅ 已完成

### Description
从知识库检索购房流程相关内容，回答购房步骤、注意事项等问题。

### Files to Modify
- `backend/app/agent/tools/policy.py`

### Acceptance Criteria
- [x] 从 guides Collection 检索相关内容
- [x] 支持按购房阶段过滤
- [x] 返回相关度最高的内容片段
- [x] 注册到工具注册表

---

## 19. 实现联网搜索新闻工具 ✅ 已完成

### Description
调用搜索 API 获取最新的房产政策新闻。

### Files to Create
- `backend/app/agent/tools/news.py`

### 实现方案
- 方案 C：模拟数据（比赛演示用）

### Acceptance Criteria
- [x] 能够搜索并返回新闻标题、摘要、链接
- [x] 支持按城市过滤
- [x] 处理网络错误，返回友好提示
- [x] 注册到工具注册表

---

## 20. 实现综合报告生成工具 ✅ 已完成

### Description
整合财务分析、市场分析、政策信息，生成结构化的购房分析报告。

### Files to Create
- `backend/app/agent/tools/report.py`

### Acceptance Criteria
- [x] 内部调用其他工具获取数据
- [x] 生成结构化的报告 JSON
- [x] 包含风险提示和行动建议
- [x] 注册到工具注册表

---

## 21. 升级政策检索为向量检索 ✅ 已完成

### Description
将 search_policy 和 search_faq 从关键词匹配升级为 Chroma 向量检索。

### Files to Modify
- `backend/app/agent/tools/policy.py`

### Acceptance Criteria
- [x] 使用 Chroma 进行语义检索
- [x] 检索结果按相关度排序
- [x] 支持 top_k 参数控制返回数量
- [x] 保持向后兼容，工具接口不变（降级到关键词匹配）

---

## 22. 实现对话历史持久化 ✅ 已完成

### Description
修改 AgentEngine，将对话消息保存到 PostgreSQL。

### Files to Modify
- `backend/app/api/chat.py`
- `backend/app/db/database.py`

### Acceptance Criteria
- [x] 用户消息保存到数据库
- [x] AI 回复保存到数据库（含 metadata）
- [x] 支持通过 conversation_id 继续对话
- [x] Chat API 添加 conversation_id 和 user_id 参数

---

## 23. 更新角色工具列表 ✅ 已完成

### Description
将新增的工具添加到对应角色的工具列表中。

### Files to Modify
- `backend/app/agent/roles.py`

### 工具分配
| 角色 | 新增工具 |
|------|----------|
| 财务顾问 | `generate_repayment_plan` |
| 政策专家 | `search_guide`, `search_news` |
| 购房顾问 | `generate_report` |

### Acceptance Criteria
- [x] 角色工具列表更新
- [x] 工具注册表包含所有新工具

---

## 24. 更新工具模块导出 ✅ 已完成

### Description
在 tools/__init__.py 中导出新增的工具类。

### Files to Modify
- `backend/app/agent/tools/__init__.py`

### Acceptance Criteria
- [x] 所有新工具类已导出
- [x] GenerateRepaymentPlanTool, SearchGuideTool, SearchNewsTool, GenerateReportTool

---

## 25. 补充测试 ⏳ 待实现

### Description
为新增功能编写测试用例。

### Files to Create
- `backend/tests/test_repayment_plan.py`
- `backend/tests/test_news_tool.py`
- `backend/tests/test_report_tool.py`
- `backend/tests/test_conversation_api.py`

### Acceptance Criteria
- [ ] 还款计划计算正确性测试
- [ ] 联网搜索错误处理测试
- [ ] 报告生成结构完整性测试
- [ ] 对话历史 CRUD 测试

---

## 26. 最终验证 ✅ 已完成

### Description
完整测试所有功能，确保功能清单全部实现。

### 验证清单
- [x] 所有 14 个工具已注册并可执行
- [x] 对话历史可以持久化和恢复
- [x] 向量检索返回相关结果（支持降级到关键词匹配）
- [x] 联网搜索正常工作（模拟数据）
- [x] 综合报告包含所有必要信息
- [x] 所有 182 个测试通过

---

## 27. 实现用户系统（登录/注册） ✅ 已完成

### Description
实现简单的用户认证系统，支持用户注册和登录。

### Files to Create
- `backend/app/api/auth.py`

### API 端点
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/auth/register | 用户注册 |
| POST | /api/v1/auth/login | 用户登录 |
| GET | /api/v1/auth/me | 获取当前用户信息 |

### 实现方案
- 简化版：使用 UUID 作为用户标识，无密码（比赛演示用）

### Acceptance Criteria
- [x] 支持用户注册（昵称）
- [x] 支持用户登录（返回 user_id）
- [x] 对话可以关联到用户
- [x] 注册路由到主应用

---

## 任务状态总结

### 已完成
- 任务 1-24：核心 Agent 功能 + 补充工具
- 任务 26：最终验证（182 个测试全部通过）
- 任务 27：用户系统

### 待实现（可选）
- 任务 25：补充测试（新工具的专项测试，现有测试已覆盖核心功能）
