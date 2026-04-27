# AI 开发团队 - Vue 3 前端重构方案

## 1. 技术选型

| 类别 | 选择 |
|------|------|
| 框架 | Vue 3 (Composition API + `<script setup>`) |
| 构建工具 | Vite |
| 语言 | TypeScript |
| 样式 | Tailwind CSS |
| 状态管理 | Pinia |
| HTTP 客户端 | Native `fetch` + EventSource (SSE) |
| 部署 | 独立项目，构建后由 FastAPI 直接托管静态文件 |

## 2. 项目结构

```
frontend-vue/
├── src/
│   ├── api/
│   │   └── development.ts          # SSE 流式调用封装
│   ├── stores/
│   │   └── development.ts          # Pinia store：管理开发流程状态
│   ├── components/
│   │   ├── TopBar.vue              # 顶部导航栏
│   │   ├── RequirementInput.vue    # 需求输入表单
│   │   ├── AgentPipeline.vue       # Agent 执行流水线（总览）
│   │   ├── AgentCard.vue           # 单个 Agent 卡片（接收 SSE 事件）
│   │   ├── ResultPanel.vue         # 最终结果展示（可折叠展开）
│   │   └── ProgressIndicator.vue   # 步骤指示器
│   ├── types/
│   │   └── index.ts                # TypeScript 类型定义
│   ├── App.vue
│   └── main.ts
├── index.html
├── vite.config.ts
├── tailwind.config.js
└── package.json
```

## 3. API 接口对接

后端已有接口（无需改动后端）：

```
POST /develop/stream
请求体: { "requirement": "..." }
返回: SSE stream
```

SSE 事件类型：

| event | data |
|-------|------|
| `status` | `{ type, data: string, done }` — 步骤状态描述 |
| `product_manager` | `{ type, data: string, done }` — PM Agent 输出 |
| `developer` | `{ type, data: string, done }` — Dev Agent 输出 |
| `tester` | `{ type, data: string, done }` — Test Agent 输出 |
| `devops` | `{ type, data: string, done }` — DevOps Agent 输出 |
| `complete` | `{ type, data: FullResult, done: true }` — 全部完成 |
| `error` | `{ type, data: string, done: true }` — 错误 |

## 4. 核心交互流程

```
用户输入需求
    ↓
点击"开始开发"
    ↓
显示 AgentPipeline（4个 AgentCard 横向排列）
    ↓
SSE 建立连接
    ↓
product_manager 事件 → AgentCard[PM] 显示内容
    ↓
developer 事件     → AgentCard[Dev] 显示内容
    ↓
tester 事件       → AgentCard[Test] 显示内容
    ↓
devops 事件       → AgentCard[DevOps] 显示内容
    ↓
complete 事件     → 全部完成，显示 ResultPanel
```

## 5. 状态设计（Pinia Store）

```typescript
interface DevelopmentState {
  requirement: string
  isRunning: boolean
  currentStep: 'idle' | 'pm' | 'dev' | 'test' | 'devops' | 'done' | 'error'
  spec: string
  code: string
  testReport: string
  deploymentPlan: string
  errorMessage: string
}
```

## 6. 部署方案

**方案 A（推荐）：FastAPI 托管静态文件**
```python
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="dist", html=True), name="dist")
```
构建后 `dist/` 目录放到 `ai-dev-team/` 下，后端直接托管。

**方案 B：Nginx 代理**
- `/` → Vue (端口 5173 dev / 静态文件 prod)
- `/api/*` → FastAPI (端口 8000)
- `/develop/stream` → SSE 穿透

## 7. 与 Streamlit 对比

| 维度 | Streamlit | Vue 3 |
|------|-----------|-------|
| 开发速度 | ★★★★★ | ★★★☆☆ |
| 定制化 | ★★☆☆☆ | ★★★★★ |
| 用户体验 | 一般 | 好 |
| 响应式布局 | 差 | 好 |
| 组件复用 | 差 | 好 |
| 部署复杂度 | 低 | 中 |
| 状态管理 | session_state | Pinia |

## 8. 开发计划

1. 初始化 Vite + Vue 3 + TypeScript + Tailwind 项目
2. 定义 TypeScript 类型（对应 SSE 事件结构）
3. 封装 SSE API 调用（`src/api/development.ts`）
4. 实现 Pinia store
5. 实现 6 个 Vue 组件
6. 对接后端 `/develop/stream` 测试
7. 构建并部署到 FastAPI 静态托管

## 9. 环境要求

- Node.js 18+
- `npm create vite@latest` 初始化
- `npm install pinia tailwindcss autoprefixer postcss`
- 构建产物 `dist/` 复制到后端目录
