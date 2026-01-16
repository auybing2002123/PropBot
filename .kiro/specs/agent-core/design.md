# 设计文档

## 概述

本设计文档描述购房决策智能助手的核心 Agent 系统实现方案。采用"伪多 Agent"架构，本质是单 Agent + 多角色 + 多工具，对外表现为多智能体协作。

## 架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户输入                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Chat API                                   │
│                    POST /api/v1/chat                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Agent Engine                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Intent Recognizer                           │   │
│  │         关键词匹配 → LLM 分类（fallback）                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│         ┌────────────────────┼────────────────────┐            │
│         ▼                    ▼                    ▼            │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐      │
│  │ 财务顾问     │     │ 政策专家     │     │ 市场分析师   │      │
│  │ calc_loan   │     │search_policy│     │query_market │      │
│  │ calc_tax    │     │ search_faq  │     │query_trend  │      │
│  │assess_press │     │             │     │compare_dist │      │
│  └─────────────┘     └─────────────┘     └─────────────┘      │
│         │                    │                    │            │
│         └────────────────────┼────────────────────┘            │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    购房顾问                               │   │
│  │              整合各角色结果，生成综合建议                   │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LLM Client                                  │
│                   DeepSeek API 调用                              │
└─────────────────────────────────────────────────────────────────┘
```

## 组件和接口

### 目录结构

```
backend/app/
├── agent/
│   ├── __init__.py
│   ├── engine.py           # Agent 引擎核心
│   ├── roles.py            # 角色定义
│   ├── intent.py           # 意图识别
│   └── tools/
│       ├── __init__.py
│       ├── base.py         # 工具基类
│       ├── registry.py     # 工具注册表
│       ├── financial.py    # 财务计算工具
│       ├── market.py       # 市场查询工具
│       └── policy.py       # 政策检索工具
├── llm/
│   ├── __init__.py
│   └── client.py           # LLM 客户端
├── api/
│   ├── chat.py             # 对话 API
│   └── calculator.py       # 计算器 API
└── models/
    └── schemas.py          # Pydantic 模型
```

### LLM Client 接口

```python
class DeepSeekClient:
    """DeepSeek API 客户端"""
    
    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        temperature: float = 0.7
    ) -> dict:
        """
        调用 DeepSeek 对话接口
        
        Args:
            messages: 对话消息列表
            tools: 可用工具列表（OpenAI 格式）
            temperature: 温度参数
            
        Returns:
            API 响应字典
        """
        pass
```

### Tool Base 接口

```python
class BaseTool(ABC):
    """工具基类"""
    name: str
    description: str
    parameters: list[ToolParameter]
    
    @abstractmethod
    async def execute(self, **kwargs) -> dict:
        """执行工具"""
        pass
    
    def to_openai_schema(self) -> dict:
        """转换为 OpenAI 函数调用格式"""
        pass
```

### Role 接口

```python
@dataclass
class Role:
    """角色定义"""
    id: str                    # 角色ID
    name: str                  # 显示名称
    icon: str                  # 图标
    system_prompt: str         # 系统提示词
    tools: list[str]           # 可用工具名称列表
    trigger_keywords: list[str] # 触发关键词
```

### Agent Engine 接口

```python
class AgentEngine:
    """伪多 Agent 引擎"""
    
    async def process(
        self,
        user_input: str,
        context: dict,
        mode: str = "standard"  # "standard" 或 "discussion"
    ) -> AsyncGenerator[dict, None]:
        """
        处理用户输入，流式返回结果
        
        Args:
            user_input: 用户输入
            context: 对话上下文
            mode: 执行模式
                - "standard": 标准模式（LLM规划+串行执行）
                - "discussion": 高级模式（对话协商）
        
        Yields:
            {"type": "role_start", "role": "...", "name": "...", "icon": "..."}
            {"type": "role_result", "role": "...", "content": "..."}
            {"type": "discussion", "from": "...", "to": "...", "content": "..."}  # 高级模式
            {"type": "done"}
        """
        pass
```

### 意图识别与执行计划接口

```python
@dataclass
class ExecutionPlan:
    """执行计划"""
    roles: list[Role]                    # 角色列表（已按执行顺序排列）
    execution_mode: str                  # "sequential" 或 "parallel"
    reason: str                          # 规划理由

class IntentRecognizer:
    """意图识别器"""
    
    def match_keywords(self, user_input: str) -> list[Role]:
        """关键词匹配"""
        pass
    
    async def classify_with_llm(self, user_input: str) -> list[Role]:
        """LLM 意图分类（fallback）"""
        pass
    
    async def plan_execution(self, user_input: str) -> ExecutionPlan:
        """规划执行计划，决定角色执行顺序和模式"""
        pass
```

## 多角色协作模式

### 标准模式（Standard Mode）

采用 **LLM 动态规划 + 串行执行 + 上下文传递** 的方案：

```
用户输入
    ↓
┌─────────────────────────────────────────────────────────┐
│ 1. 意图识别：关键词匹配 → LLM 分类（fallback）            │
│    → 候选角色列表                                        │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ 2. 执行规划：LLM 分析依赖关系                            │
│    → ExecutionPlan {roles, mode, reason}               │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ 3. 串行执行：按规划顺序执行，传递上下文                    │
│    角色1 → 结果1 → 角色2(+结果1) → 结果2 → ...          │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ 4. 结果整合：购房顾问汇总各专家意见                       │
└─────────────────────────────────────────────────────────┘
```

**优点**：快速、可控、成本低
**适用**：大部分购房咨询问题

### 高级模式（Discussion Mode）- 对话协商

采用 **多角色对话协商** 的方案，类似 AutoGen：

```
用户输入
    ↓
┌─────────────────────────────────────────────────────────┐
│ 1. 意图识别：确定参与讨论的角色                           │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ 2. 多轮对话协商                                          │
│    政策专家: "南宁不限购，首套首付20%起"                  │
│    财务顾问: "200万首付40万，月供8000，压力大"            │
│    市场分析师: "建议看江南区，150万左右"                  │
│    财务顾问: "150万的话月供降到6000，压力中等"            │
│    ... (多轮讨论直到达成共识)                            │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ 3. 购房顾问总结讨论结果，输出最终建议                     │
└─────────────────────────────────────────────────────────┘
```

**优点**：更深入的分析、可发现更优方案、展示"专家讨论"过程
**缺点**：延迟高、API 成本高（3-5倍）
**适用**：复杂的综合性购房决策问题

### 模式选择

用户可通过 API 参数选择模式：

```python
# POST /api/v1/chat
class ChatRequest(BaseModel):
    session_id: str
    message: str
    mode: str = "standard"  # "standard" 或 "discussion"
```

前端可提供切换开关，让用户选择是否启用"深度分析"模式。

### Chat API 接口

```python
# POST /api/v1/chat
class ChatRequest(BaseModel):
    session_id: str
    message: str

# 响应：Server-Sent Events 流
# data: {"type": "role_start", "role": "financial_advisor", "name": "财务顾问", "icon": "💰"}
# data: {"type": "role_result", "role": "financial_advisor", "content": "..."}
# data: {"type": "done"}
```

### Calculator API 接口

```python
# POST /api/v1/calc/loan
class LoanCalcRequest(BaseModel):
    price: float              # 房价（元）
    down_payment_ratio: float # 首付比例
    years: int                # 贷款年限
    rate: float               # 年利率（%）
    method: str = "equal_payment"  # 还款方式

class LoanCalcResponse(BaseModel):
    down_payment: float       # 首付金额
    loan_amount: float        # 贷款金额
    monthly_payment: float    # 月供
    total_payment: float      # 还款总额
    total_interest: float     # 总利息

# POST /api/v1/calc/tax
class TaxCalcRequest(BaseModel):
    price: float              # 房价
    area: float               # 面积（㎡）
    is_first_home: bool       # 是否首套
    house_age_years: int      # 房龄（年）

class TaxCalcResponse(BaseModel):
    deed_tax: float           # 契税
    vat: float                # 增值税
    income_tax: float         # 个税
    agent_fee: float          # 中介费
    total: float              # 税费总计
```

## 数据模型

### 工具参数模型

```python
class ToolParameter(BaseModel):
    name: str
    type: str  # "string", "number", "integer", "boolean"
    description: str
    required: bool = True
    enum: list[str] | None = None
```

### 对话上下文模型

```python
class ConversationContext(BaseModel):
    session_id: str
    history: list[dict]  # 历史消息
    user_info: dict | None = None  # 用户信息（预算、收入等）
```

### 统一响应模型

```python
class APIResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Any = None
```



## 正确性属性

正确性属性是系统应该满足的通用规则，用于验证实现的正确性。每个属性都是一个"对于所有..."的陈述。

### Property 1: 工具 Schema 转换一致性

*对于任意* 工具定义，调用 `to_openai_schema()` 方法应返回符合 OpenAI 函数调用格式的字典，包含 type、function.name、function.description、function.parameters 字段。

**验证: 需求 2.3**

### Property 2: 工具注册和检索一致性

*对于任意* 工具，注册到 Tool_Registry 后，通过相同名称检索应返回相同的工具实例。

**验证: 需求 2.4**

### Property 3: 工具参数验证

*对于任意* 工具和无效参数（缺少必需字段或类型错误），执行时应抛出验证错误而非执行失败。

**验证: 需求 2.5**

### Property 4: 贷款计算数学正确性

*对于任意* 有效的贷款参数（房价、首付比例、年限、利率），等额本息月供计算应满足公式：
`月供 = 贷款金额 × 月利率 × (1+月利率)^月数 / ((1+月利率)^月数 - 1)`

**验证: 需求 3.1**

### Property 5: 税费计算规则正确性

*对于任意* 有效的房产参数，契税计算应满足：
- 首套且面积≤90㎡：房价 × 1%
- 首套且面积>90㎡：房价 × 1.5%
- 二套且面积≤90㎡：房价 × 1%
- 二套且面积>90㎡：房价 × 2%

**验证: 需求 3.3**

### Property 6: 总成本汇总正确性

*对于任意* 购房成本组成（首付、贷款利息、税费、其他费用），总成本应等于各项之和。

**验证: 需求 3.4**

### Property 7: 还款压力等级划分

*对于任意* 月供和收入，压力等级应满足：
- 月供/收入 ≤ 30%：低压力
- 30% < 月供/收入 ≤ 50%：中压力
- 月供/收入 > 50%：高压力

**验证: 需求 3.5**

### Property 8: 政策检索城市过滤

*对于任意* 带城市参数的政策检索，返回结果中所有文档的城市字段应与查询城市匹配。

**验证: 需求 5.4**

### Property 9: 角色工具列表完整性

*对于任意* 已定义角色，加载后的 tools 列表应非空且所有工具名称都在 Tool_Registry 中注册。

**验证: 需求 6.5**

### Property 10: 意图识别关键词匹配

*对于任意* 包含角色触发关键词的用户输入，Intent_Recognizer 应返回包含该角色的列表。

**验证: 需求 7.1, 7.2, 7.3**

### Property 11: API 响应格式一致性

*对于任意* Calculator_API 调用（成功或失败），响应应包含 code、message、data 三个字段。

**验证: 需求 10.5**

### Property 12: 参数验证错误格式

*对于任意* 缺少必需参数的 API 请求，响应应包含非零 code 和说明缺失字段的 message。

**验证: 需求 11.4**

## 错误处理

### LLM API 错误

| 错误类型 | 错误码 | 用户提示 |
|---------|--------|---------|
| API 超时 | 1001 | 服务响应超时，请稍后重试 |
| API 密钥无效 | 1002 | 服务配置错误，请联系管理员 |
| 请求频率限制 | 1003 | 请求过于频繁，请稍后重试 |
| 未知错误 | 1099 | 服务暂时不可用，请稍后重试 |

### 工具执行错误

| 错误类型 | 错误码 | 用户提示 |
|---------|--------|---------|
| 参数验证失败 | 2001 | 输入参数有误：{字段名} |
| 数据查询失败 | 2002 | 数据查询失败，请稍后重试 |
| 计算错误 | 2003 | 计算过程出错，请检查输入 |

### 通用错误

| 错误类型 | 错误码 | 用户提示 |
|---------|--------|---------|
| 请求参数缺失 | 3001 | 缺少必需参数：{字段名} |
| 请求参数类型错误 | 3002 | 参数类型错误：{字段名} |

## 测试策略

### 单元测试

- 财务计算工具：测试各种边界条件（零利率、最大年限等）
- 税费计算工具：测试不同房产类型和面积组合
- 意图识别：测试关键词匹配和边界情况

### 属性测试

使用 pytest + hypothesis 进行属性测试：

- 贷款计算数学正确性（Property 4）
- 税费计算规则正确性（Property 5）
- 总成本汇总正确性（Property 6）
- 压力等级划分（Property 7）
- 意图识别关键词匹配（Property 10）

### 集成测试

- Chat API 端到端测试
- Calculator API 端到端测试
- Agent Engine 多角色协作测试
