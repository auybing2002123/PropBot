# Implementation Tasks

## Task 1: 创建项目目录结构

### Description
在 WSL 中创建 FastAPI 项目的基础目录结构和必要文件。

### Files to Create
- `~/projects/house-advisor/backend/app/__init__.py`
- `~/projects/house-advisor/backend/app/config/__init__.py`
- `~/projects/house-advisor/backend/app/api/__init__.py`
- `~/projects/house-advisor/backend/app/db/__init__.py`
- `~/projects/house-advisor/backend/app/utils/__init__.py`
- `~/projects/house-advisor/backend/tests/__init__.py`
- `~/projects/house-advisor/backend/.gitignore`

### Acceptance Criteria
- [x] 目录结构符合 design.md 定义
- [x] 所有 `__init__.py` 文件已创建
- [x] `.gitignore` 包含 `.env`、`__pycache__`、`.pytest_cache`

---

## Task 2: 创建 Docker Compose 配置

### Description
创建 docker-compose.yml 定义 PostgreSQL、Redis、Chroma 服务。

### Files to Create
- `~/projects/house-advisor/docker-compose.yml`

### Acceptance Criteria
- [x] PostgreSQL 15 配置正确，端口 5433:5432
- [x] Redis 7 配置正确，端口 6380:6379
- [x] Chroma 配置正确，端口 8001:8000
- [x] 数据持久化卷已配置
- [x] 健康检查已配置

---

## Task 3: 创建环境变量配置

### Description
创建 .env.example 模板和 requirements.txt 依赖文件。

### Files to Create
- `~/projects/house-advisor/backend/.env.example`
- `~/projects/house-advisor/backend/requirements.txt`

### Acceptance Criteria
- [x] .env.example 包含所有必需配置项
- [x] requirements.txt 包含所有依赖及版本号

---

## Task 4: 实现配置管理模块

### Description
使用 Pydantic Settings 实现配置加载和验证。

### Files to Create
- `~/projects/house-advisor/backend/app/config/settings.py`

### Acceptance Criteria
- [x] 从 .env 文件加载环境变量
- [x] 使用 Pydantic 验证配置
- [x] 缺失必需配置时抛出明确错误
- [x] 使用 lru_cache 缓存配置实例

---

## Task 5: 实现日志配置模块

### Description
配置 Python logging 模块，支持不同日志级别。

### Files to Create
- `backend/app/utils/logger.py`

### Acceptance Criteria
- [x] 日志格式：时间 | 级别 | 模块名 | 消息
- [x] 支持 DEBUG、INFO、WARNING、ERROR 级别
- [x] 开发环境默认 DEBUG 级别

---

## Task 6: 实现数据库连接模块

### Description
实现 PostgreSQL 和 Redis 的异步连接管理。

### Files to Create
- `backend/app/db/database.py`

### Acceptance Criteria
- [x] SQLAlchemy 异步引擎连接 PostgreSQL
- [x] redis-py 异步客户端连接 Redis
- [x] 提供连接和断开方法
- [x] 提供健康检查方法

---

## Task 7: 实现健康检查接口

### Description
创建 /api/v1/health 接口，检查各服务状态。

### Files to Create
- `backend/app/api/health.py`

### Acceptance Criteria
- [x] GET /api/v1/health 返回服务状态
- [x] 检查 PostgreSQL 连接状态
- [x] 检查 Redis 连接状态
- [x] 返回格式符合统一响应规范

---

## Task 8: 实现 FastAPI 主入口

### Description
创建 FastAPI 应用实例，配置 CORS、路由、生命周期。

### Files to Create
- `backend/app/main.py`

### Acceptance Criteria
- [x] FastAPI 应用正确初始化
- [x] CORS 允许前端跨域访问
- [x] API 路由前缀为 /api/v1/
- [x] 启动时连接数据库，关闭时断开连接

---

## Task 9: 启动 Docker 服务并验证

### Description
启动 Docker 数据库服务，验证连接正常。

### Commands
```bash
# 在 WSL 中执行
cd ~/projects/house-advisor
docker-compose up -d
docker-compose ps
```

### Acceptance Criteria
- [x] PostgreSQL 容器运行正常
- [x] Redis 容器运行正常
- [x] Chroma 容器运行正常

---

## Task 10: 安装依赖并启动后端服务

### Description
安装 Python 依赖，创建 .env 文件，启动 FastAPI 服务。

### Commands
```bash
# 在 WSL 中执行
cd ~/projects/house-advisor/backend
conda activate house-advisor
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

### Acceptance Criteria
- [x] 依赖安装成功
- [x] 服务在 8080 端口启动
- [x] 无启动错误

---

## Task 11: 验证健康检查接口

### Description
调用健康检查接口，验证返回结果正确。

### Test
```bash
curl http://localhost:8080/api/v1/health
```

### Expected Response
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "status": "healthy",
    "services": {
      "postgres": "healthy",
      "redis": "healthy"
    }
  }
}
```

### Acceptance Criteria
- [x] 接口返回 200 状态码
- [x] 返回格式符合预期
- [x] PostgreSQL 和 Redis 状态均为 healthy


---

## 补充任务：数据库持久化

以下任务是原设计中遗漏的，需要补充实现。

---

## Task 12: 设计数据库表结构

### Description
设计用户、对话、消息等核心业务表，使用 SQLAlchemy ORM 模型。

### Files to Create
- `backend/app/models/user.py`
- `backend/app/models/conversation.py`
- `backend/app/models/message.py`
- `backend/app/models/base.py`

### 表结构设计

```sql
-- 用户表（简化版，比赛可选）
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nickname VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 对话会话表
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    title VARCHAR(200),  -- 对话标题（取首条消息摘要）
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 消息表
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,  -- 'user' | 'assistant' | 'system'
    content TEXT NOT NULL,
    metadata JSONB,  -- 存储工具调用结果、角色信息等
    created_at TIMESTAMP DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
```

### Acceptance Criteria
- [x] SQLAlchemy ORM 模型定义完成
- [x] 模型包含必要的关系定义
- [x] 支持 UUID 主键
- [x] metadata 字段使用 JSONB 类型

---

## Task 13: 配置 Alembic 数据库迁移

### Description
使用 Alembic 管理数据库表结构版本，支持迁移和回滚。

### Files to Create
- `backend/alembic.ini`
- `backend/alembic/env.py`
- `backend/alembic/versions/001_initial_tables.py`

### Commands
```bash
# 初始化 Alembic
cd backend
alembic init alembic

# 生成迁移脚本
alembic revision --autogenerate -m "initial tables"

# 执行迁移
alembic upgrade head
```

### Acceptance Criteria
- [x] Alembic 配置正确读取 DATABASE_URL
- [x] 迁移脚本可以创建所有表
- [x] 支持 `alembic upgrade` 和 `alembic downgrade`

---

## Task 14: 实现对话历史 CRUD 服务

### Description
实现对话和消息的增删改查服务层。

### Files to Create
- `backend/app/services/__init__.py`
- `backend/app/services/conversation.py`

### API 设计
```python
class ConversationService:
    async def create_conversation(user_id: str | None) -> Conversation
    async def get_conversation(conversation_id: str) -> Conversation | None
    async def list_conversations(user_id: str | None, limit: int = 20) -> list[Conversation]
    async def delete_conversation(conversation_id: str) -> bool
    
    async def add_message(conversation_id: str, role: str, content: str, metadata: dict = None) -> Message
    async def get_messages(conversation_id: str, limit: int = 50) -> list[Message]
```

### Acceptance Criteria
- [x] 支持创建、查询、删除对话
- [x] 支持添加、查询消息
- [x] 使用异步数据库操作
- [x] 正确处理事务

---

## Task 15: 实现对话历史 API

### Description
创建对话历史相关的 REST API 接口。

### Files to Create
- `backend/app/api/conversation.py`

### API 端点
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/conversations | 获取对话列表 |
| POST | /api/v1/conversations | 创建新对话 |
| GET | /api/v1/conversations/{id} | 获取对话详情（含消息） |
| DELETE | /api/v1/conversations/{id} | 删除对话 |

### Acceptance Criteria
- [x] API 返回格式符合统一规范
- [x] 支持分页查询
- [x] 删除对话时级联删除消息

---

## Task 16: 初始化 Chroma 向量数据库

### Description
配置 Chroma 客户端，创建知识库 Collection，导入政策文档。

### Files to Create
- `backend/app/db/chroma.py`
- `backend/scripts/init_knowledge_base.py`

### Collection 设计
| Collection | 说明 | 文档来源 |
|------------|------|----------|
| policies | 限购限贷政策 | `data/knowledge/policies/*.md` |
| faq | 常见问题 | `data/knowledge/faq/*.json` |
| guides | 购房指南 | `data/knowledge/guides/*.md` |

### Acceptance Criteria
- [x] Chroma 客户端连接配置正确
- [x] 创建三个 Collection
- [x] 使用 sentence-transformers 生成向量（Chroma 内置）
- [x] 文档分块大小合理（约 500 字符）
- [x] 支持按城市过滤的 metadata

---

## Task 17: 验证数据库和向量库

### Description
启动服务，验证数据库表和向量库初始化正确。

### Commands
```bash
# 执行数据库迁移
cd backend
alembic upgrade head

# 初始化知识库向量
python scripts/init_knowledge_base.py

# 验证
psql -h localhost -p 5434 -U house_advisor -d house_advisor -c "\dt"
```

### Acceptance Criteria
- [x] PostgreSQL 表创建成功
- [x] Chroma Collection 创建成功（policies: 7, faq: 15, guides: 5）
- [x] 知识库文档已导入向量库（共 27 个文档）
- [x] 健康检查接口返回所有服务 healthy

---

## ✅ backend-infrastructure Spec 完成

所有任务已完成验证：
- Docker 服务运行正常（PostgreSQL、Redis、Chroma）
- 数据库迁移成功执行
- 知识库初始化完成（27 个文档）
- 健康检查接口返回正常

---

## 更新 requirements.txt

需要添加的依赖：
```
alembic>=1.13.0
asyncpg>=0.29.0  # 已有
chromadb>=0.4.0  # 已有
sentence-transformers>=2.2.0  # 已有
```
