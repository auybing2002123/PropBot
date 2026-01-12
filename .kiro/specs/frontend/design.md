# 技术设计文档

## 概述

本文档描述购房决策智能助手前端的技术设计方案。前端采用 Vue3 组合式 API + TypeScript，使用 Element Plus 组件库和 ECharts 图表库，实现响应式 Web 应用。

## 架构设计

```
frontend/
├── public/                    # 静态资源
├── src/
│   ├── api/                   # API 接口封装
│   │   ├── index.ts           # axios 实例配置
│   │   ├── auth.ts            # 用户认证 API
│   │   ├── chat.ts            # 对话 API（含 SSE）
│   │   ├── calculator.ts      # 计算器 API
│   │   ├── conversation.ts    # 对话历史 API
│   │   └── market.ts          # 市场数据 API
│   ├── assets/                # 静态资源（样式、图片）
│   │   └── styles/
│   │       ├── variables.scss # 全局变量
│   │       └── global.scss    # 全局样式
│   ├── components/            # 公共组件
│   │   ├── layout/
│   │   │   ├── AppHeader.vue  # 顶部导航
│   │   │   ├── AppTabBar.vue  # 底部 Tab 导航
│   │   │   └── AppLayout.vue  # 整体布局
│   │   ├── chat/
│   │   │   ├── ChatMessage.vue      # 消息组件
│   │   │   ├── RoleMessage.vue      # 角色消息组件
│   │   │   ├── QuickQuestions.vue   # 快捷问题
│   │   │   └── ChatInput.vue        # 输入框
│   │   ├── calculator/
│   │   │   ├── LoanForm.vue         # 贷款计算表单
│   │   │   ├── TaxForm.vue          # 税费计算表单
│   │   │   └── ResultCard.vue       # 结果卡片
│   │   ├── market/
│   │   │   ├── DataCard.vue         # 数据卡片
│   │   │   ├── PriceChart.vue       # 房价走势图
│   │   │   └── DistrictTable.vue    # 区域对比表
│   │   └── common/
│   │       ├── CitySelector.vue     # 城市选择器
│   │       └── PolicyCard.vue       # 政策卡片
│   ├── views/                 # 页面组件
│   │   ├── ChatView.vue       # 对话页面
│   │   ├── CalculatorView.vue # 计算器页面
│   │   ├── MarketView.vue     # 市场分析页面
│   │   ├── PolicyView.vue     # 政策页面
│   │   └── ProfileView.vue    # 我的页面
│   ├── stores/                # Pinia 状态管理
│   │   ├── auth.ts            # 用户认证状态
│   │   ├── city.ts            # 城市选择状态
│   │   └── chat.ts            # 对话状态
│   ├── router/                # 路由配置
│   │   └── index.ts
│   ├── types/                 # TypeScript 类型定义
│   │   ├── api.ts             # API 响应类型
│   │   ├── chat.ts            # 对话相关类型
│   │   └── calculator.ts      # 计算器相关类型
│   ├── utils/                 # 工具函数
│   │   ├── format.ts          # 格式化函数
│   │   └── sse.ts             # SSE 客户端
│   ├── App.vue                # 根组件
│   └── main.ts                # 入口文件
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── .env.development           # 开发环境变量
```

## 组件设计

### 1. AppLayout 布局组件

```vue
<!-- src/components/layout/AppLayout.vue -->
<template>
  <div class="app-layout">
    <AppHeader />
    <main class="app-main">
      <router-view />
    </main>
    <AppTabBar />
  </div>
</template>
```

### 2. RoleMessage 角色消息组件

```typescript
// 角色配置
const ROLE_CONFIG = {
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
```

```vue
<!-- src/components/chat/RoleMessage.vue -->
<template>
  <div class="role-message" :style="{ borderLeftColor: roleConfig.color }">
    <div class="role-header">
      <component :is="roleConfig.icon" :style="{ color: roleConfig.color }" />
      <span class="role-name">{{ roleConfig.name }}</span>
    </div>
    <div class="role-content" v-html="renderedContent"></div>
  </div>
</template>
```

### 3. SSE 客户端

```typescript
// src/utils/sse.ts
export interface SSEEvent {
  type: 'role_start' | 'role_result' | 'discussion' | 'error' | 'done' | 'conversation_created'
  role?: string
  name?: string
  icon?: string
  content?: string
  code?: number
  message?: string
  conversation_id?: string
}

export function createSSEClient(url: string, body: object) {
  return {
    async *stream(): AsyncGenerator<SSEEvent> {
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })
      
      const reader = response.body!.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6))
            yield data as SSEEvent
          }
        }
      }
    }
  }
}
```

### 4. 对话状态管理

```typescript
// src/stores/chat.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { v4 as uuidv4 } from 'uuid'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  roleId?: string  // 角色ID（assistant消息）
  roleName?: string
  roleIcon?: string
  roleColor?: string
  loading?: boolean
}

export const useChatStore = defineStore('chat', () => {
  const sessionId = ref(uuidv4())
  const conversationId = ref<string | null>(null)
  const messages = ref<Message[]>([])
  const isLoading = ref(false)
  
  function addUserMessage(content: string) {
    messages.value.push({
      id: uuidv4(),
      role: 'user',
      content
    })
  }
  
  function addRoleMessage(roleId: string, roleName: string, roleIcon: string, roleColor: string) {
    const id = uuidv4()
    messages.value.push({
      id,
      role: 'assistant',
      content: '',
      roleId,
      roleName,
      roleIcon,
      roleColor,
      loading: true
    })
    return id
  }
  
  function updateRoleMessage(id: string, content: string) {
    const msg = messages.value.find(m => m.id === id)
    if (msg) {
      msg.content = content
      msg.loading = false
    }
  }
  
  function clearMessages() {
    messages.value = []
    sessionId.value = uuidv4()
    conversationId.value = null
  }
  
  return {
    sessionId,
    conversationId,
    messages,
    isLoading,
    addUserMessage,
    addRoleMessage,
    updateRoleMessage,
    clearMessages
  }
})
```

### 5. 计算器表单组件

```typescript
// src/types/calculator.ts
export interface LoanCalcParams {
  price: number           // 房屋总价（元）
  down_payment_ratio: number  // 首付比例
  years: number           // 贷款年限
  rate: number            // 年利率（%）
  method: 'equal_payment' | 'equal_principal'
}

export interface LoanCalcResult {
  down_payment: number    // 首付金额
  loan_amount: number     // 贷款金额
  monthly_payment: number // 月供
  total_interest: number  // 总利息
  total_payment: number   // 还款总额
}

export interface TaxCalcParams {
  price: number           // 房屋总价
  area: number            // 面积
  is_first_home: boolean  // 是否首套
  house_age_years: number // 房龄
  original_price?: number // 原购买价格
}

export interface TaxCalcResult {
  deed_tax: number        // 契税
  vat: number             // 增值税
  income_tax: number      // 个税
  agent_fee: number       // 中介费
  total: number           // 总税费
}
```

### 6. 市场数据图表

```typescript
// src/components/market/PriceChart.vue
import * as echarts from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([LineChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer])

// 图表配置
const chartOption = {
  tooltip: { trigger: 'axis' },
  xAxis: {
    type: 'category',
    data: ['2019', '2020', '2021', '2022', '2023', '2024']
  },
  yAxis: {
    type: 'value',
    name: '均价(元/㎡)'
  },
  series: [{
    type: 'line',
    smooth: true,
    data: priceData,
    itemStyle: { color: '#1890ff' }
  }]
}
```

## API 接口封装

### axios 实例配置

```typescript
// src/api/index.ts
import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api/v1',
  timeout: 30000
})

// 响应拦截器
api.interceptors.response.use(
  response => {
    const { code, message, data } = response.data
    if (code !== 0) {
      ElMessage.error(message || '请求失败')
      return Promise.reject(new Error(message))
    }
    return data
  },
  error => {
    if (error.code === 'ECONNABORTED') {
      ElMessage.error('请求超时，请稍后重试')
    } else if (!error.response) {
      ElMessage.error('网络异常，请检查网络连接')
    } else {
      ElMessage.error(error.response.data?.message || '服务器错误')
    }
    return Promise.reject(error)
  }
)

export default api
```

### 对话 API

```typescript
// src/api/chat.ts
import { createSSEClient, SSEEvent } from '@/utils/sse'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api/v1'

export interface ChatParams {
  session_id: string
  message: string
  mode?: 'standard' | 'discussion'
  conversation_id?: string
  user_id?: string
}

export async function* sendMessage(params: ChatParams): AsyncGenerator<SSEEvent> {
  const client = createSSEClient(`${API_BASE}/chat`, params)
  yield* client.stream()
}

export async function clearSession(sessionId: string) {
  const response = await fetch(`${API_BASE}/chat/${sessionId}`, {
    method: 'DELETE'
  })
  return response.json()
}
```

### 计算器 API

```typescript
// src/api/calculator.ts
import api from './index'
import type { LoanCalcParams, LoanCalcResult, TaxCalcParams, TaxCalcResult } from '@/types/calculator'

export async function calcLoan(params: LoanCalcParams): Promise<LoanCalcResult> {
  return api.post('/calc/loan', params)
}

export async function calcTax(params: TaxCalcParams): Promise<TaxCalcResult> {
  return api.post('/calc/tax', params)
}

export async function calcTotalCost(params: object): Promise<object> {
  return api.post('/calc/total_cost', params)
}
```

## 路由配置

```typescript
// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    component: () => import('@/components/layout/AppLayout.vue'),
    children: [
      {
        path: '',
        redirect: '/chat'
      },
      {
        path: 'chat',
        name: 'Chat',
        component: () => import('@/views/ChatView.vue'),
        meta: { title: '智能对话' }
      },
      {
        path: 'calculator',
        name: 'Calculator',
        component: () => import('@/views/CalculatorView.vue'),
        meta: { title: '购房计算器' }
      },
      {
        path: 'market',
        name: 'Market',
        component: () => import('@/views/MarketView.vue'),
        meta: { title: '市场分析' }
      },
      {
        path: 'policy',
        name: 'Policy',
        component: () => import('@/views/PolicyView.vue'),
        meta: { title: '购房政策' }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/ProfileView.vue'),
        meta: { title: '我的' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
```

## 样式变量

```scss
// src/assets/styles/variables.scss

// 主题色
$primary-color: #1890ff;
$success-color: #52c41a;
$warning-color: #faad14;
$info-color: #1890ff;
$purple-color: #722ed1;

// 角色颜色
$role-financial: #52c41a;
$role-policy: #1890ff;
$role-market: #faad14;
$role-consultant: #722ed1;

// 背景色
$bg-color: #f5f7fa;
$card-bg: #ffffff;

// 文字颜色
$text-primary: #333333;
$text-secondary: #666666;
$text-tertiary: #999999;

// 卡片样式
$card-radius: 12px;
$card-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);

// 字体
$font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'PingFang SC', 'Microsoft YaHei', sans-serif;
$font-size-title: 18px;
$font-size-body: 14px;
$font-size-caption: 12px;
```

## 环境变量

```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8080/api/v1
```

```bash
# .env.production
VITE_API_BASE_URL=/api/v1
```

## 依赖清单

```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "axios": "^1.6.0",
    "element-plus": "^2.4.0",
    "@element-plus/icons-vue": "^2.3.0",
    "echarts": "^5.4.0",
    "uuid": "^9.0.0",
    "marked": "^11.0.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "sass": "^1.69.0",
    "unplugin-auto-import": "^0.17.0",
    "unplugin-vue-components": "^0.26.0"
  }
}
```
