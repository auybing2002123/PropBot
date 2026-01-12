# Requirements Document

## Introduction

后端基础架构搭建，包括 FastAPI 项目结构、Docker 数据库服务、基础配置和健康检查接口。这是整个项目的基础，后续的 Agent 核心和前端都依赖此基础架构。

## Glossary

- **Backend**: FastAPI 后端服务，运行在 WSL Ubuntu-24.04 环境
- **Docker_Services**: 通过 Docker Compose 运行的数据库服务（PostgreSQL、Redis、Chroma）
- **Health_Check**: 健康检查接口，用于验证服务是否正常运行
- **Config_Manager**: 配置管理模块，从环境变量加载配置

## Requirements

### Requirement 1: 项目目录结构

**User Story:** 作为开发者，我希望有规范的项目目录结构，以便代码组织清晰、易于维护。

#### Acceptance Criteria

1. THE Backend SHALL 在 WSL `~/projects/house-advisor/backend/` 目录下创建项目
2. THE Backend SHALL 包含以下目录结构：app/、tests/、config/
3. THE Backend SHALL 包含 requirements.txt 定义 Python 依赖
4. THE Backend SHALL 包含 .env.example 作为环境变量模板

### Requirement 2: FastAPI 应用初始化

**User Story:** 作为开发者，我希望 FastAPI 应用正确初始化，以便可以启动 Web 服务。

#### Acceptance Criteria

1. THE Backend SHALL 创建 FastAPI 应用实例，配置 CORS 允许前端跨域访问
2. THE Backend SHALL 配置 API 路由前缀为 `/api/v1/`
3. WHEN 应用启动时, THE Backend SHALL 加载环境变量配置
4. THE Backend SHALL 在 8080 端口启动服务

### Requirement 3: Docker 数据库服务

**User Story:** 作为开发者，我希望通过 Docker 启动数据库服务，以便开发环境一致且易于管理。

#### Acceptance Criteria

1. THE Docker_Services SHALL 通过 docker-compose.yml 定义服务
2. THE Docker_Services SHALL 包含 PostgreSQL 15，端口映射 5433:5432
3. THE Docker_Services SHALL 包含 Redis 7，端口映射 6380:6379
4. THE Docker_Services SHALL 包含 Chroma，端口映射 8001:8000
5. THE Docker_Services SHALL 配置数据持久化卷，防止数据丢失

### Requirement 4: 配置管理

**User Story:** 作为开发者，我希望有统一的配置管理，以便敏感信息不硬编码、环境切换方便。

#### Acceptance Criteria

1. THE Config_Manager SHALL 从 .env 文件加载环境变量
2. THE Config_Manager SHALL 使用 Pydantic Settings 进行配置验证
3. THE Config_Manager SHALL 支持以下配置项：DATABASE_URL、REDIS_URL、CHROMA_URL、DEEPSEEK_API_KEY
4. IF 必需配置项缺失, THEN THE Config_Manager SHALL 在启动时抛出明确错误

### Requirement 5: 健康检查接口

**User Story:** 作为运维人员，我希望有健康检查接口，以便可以监控服务状态。

#### Acceptance Criteria

1. WHEN 访问 GET `/api/v1/health`, THE Backend SHALL 返回服务状态
2. THE Health_Check SHALL 检查 PostgreSQL 连接状态
3. THE Health_Check SHALL 检查 Redis 连接状态
4. THE Health_Check SHALL 返回格式：`{"code": 0, "message": "success", "data": {"status": "healthy", "services": {...}}}`
5. IF 任一服务不可用, THEN THE Health_Check SHALL 返回 `{"code": 500, "message": "服务异常", "data": {"status": "unhealthy", "services": {...}}}`

### Requirement 6: 数据库连接

**User Story:** 作为开发者，我希望有数据库连接池管理，以便数据库操作高效可靠。

#### Acceptance Criteria

1. THE Backend SHALL 使用 SQLAlchemy 异步引擎连接 PostgreSQL
2. THE Backend SHALL 使用 redis-py 异步客户端连接 Redis
3. WHEN 应用启动时, THE Backend SHALL 初始化数据库连接
4. WHEN 应用关闭时, THE Backend SHALL 正确关闭数据库连接

### Requirement 7: 日志配置

**User Story:** 作为开发者，我希望有统一的日志配置，以便可以追踪问题和调试。

#### Acceptance Criteria

1. THE Backend SHALL 使用 Python logging 模块配置日志
2. THE Backend SHALL 支持 DEBUG、INFO、WARNING、ERROR 日志级别
3. THE Backend SHALL 日志格式包含：时间、级别、模块名、消息
4. WHEN 开发环境时, THE Backend SHALL 默认使用 DEBUG 级别
