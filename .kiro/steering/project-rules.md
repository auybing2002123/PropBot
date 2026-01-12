# 购房决策智能助手 - 项目规范

## 通用规则
- 不要说"完成了"然后不验证，先验证，验证通过后再说完成
- 如果验证失败，自己修复后再次验证
- 禁止硬编码敏感信息：数据库连接字符串、API 密钥、JWT 密钥、第三方服务凭证
- 修改代码文件时，判断是否需要同步更新相关文档（如 API 变更需更新功能清单）
- **禁止下载任何文件到 C 盘**：模型、数据集、依赖包等大文件下载前必须先向用户确认存放路径

## 错误处理规范
- 后端统一异常处理，返回格式：`{"code": 错误码, "message": "用户友好提示", "data": null}`
- 不暴露堆栈信息和敏感错误细节给前端
- 前端统一错误提示，使用 Element Plus 的 Message 组件

## 日志规范
- 使用 Python logging 模块
- 开发环境：DEBUG 级别，打印详细日志
- 生产环境：INFO 级别
- 关键操作必须记录日志：用户提问、AI 响应、API 调用、错误信息

## 安全规范
- API 接口做基本的参数校验（使用 Pydantic）
- 用户输入做 XSS 防护
- SQL 使用参数化查询，防止注入

## 项目概述
- 项目名称：购房决策智能助手
- 项目类型：比赛项目
- 目标城市：南宁、柳州（广西）

## 开发环境

### 项目根目录
- Windows 路径：`E:\code\PropBot\`
- WSL 路径：`/mnt/e/code/PropBot/`

### 前端
- 位置：`frontend/`（项目根目录下）
- 技术栈：Vue3 + Element Plus + ECharts
- Node 版本：18+（使用 nvm 管理）
- 包管理：npm
- 运行环境：Windows

### 后端
- 位置：`backend/`（项目根目录下）
- 技术栈：FastAPI + 手搓 Agent + DeepSeek API
- Python 版本：3.11
- 虚拟环境：conda `house-advisor`
- 运行环境：WSL Ubuntu-24.04
- 激活命令：`conda activate house-advisor`

### 数据库服务（WSL Docker）
- PostgreSQL：用户数据、对话历史
- Redis：会话缓存、限流
- Chroma：向量数据库（知识库）

## 架构说明
- 对外宣传：**多智能体协作系统**
- 内部实现：**伪多Agent**（单Agent + 多角色 + 多工具）
- 4个角色：财务顾问、政策专家、市场分析师、购房顾问

## 数据说明
- 使用**模拟数据**，不调用真实 API
- 政策新闻：知识库（静态）+ 联网工具（动态）

## UI 规范
- 组件库：Element Plus
- 图表：ECharts
- 不使用：渐变色、emoji（用 Element Plus Icons）

## 文档位置
- `docs/需求文档.md` - 产品需求
- `docs/数据需求文档.md` - 数据结构定义
- `docs/功能清单.md` - 功能和工具列表
- `docs/架构设计文档.md` - 伪多Agent架构
- `docs/技术实现方案.md` - 技术栈和实现细节
- `docs/UI设计文档.md` - 页面设计和视觉规范

## 代码规范
- Python：遵循 PEP8，用中文注释
- Vue：组合式 API（setup），中文注释
- 变量命名：英文，注释用中文（方便比赛展示）

## Git 规范
- commit 信息用中文（方便评委查看）
- 分支策略：main 主分支，feature/* 功能开发

### Commit Message 格式
```
type: 中文描述
```

### Type 类型
| Type | 说明 |
|------|------|
| `feat` | 新功能 |
| `fix` | 修复 bug |
| `docs` | 文档更新 |
| `style` | 代码格式（不影响功能） |
| `refactor` | 重构 |
| `test` | 测试相关 |
| `chore` | 构建/工具 |

### 示例
```
feat: 添加用户登录接口
fix: 修复贷款计算精度问题
docs: 更新 API 文档
```

## API 规范
- 接口前缀：`/api/v1/`
- 返回格式：`{"code": 0, "message": "success", "data": {}}`
- 错误码：0 成功，非 0 失败

## 端口约定
| 服务 | 端口 | 说明 |
|------|------|------|
| 前端开发 | 5173 | Vite 默认 |
| 后端 API | 8080 | FastAPI |
| PostgreSQL | 5434 | 避开系统 5432/5433 |
| Redis | 6380 | 避开系统 6379 |
| Chroma | 8001 | 避开可能的冲突 |

## 环境变量
- 敏感信息放 `.env` 文件，不提交 Git
- 必需变量：
  - `DEEPSEEK_API_KEY` - DeepSeek API 密钥
  - `DATABASE_URL=postgresql://house_advisor:house_advisor_pwd@localhost:5434/house_advisor`
  - `REDIS_URL=redis://localhost:6380/0`
  - `CHROMA_URL=http://localhost:8001`
  - `EMBEDDING_MODEL_PATH=~/models/bge-base-zh-v1.5` - 本地 BGE embedding 模型路径

## 本地模型配置
- 模型统一存放目录：`~/models/`
- 可用模型：
  - `bge-base-zh-v1.5` - 中文 embedding 模型（推荐，用于知识库检索）
  - `bge-large-zh-v1.5` - 大型中文 embedding 模型（效果更好，但更慢）
  - `bge-reranker-base` - 重排序模型（可选）
- Chroma 向量数据库使用本地 BGE 模型，避免下载

## Docker 规则
- 开发阶段：**只用 Docker 跑数据库**（方案 A）
- 后端代码用 conda 环境本地运行，方便调试
- docker-compose.yml 位置：项目根目录 `docker-compose.yml`
- **使用 `docker compose`（不带横杠）命令**，`docker-compose` 已弃用

```yaml
# 数据库服务（独立端口，避免与系统服务冲突）
services:
  postgres:
    image: postgres:15
    ports: ["5434:5432"]
    environment:
      POSTGRES_USER: house_advisor
      POSTGRES_PASSWORD: house_advisor_pwd
      POSTGRES_DB: house_advisor
  redis:
    image: redis:7
    ports: ["6380:6379"]
  chroma:
    image: chromadb/chroma
    ports: ["8001:8000"]
```

## 测试规则
- 比赛项目，**要求完整测试覆盖**
- 重点测试：核心计算逻辑（贷款、税费）

### 测试账号
- 用户名：`demo`
- 密码：`demo123`

### 测试工具
| 测试类型 | 工具 | 说明 |
|---------|------|------|
| 后端 API | HTTP MCP | `mcp_http_http_get/post` 直接调用接口 |
| 前端 UI | Playwright MCP | `mcp_playwright_*` 浏览器自动化 |
| 单元测试 | pytest | 核心计算逻辑 |

## Spec 开发计划

按以下顺序创建和执行 Spec：

| 顺序 | Spec 名称 | 内容 | 依赖 |
|------|----------|------|------|
| 1 | backend-infrastructure | FastAPI 项目结构、Docker 数据库、基础配置 | 无 |
| 2 | agent-core | 多角色 Agent、工具调用（含计算器）、对话 API | Spec 1 |
| 3 | frontend | Vue3 项目、5 个页面、对话交互 | Spec 1, 2 |

说明：
- 计算器功能作为 Agent 工具实现，不单独建 Spec
- 每个 Spec 完成后再开始下一个

## WSL 操作命令
```bash
# 进入项目目录并激活环境
wsl -d Ubuntu-24.04 -- bash -c "cd /mnt/e/code/PropBot && source ~/anaconda3/etc/profile.d/conda.sh && conda activate house-advisor && <命令>"

# 简化版（如果 conda 已初始化）
wsl -d Ubuntu-24.04 -- bash -lc "cd /mnt/e/code/PropBot && conda activate house-advisor && <命令>"

# 启动 Docker 服务（使用 docker compose，不带横杠）
wsl -d Ubuntu-24.04 -- bash -c "docker compose -f /mnt/e/code/PropBot/docker-compose.yml up -d"

# 查看 Docker 服务状态
wsl -d Ubuntu-24.04 -- docker compose -f /mnt/e/code/PropBot/docker-compose.yml ps

# 数据库迁移
wsl -d Ubuntu-24.04 -- bash -c "cd /mnt/e/code/PropBot/backend && source ~/anaconda3/etc/profile.d/conda.sh && conda activate house-advisor && alembic upgrade head"

# 初始化知识库
wsl -d Ubuntu-24.04 -- bash -c "cd /mnt/e/code/PropBot/backend && source ~/anaconda3/etc/profile.d/conda.sh && conda activate house-advisor && python scripts/init_knowledge_base.py"
```
