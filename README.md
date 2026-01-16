# 🏠 购房决策智能助手 (PropBot)

一个基于多智能体协作的购房决策辅助系统，帮助用户做出科学的购房决策。

## ✨ 功能特点

- **智能对话**：基于 DeepSeek API 的多角色 AI 助手，支持自然语言交互
- **多角色协作**：财务顾问、政策专家、市场分析师、购房顾问四大角色协同工作
- **财务规划**：贷款计算（公积金/商贷/组合贷）、税费估算、还款压力评估
- **政策咨询**：限购限贷政策查询、购房流程指导、常见问题解答
- **市场分析**：房价走势、区域对比、购房时机判断
- **知识检索**：基于 RAG 的政策文档检索，支持本地 BGE 中文向量模型

## 🛠️ 技术栈

### 后端
- **框架**：FastAPI + Uvicorn
- **数据库**：PostgreSQL（业务数据）+ Redis（缓存）+ Chroma（向量库）
- **AI**：DeepSeek API + 本地 BGE Embedding 模型
- **ORM**：SQLAlchemy + Alembic

### 前端
- **框架**：Vue 3 + TypeScript + Vite
- **UI**：Element Plus
- **图表**：ECharts
- **状态管理**：Pinia

## 📁 项目结构

```
PropBot/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/            # API 接口
│   │   ├── agent/          # Agent 引擎和工具
│   │   ├── db/             # 数据库连接
│   │   ├── llm/            # LLM 客户端
│   │   ├── models/         # 数据模型
│   │   └── utils/          # 工具函数
│   ├── alembic/            # 数据库迁移
│   ├── data/               # 知识库数据
│   ├── scripts/            # 初始化脚本
│   └── tests/              # 测试文件
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── api/           # API 封装
│   │   ├── components/    # Vue 组件
│   │   ├── stores/        # Pinia 状态
│   │   ├── views/         # 页面视图
│   │   └── utils/         # 工具函数
│   └── public/            # 静态资源
├── docs/                   # 项目文档
└── docker-compose.yml      # Docker 编排
```

## 🚀 快速开始

### 环境要求

- **Python**: 3.11+
- **Node.js**: 18+
- **Docker**: 用于运行数据库服务
- **操作系统**: Windows (WSL) / Linux / macOS

### 1. 克隆项目

```bash
git clone https://github.com/your-username/PropBot.git
cd PropBot
```

### 2. 启动数据库服务

```bash
# 使用 Docker Compose 启动 PostgreSQL、Redis、Chroma
docker compose up -d

# 检查服务状态
docker compose ps
```

服务端口：
- PostgreSQL: `5434`
- Redis: `6380`
- Chroma: `8001`

### 3. 配置后端

```bash
cd backend

# 创建 conda 环境（推荐）
conda create -n house-advisor python=3.11
conda activate house-advisor

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 DeepSeek API Key
```

`.env` 配置说明：

```env
# 必填：DeepSeek API 密钥
DEEPSEEK_API_KEY=your_api_key_here

# 数据库配置（使用默认值即可）
DATABASE_URL=postgresql://house_advisor:house_advisor_pwd@localhost:5434/house_advisor
REDIS_URL=redis://localhost:6380/0
CHROMA_URL=http://localhost:8001

# 可选：本地 Embedding 模型路径
EMBEDDING_MODEL_PATH=~/models/bge-base-zh-v1.5
```

### 4. 初始化数据库

```bash
# 运行数据库迁移
alembic upgrade head

# 初始化知识库数据
python scripts/init_knowledge_base.py
```

### 5. 启动后端服务

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

后端 API 文档：http://localhost:8080/docs

### 6. 配置前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端访问地址：http://localhost:5173

## 📖 使用指南

### 智能对话

在对话页面输入你的购房问题，AI 助手会自动调度合适的角色为你解答：

- **财务问题**："我月收入1.5万，能买150万的房子吗？"
- **政策问题**："南宁现在还限购吗？"
- **市场问题**："青秀区和良庆区哪个更值得买？"
- **综合咨询**："我想在南宁买房，预算150万，给我一些建议"

### 计算器工具

- **贷款计算**：支持公积金、商贷、组合贷三种方案
- **税费计算**：契税、增值税、个税、中介费等
- **总成本计算**：首付 + 贷款 + 税费 + 装修等全部费用

### 市场分析

- 查看南宁、柳州各区房价走势
- 区域对比分析
- 购房时机判断

## 🔧 开发指南

### 后端开发

```bash
# 在 WSL 中运行后端
cd /mnt/e/code/PropBot/backend
conda activate house-advisor
uvicorn app.main:app --reload --port 8080
```

### 前端开发

```bash
# 在 Windows 中运行前端
cd E:\code\PropBot\frontend
npm run dev
```

### 运行测试

```bash
# 后端测试
cd backend
pytest

# 前端构建
cd frontend
npm run build
```

## 📝 API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/chat` | POST | 智能对话（SSE 流式响应） |
| `/api/v1/calc/loan` | POST | 贷款计算 |
| `/api/v1/calc/tax` | POST | 税费计算 |
| `/api/v1/calc/total_cost` | POST | 总成本计算 |
| `/api/v1/market/{city}` | GET | 获取市场数据 |
| `/api/v1/conversations` | GET/POST | 对话管理 |
| `/api/v1/auth/login` | POST | 用户登录 |
| `/api/v1/auth/register` | POST | 用户注册 |

完整 API 文档请访问：http://localhost:8080/docs

## 🏗️ 部署

### 生产环境部署

1. **构建前端**

```bash
cd frontend
npm run build
# 构建产物在 dist/ 目录
```

2. **配置 Nginx**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 代理
    location /api {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

3. **使用 Gunicorn 运行后端**

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8080
```

## 🎯 目标城市

当前支持：
- 广西南宁
- 广西柳州

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 联系方式

如有问题，请提交 Issue 或联系项目维护者。
