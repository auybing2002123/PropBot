# 实现任务

## 任务概览

本文档定义了前端实现的具体任务，按依赖关系排序。

---

## 任务 1: 项目初始化

### 描述
使用 Vite 创建 Vue3 + TypeScript 项目，安装核心依赖。

### 验收标准
- [x] 使用 `npm create vite@latest frontend -- --template vue-ts` 创建项目
- [x] 安装 Element Plus、Vue Router、Pinia、axios、ECharts
- [x] 配置 Element Plus 按需导入（unplugin-auto-import + unplugin-vue-components）
- [x] 配置 SCSS 支持
- [x] 创建 `.env.development` 配置 API 地址

### 相关文件
- `frontend/package.json`
- `frontend/vite.config.ts`
- `frontend/tsconfig.json`
- `frontend/.env.development`

---

## 任务 2: 样式和类型基础

### 描述
创建全局样式变量和 TypeScript 类型定义。

### 验收标准
- [x] 创建 `src/assets/styles/variables.scss` 定义颜色、字体、卡片样式变量
- [x] 创建 `src/assets/styles/global.scss` 定义全局样式重置
- [x] 创建 `src/types/api.ts` 定义 API 响应类型
- [x] 创建 `src/types/chat.ts` 定义对话相关类型
- [x] 创建 `src/types/calculator.ts` 定义计算器相关类型

### 相关文件
- `frontend/src/assets/styles/variables.scss`
- `frontend/src/assets/styles/global.scss`
- `frontend/src/types/api.ts`
- `frontend/src/types/chat.ts`
- `frontend/src/types/calculator.ts`

---

## 任务 3: API 层封装

### 描述
封装 axios 实例和各模块 API 接口。

### 验收标准
- [x] 创建 `src/api/index.ts` 配置 axios 实例和拦截器
- [x] 创建 `src/api/auth.ts` 封装用户认证接口
- [x] 创建 `src/api/chat.ts` 封装对话接口（含 SSE）
- [x] 创建 `src/api/calculator.ts` 封装计算器接口
- [x] 创建 `src/api/conversation.ts` 封装对话历史接口
- [x] 创建 `src/utils/sse.ts` 实现 SSE 客户端

### 相关文件
- `frontend/src/api/index.ts`
- `frontend/src/api/auth.ts`
- `frontend/src/api/chat.ts`
- `frontend/src/api/calculator.ts`
- `frontend/src/api/conversation.ts`
- `frontend/src/utils/sse.ts`

---

## 任务 4: 状态管理

### 描述
使用 Pinia 创建状态管理 store。

### 验收标准
- [x] 创建 `src/stores/auth.ts` 管理用户认证状态
- [x] 创建 `src/stores/city.ts` 管理城市选择状态
- [x] 创建 `src/stores/chat.ts` 管理对话状态
- [x] auth store 支持 localStorage 持久化
- [x] city store 支持 localStorage 持久化

### 相关文件
- `frontend/src/stores/auth.ts`
- `frontend/src/stores/city.ts`
- `frontend/src/stores/chat.ts`

---

## 任务 5: 路由配置

### 描述
配置 Vue Router，定义 5 个页面路由。

### 验收标准
- [x] 创建 `src/router/index.ts` 配置路由
- [x] 配置嵌套路由，AppLayout 为父路由
- [x] 配置路由懒加载
- [x] 默认重定向到 /chat

### 相关文件
- `frontend/src/router/index.ts`

---

## 任务 6: 布局组件

### 描述
实现整体布局，包括顶部导航和底部 Tab。

### 验收标准
- [x] 创建 `src/components/layout/AppHeader.vue` 顶部导航
- [x] 创建 `src/components/layout/AppTabBar.vue` 底部 Tab 导航
- [x] 创建 `src/components/layout/AppLayout.vue` 整体布局
- [x] AppHeader 显示 Logo、标题、城市选择器
- [x] AppTabBar 使用 Element Plus Icons，支持路由切换
- [x] 当前 Tab 高亮显示

### 相关文件
- `frontend/src/components/layout/AppHeader.vue`
- `frontend/src/components/layout/AppTabBar.vue`
- `frontend/src/components/layout/AppLayout.vue`

---

## 任务 7: 公共组件

### 描述
实现城市选择器等公共组件。

### 验收标准
- [x] 创建 `src/components/common/CitySelector.vue` 城市选择器
- [x] 支持南宁、柳州两个选项
- [x] 切换城市时更新 city store

### 相关文件
- `frontend/src/components/common/CitySelector.vue`

---

## 任务 8: 对话组件

### 描述
实现对话页面所需的消息组件。

### 验收标准
- [x] 创建 `src/components/chat/RoleMessage.vue` 角色消息组件
- [x] 创建 `src/components/chat/ChatInput.vue` 输入框组件
- [x] RoleMessage 根据角色显示不同图标和颜色
- [x] RoleMessage 支持 Markdown 渲染
- [x] RoleMessage 支持 loading 状态

### 说明
ChatMessage.vue 和 QuickQuestions.vue 功能已内联到 ChatView.vue 中实现。

### 相关文件
- `frontend/src/components/chat/RoleMessage.vue`
- `frontend/src/components/chat/ChatInput.vue`

---

## 任务 9: 对话页面

### 描述
实现对话页面，支持多角色流式对话。

### 验收标准
- [x] 创建 `src/views/ChatView.vue` 对话页面
- [x] 显示欢迎消息
- [x] 显示快捷问题按钮
- [x] 发送消息调用 SSE 接口
- [x] 逐角色展示流式响应
- [x] 支持多轮对话
- [x] 消息列表自动滚动到底部

### 相关文件
- `frontend/src/views/ChatView.vue`

---

## 任务 10: 计算器组件

### 描述
实现计算器页面所需的表单和结果组件。

### 验收标准
- [x] 创建 `src/components/calculator/LoanForm.vue` 贷款计算表单
- [x] 创建 `src/components/calculator/TaxForm.vue` 税费计算表单
- [x] 创建 `src/components/calculator/TotalCostForm.vue` 总成本表单
- [x] 创建 `src/components/calculator/ResultCard.vue` 结果展示卡片
- [x] 表单使用 Element Plus 组件
- [x] 表单验证必填字段

### 相关文件
- `frontend/src/components/calculator/LoanForm.vue`
- `frontend/src/components/calculator/TaxForm.vue`
- `frontend/src/components/calculator/TotalCostForm.vue`
- `frontend/src/components/calculator/ResultCard.vue`

---

## 任务 11: 计算器页面

### 描述
实现计算器页面，包含 3 个 Tab。

### 验收标准
- [x] 创建 `src/views/CalculatorView.vue` 计算器页面
- [x] 使用 el-tabs 实现 3 个 Tab 切换
- [x] 贷款计算 Tab 调用 /calc/loan 接口
- [x] 税费计算 Tab 调用 /calc/tax 接口
- [x] 总成本 Tab 调用 /calc/total_cost 接口
- [x] 显示计算结果

### 相关文件
- `frontend/src/views/CalculatorView.vue`

---

## 任务 12: 市场分析组件

### 描述
实现市场分析页面所需的图表和数据组件。

### 验收标准
- [x] 创建 `src/components/market/DataCard.vue` 数据卡片组件
- [x] 创建 `src/components/market/PriceChart.vue` 房价走势图组件
- [x] 创建 `src/components/market/DistrictTable.vue` 区域对比表组件
- [x] PriceChart 使用 ECharts 折线图
- [x] DataCard 显示数值和环比变化

### 相关文件
- `frontend/src/components/market/DataCard.vue`
- `frontend/src/components/market/PriceChart.vue`
- `frontend/src/components/market/DistrictTable.vue`

---

## 任务 13: 市场分析页面

### 描述
实现市场分析页面，展示房价数据和图表。

### 验收标准
- [x] 创建 `src/views/MarketView.vue` 市场分析页面
- [x] 显示城市和区域选择器
- [x] 显示 4 个数据卡片（均价、环比、成交量、去化周期）
- [x] 显示房价走势折线图
- [x] 显示区域对比表格
- [x] 切换城市/区域时刷新数据
- [x] 包含"咨询 AI"按钮

### 相关文件
- `frontend/src/views/MarketView.vue`

---

## 任务 14: 政策组件

### 描述
实现政策页面所需的卡片组件。

### 验收标准
- [x] 创建 `src/components/common/PolicyCard.vue` 政策卡片组件
- [x] 显示政策标题、要点、来源、更新时间
- [x] 包含"咨询 AI"按钮

### 相关文件
- `frontend/src/components/common/PolicyCard.vue`

---

## 任务 15: 政策页面

### 描述
实现政策页面，展示限购限贷等政策。

### 验收标准
- [x] 创建 `src/views/PolicyView.vue` 政策页面
- [x] 显示城市选择器
- [x] 使用 el-tabs 实现政策分类（限购、公积金、贷款、流程）
- [x] 以卡片列表展示政策
- [x] 点击"咨询 AI"跳转到对话页面

### 相关文件
- `frontend/src/views/PolicyView.vue`

---

## 任务 16: 我的页面

### 描述
实现用户中心页面。

### 验收标准
- [x] 创建 `src/views/ProfileView.vue` 我的页面
- [x] 显示用户信息卡片
- [x] 显示功能入口列表（对话历史、收藏、设置、帮助）
- [x] 点击对话历史显示历史列表
- [x] 显示免责声明

### 相关文件
- `frontend/src/views/ProfileView.vue`

---

## 任务 17: 用户认证（已重构）

### 描述
实现独立登录/注册页面，支持用户名+密码认证。

### 验收标准
- [x] ~~首次访问显示注册弹窗~~（已废弃）
- [x] 创建独立登录页面 `src/views/LoginView.vue`
- [x] 支持登录/注册 Tab 切换
- [x] 登录：用户名 + 密码
- [x] 注册：用户名 + 密码 + 确认密码
- [x] 未登录用户访问其他页面自动跳转登录页
- [x] 登录成功跳转到对话页面
- [x] 后端支持密码加密存储
- [x] 路由守卫拦截未认证请求

### 相关文件
- `frontend/src/views/LoginView.vue`（新增）
- `frontend/src/views/ProfileView.vue`（移除注册弹窗）
- `frontend/src/stores/auth.ts`（更新）
- `frontend/src/router/index.ts`（添加路由守卫）
- `frontend/src/api/auth.ts`（更新）
- `backend/app/api/auth.py`（更新）
- `backend/app/models/user.py`（添加密码字段）

---

## 任务 18: 入口文件和应用配置

### 描述
配置应用入口和全局设置。

### 验收标准
- [x] 更新 `src/main.ts` 注册 Router、Pinia、Element Plus
- [x] 更新 `src/App.vue` 使用 router-view
- [x] 导入全局样式
- [x] 配置 Element Plus 中文语言包

### 相关文件
- `frontend/src/main.ts`
- `frontend/src/App.vue`

---

## 任务依赖关系

```
任务 1 (项目初始化)
    ↓
任务 2 (样式和类型) ← 任务 3 (API 层)
    ↓                    ↓
任务 4 (状态管理) ←──────┘
    ↓
任务 5 (路由配置)
    ↓
任务 6 (布局组件) ← 任务 7 (公共组件)
    ↓
任务 8 (对话组件) → 任务 9 (对话页面)
    ↓
任务 10 (计算器组件) → 任务 11 (计算器页面)
    ↓
任务 12 (市场组件) → 任务 13 (市场页面)
    ↓
任务 14 (政策组件) → 任务 15 (政策页面)
    ↓
任务 16 (我的页面) ← 任务 17 (用户认证)
    ↓
任务 18 (入口文件)
```

---

## 测试验证

每个任务完成后，使用以下方式验证：

1. **开发服务器**: `npm run dev` 启动，访问 http://localhost:5173
2. **页面渲染**: 检查页面是否正确渲染，无控制台错误
3. **API 调用**: 使用浏览器开发者工具检查网络请求
4. **响应式**: 调整浏览器窗口大小，检查布局适配

---

## 完成状态

✅ 所有 18 个任务已完成

- 构建验证：`npm run build` 通过
- TypeScript 类型检查：通过
- 所有页面和组件已创建
