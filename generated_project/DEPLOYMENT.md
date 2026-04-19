# 部署文档

The user is asking me to provide additional content for a calculator project, specifically:
1. 部署架构 (Deployment Architecture)
2. CI/CD配置 (CI/CD Configuration)
3. 监控方案 (Monitoring Solution)
4. 维护建议 (Maintenance Suggestions)

This is a continuation of the previous product requirements, technical implementation, and test documentation. I need to provide detailed, practical guidance for deploying and maintaining the calculator application.

Let me structure this comprehensively with clear tables, diagrams, and code examples.


# 计算器项目部署与运维指南

---

## 1. 部署架构

### 1.1 系统架构概览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              部署架构总览                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  用户请求                                                                   │
│     │                                                                      │
│     ▼                                                                      │
│  ┌──────────────┐                                                          │
│  │   CDN网络     │  ──→  全球边缘节点加速                                    │
│  │ (Cloudflare) │                                                          │
│  └──────┬───────┘                                                          │
│         │                                                                  │
│         ▼                                                                  │
│  ┌──────────────┐                                                          │
│  │ GitHub Pages │  ──→  静态文件托管 (HTML/CSS/JS)                          │
│  │   静态服务器  │                                                          │
│  └──────┬───────┘                                                          │
│         │                                                                  │
│         ▼                                                                  │
│  ┌──────────────┐                                                          │
│  │    Git仓库   │  ──→  源代码版本控制                                       │
│  │   (GitHub)   │                                                          │
│  └──────────────┘                                                          │
│                                                                             │
│  ┌──────────────┐                                                          │
│  │   第三方CDN   │  ──→  BigNumber.js, Font Awesome                         │
│  │   静态资源    │                                                          │
│  └──────────────┘                                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 架构组件说明

| 组件 | 服务商 | 用途 | 成本 | 备注 |
|-----|-------|------|-----|------|
| **源代码仓库** | GitHub | 代码版本管理 | 免费 | 需设为Public |
| **静态托管** | GitHub Pages | 静态文件托管与分发 | 免费 | 自动构建部署 |
| **CDN加速** | GitHub 全球网络 | 静态资源全球分发 | 免费 | 内置支持 |
| **外部依赖** | cdnjs/Cloudflare | JS库和字体CDN | 免费 | 高可用保障 |
| **域名解析** | 自选DNS服务商 | 域名指向 | 付费可选 | 如需自定义域名 |
| **监控服务** | 浏览器内置 | 前端错误监控 | 免费 | 可扩展接入Sentry |

### 1.3 部署环境配置

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           部署环境配置                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  生产环境 (Production)                                                      │
│  ├── 访问地址: https://用户名.github.io/calculator/                         │
│  ├── 部署源: main分支 /docs 文件夹 或 根目录                                 │
│  ├── 构建命令: 无 (纯静态)                                                   │
│  └── 域名: 可绑定自定义域名                                                  │
│                                                                             │
│  预发布环境 (Staging)                                                       │
│  ├── 访问地址: https://用户名.github.io/calculator/                         │
│  ├── 说明: 可创建 gh-pages 分支用于预发布测试                                │
│  └── 用途: 上线前最终验证                                                    │
│                                                                             │
│  开发环境 (Development)                                                     │
│  ├── 访问地址: http://localhost:3000                                        │
│  ├── 启动方式: 直接打开 index.html 或使用本地服务器                          │
│  └── 用途: 开发调试                                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.4 域名配置方案

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           域名配置方案                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  方案A: 使用默认域名 (推荐快速上线)                                          │
│  ─────────────────────────────────────────                                  │
│  地址: https://yourusername.github.io/calculator/                           │
│  配置: 无需任何配置，开箱即用                                                │
│  优点: 零配置，立即可用                                                      │
│  缺点: 域名较长，不易记忆                                                    │
│                                                                             │
│  方案B: 使用自定义域名 (推荐正式项目)                                        │
│  ─────────────────────────────────────────                                  │
│  地址: https://calc.example.com                                             │
│  配置: 需要配置CNAME记录                                                     │
│  优点: 品牌化，专业形象                                                      │
│  缺点: 需要域名费用，需额外配置                                              │
│                                                                             │
│  方案C: 使用子域名 (折中方案)                                               │
│  ─────────────────────────────────────────                                  │
│  地址: https://calculator.example.com                                       │
│  配置: 需要配置ALIAS/CNAME记录                                               │
│  优点: 较简短，易记忆                                                       │
│  缺点: 需要域名和配置                                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. CI/CD 配置

### 2.1 CI/CD 流程设计

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CI/CD 流程图                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   代码提交                                                                   │
│      │                                                                      │
│      ▼                                                                      │
│  ┌─────────────┐                                                            │
│  │ Git Push    │  ──→  触发Webhook                                           │
│  └──────┬──────┘                                                            │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────┐                                                            │
│  │ GitHub      │  ──→  自动检测代码变更                                      │
│  │ Actions     │                                                            │
│  └──────┬──────┘                                                            │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────┐                                                            │
│  │ 构建检查     │  ──→  自动执行                                               │
│  │ (可选)       │     • HTML/CSS/JS语法检查                                   │
│  └──────┬──────┘     • Lighthouse性能测试                                    │
│         │         • 自动部署到GitHub Pages                                   │
│         ▼                                                                   │
│  ┌─────────────┐                                                            │
│  │ 自动部署    │  ──→  约1-2分钟后生效                                        │
│  │ GitHub Pages│                                                            │
│  └──────┬──────┘                                                            │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────┐                                                            │
│  │ 部署完成    │  ──→  用户可访问最新版本                                     │
│  │ 通知(可选)  │                                                            │
│  └─────────────┘                                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 GitHub Actions 配置

#### 2.2.1 基础 CI/CD 配置

在工作区创建 `.github/workflows/deploy.yml` 文件：

```yaml
# 计算器项目 - 自动部署配置
name: Deploy Calculator

# 触发条件: main分支有推送时
on:
  push:
    branches:
      - main
  # 也支持手动触发
  workflow_dispatch:

# 设置环境变量
env:
  NODE_VERSION: '18'

# 定义任务
jobs:
  # 部署任务
  deploy:
    runs-on: ubuntu-latest
    
    # 步骤定义
    steps:
      # 1. 检出代码
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # 获取完整提交历史
      
      # 2. 设置Node.js环境
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
      
      # 3. 安装依赖 (如有)
      - name: Install dependencies
        run: npm ci
      
      # 4. 运行测试 (如有)
      - name: Run tests
        run: npm test
        continue-on-error: true  # 测试失败不阻止部署
      
      # 5. 性能检查 (可选)
      - name: Run Lighthouse CI
        uses: treosh/lighthouse-ci-action@v10
        with:
          urls: https://example.com/calculator/
          budgetPath: ./lighthouse-budget.json
        continue-on-error: true
      
      # 6. 部署到 GitHub Pages
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./dist  # 部署目录
          # 如直接在根目录部署，删除publish_dir配置
```

#### 2.2.2 增强版 CI/CD 配置（带代码检查）

```yaml
# 计算器项目 - 增强版CI/CD配置
name: Calculator CI/CD

on:
  push:
    branches:
      - main
      - develop
  pull_request:
    branches:
      - main

env:
  NODE_VERSION: '18'

jobs:
  # 代码质量检查
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
      
      - name: Install dependencies
        run: npm ci
      
      # HTML语法检查
      - name: HTML Lint
        run: npm run lint:html
      
      # CSS语法检查
      - name: CSS Lint
        run: npm run lint:css
      
      # JavaScript语法检查
      - name: JavaScript Lint
        run: npm run lint:js
      
      # 格式化检查
      - name: Check formatting
        run: npm run format:check

  # 测试执行
  test:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run unit tests
        run: npm test
      
      - name: Run e2e tests
        run: npm run test:e2e

  # 部署
  deploy:
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./

  # 通知 (可选)
  notify:
    runs-on: ubuntu-latest
    needs: deploy
    if: always()
    steps:
      - name: Send notification
        if: needs.deploy.result == 'success'
        run: echo "🎉 Deployment successful!"
```

#### 2.2.3 Lighthouse 性能预算配置

创建 `lighthouse-budget.json` 文件：

```json
{
  "ci": {
    "collect": {
      "startServerCommand": "npm run start",
      "url": [
        "http://localhost:3000/index.html"
      ],
      "numberOfRuns": 3
    },
    "assert": {
      "assertions": {
        "categories:performance": ["error", {"minScore": 0.85}],
        "categories:accessibility": ["error", {"minScore": 0.9}],
        "categories:best-practices": ["error", {"minScore": 0.9}],
        "categories:seo": ["error", {"minScore": 0.9}],
        "first-contentful-paint": ["warn", {"maxNumericValue": 2000}],
        "largest-contentful-paint": ["error", {"maxNumericValue": 4000}],
        "cumulative-layout-shift": ["error", {"maxNumericValue": 0.1}],
        "total-blocking-time": ["error", {"maxNumericValue": 500}]
      }
    },
    "upload": {
      "target": "lhci",
      "serverBaseUrl": "https://lhci.example.com",
      "token": "lhci-api-token"
    }
  }
}
```

### 2.3 package.json 配置

```json
{
  "name": "calculator",
  "version": "1.0.0",
  "description": "简单计算器Web应用",
  "scripts": {
    "start": "npx serve . -l 3000",
    "test": "jest",
    "test:e2e": "playwright test",
    "lint:html": "htmlhint src/*.html",
    "lint:css": "stylelint src/*.css",
    "lint:js": "eslint src/*.js",
    "format:check": "prettier --check src/**/*.{html,css,js}",
    "format:fix": "prettier --write src/**/*.{html,css,js}"
  },
  "devDependencies": {
    "jest": "^29.0.0",
    "playwright": "^1.40.0",
    "htmlhint": "^1.1.0",
    "stylelint": "^15.0.0",
    "eslint": "^8.0.0",
    "prettier": "^3.0.0",
    "serve": "^14.0.0"
  }
}
```

---

## 3. 监控方案

### 3.1 监控架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           监控架构概览                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  用户端监控                                                                 │
│     │                                                                      │
│     ▼                                                                      │
│  ┌─────────────────────┐                                                  │
│  │   Real User Monitor  │  ──→  真实用户体验数据收集                         │
│  │        (RUM)         │                                                  │
│  └──────────┬──────────┘                                                  │
│             │                                                              │
│             ▼                                                              │
│  ┌─────────────────────┐                                                  │
│  │   Performance API    │  ──→  Web Vitals 指标                             │
│  └──────────┬──────────┘                                                  │
│             │                                                              │
│             ▼                                                              │
│  ┌─────────────────────┐                                                  │
│  │   Error Tracking     │  ──→  JS错误捕获与上报                            │
│  │   (Sentry/LogRocket) │                                                  │
│  └──────────┬──────────┘                                                  │
│             │                                                              │
│             ▼                                                              │
│  ┌─────────────────────┐                                                  │
│  │   Analytics          │  ──→  用户行为分析                                │
│  │   (可选)              │                                                  │
│  └─────────────────────┘                                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Web Vitals 监控

#### 3.2.1 核心指标定义

| 指标 | 名称 | 目标值 | 含义 |
|-----|------|-------|------|
| **LCP** | Largest Contentful Paint | ≤ 2.5s | 最大内容绘制时间 |
| **FID** | First Input Delay | ≤ 100ms | 首次输入延迟 |
| **CLS** | Cumulative Layout Shift | ≤ 0.1 | 累计布局偏移 |
| **FCP** | First Contentful Paint | ≤ 1.8s | 首次内容绘制 |
| **TTFB** | Time to First Byte | ≤ 800ms | 首字节时间 |

#### 3.2.2 监控代码实现

创建 `monitoring.js` 文件：

```javascript
/**
 * 计算器应用 - 性能监控模块
 */

class PerformanceMonitor {
    constructor() {
        this.metrics = {};
        this.init();
    }

    init() {
        // 监控 Web Vitals
        this.trackLCP();
        this.trackFID();
        this.trackCLS();
        this.trackFCP();
        this.trackTTFB();

        // 监控 JS 错误
        this.trackErrors();

        // 监控资源加载
        this.trackResources();

        // 定期上报数据
        this.scheduleReport();
    }

    /**
     * 获取 LCP 指标
     */
    trackLCP() {
        new PerformanceObserver((entryList) => {
            const entries = entryList.getEntries();
            const lastEntry = entries[entries.length - 1];
            
            this.metrics.lcp = lastEntry.renderTime || lastEntry.loadTime;
            console.log(`[Performance] LCP: ${this.metrics.lcp}ms`);
        }).observe({ type: 'largest-contentful-paint', buffered: true });
    }

    /**
     * 获取 FID 指标
     */
    trackFID() {
        new PerformanceObserver((entryList) => {
            for (const entry of entryList.getEntries()) {
                this.metrics.fid = entry.processingStart - entry.startTime;
                console.log(`[Performance] FID: ${this.metrics.fid}ms`);
            }
        }).observe({ type: 'first-input', buffered: true });
    }

    /**
     * 获取 CLS 指标
     */
    trackCLS() {
        let clsValue = 0;

        new PerformanceObserver((entryList) => {
            for (const entry of entryList.getEntries()) {
                if (!entry.hadRecentInput) {
                    clsValue += entry.value;
                    this.metrics.cls = clsValue;
                    console.log(`[Performance] CLS: ${clsValue}`);
                }
            }
        }).observe({ type: 'layout-shift', buffered: true });
    }

    /**
     * 获取 FCP 指标
     */
    trackFCP() {
        new PerformanceObserver((entryList) => {
            const entries = entryList.getEntriesByName('first-contentful-paint');
            if (entries.length > 0) {
                this.metrics.fcp = entries[0].startTime;
                console.log(`[Performance] FCP: ${this.metrics.fcp}ms`);
            }
        }).observe({ type: 'paint', buffered: true });
    }

    /**
     * 获取 TTFB 指标
     */
    trackTTFB() {
        const observer = new PerformanceObserver((entryList) => {
            const entries = entryList.getEntries();
            for (const entry of entries) {
                if (entry.responseStart > 0) {
                    this.metrics.ttfb = entry.responseStart;
                    console.log(`[Performance] TTFB: ${this.metrics.ttfb}ms`);
                }
            }
        });

        observer.observe({ type: 'navigation', buffered: true });
    }

    /**
     * 监控 JavaScript 错误
     */
    trackErrors() {
        // 监控未捕获的Promise错误
        window.addEventListener('unhandledrejection', (event) => {
            this.reportError('unhandledrejection', event.reason);
        });

        // 监控JavaScript运行时错误
        window.addEventListener('error', (event) => {
            this.reportError('error', {
                message: event.message,
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno
            });
        });
    }

    /**
     * 监控资源加载情况
     */
    trackResources() {
        new PerformanceObserver((entryList) => {
            for (const entry of entryList.getEntries()) {
                if (entry.duration > 1000) { // 加载超过1秒的资源
                    console.warn(`[Performance] Slow resource: ${entry.name} - ${entry.duration}ms`);
                }
            }
        }).observe({ type: 'resource', buffered: true });
    }

    /**
     * 上报错误
     */
    reportError(type, error) {
        const errorData = {
            type,
            message: typeof error === 'string' ? error : error.message,
            url: window.location.href,
            userAgent: navigator.userAgent,
            timestamp: new Date().toISOString(),
            metrics: this.metrics
        };

        // 发送到错误追踪服务 (如Sentry)
        if (typeof Sentry !== 'undefined') {
            Sentry.captureException(error);
        }

        // 控制台输出
        console.error('[Error]', errorData);

        // 发送到后端API (可选)
        // this.sendToServer('/api/errors', errorData);
    }

    /**
     * 定时上报性能数据
     */
    scheduleReport() {
        // 页面加载5秒后上报首次数据
        setTimeout(() => {
            this.reportMetrics();
        }, 5000);

        // 用户离开页面时上报
        window.addEventListener('beforeunload', () => {
            this.reportMetrics();
        });

        // 页面隐藏时上报
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'hidden') {
                this.reportMetrics();
            }
        });
    }

    /**
     * 上报性能指标
     */
    reportMetrics() {
        const reportData = {
            url: window.location.href,
            timestamp: new Date().toISOString(),
            metrics: this.metrics,
            navigation: {
                type: performance.getEntriesByType('navigation')[0]?.type,
                domainLookupStart: performance.getEntriesByType('navigation')[0]?.domainLookupStart,
                connectEnd: performance.getEntriesByType('navigation')[0]?.connectEnd
            }
        };

        console.log('[Metrics Report]', reportData);

        // 发送到分析服务 (可选)
        // this.sendToServer('/api/metrics', reportData);
    }

    /**
     * 获取所有指标
     */
    getMetrics() {
        return this.metrics;
    }

    /**
     * 检查指标是否达标
     */
    checkThresholds() {
        const thresholds = {
            lcp: 2500,
            fid: 100,
            cls: 0.1,
            fcp: 1800,
            ttfb: 800
        };

        const results = {};
        let allPassed = true;

        for (const [key, threshold] of Object.entries(thresholds)) {
            const value = this.metrics[key];
            const passed = value <= threshold;
            results[key] = { value, threshold, passed };
            if (!passed) allPassed = false;
        }

        return { results, allPassed };
    }
}

// 初始化监控
const monitor = new PerformanceMonitor();

// 导出供全局使用
window.monitor = monitor;
```

### 3.3 错误追踪集成 (Sentry)

#### 3.3.1 Sentry 配置

```html
<!-- 在 index.html 头部添加 -->
<head>
    <!-- Sentry SDK -->
    <script
        src="https://browser.sentry-cdn.com/7.54.0/bundle.min.js"
        integrity="sha384-be4M-N3f/jE+6D7V4PDZKN4D4fE+D4w/B4Sjpzj9G1B8K6p8P1uH6Z7E6lJJ6mXU"
        crossorigin="anonymous"
    ></script>
    
    <script>
        // 初始化 Sentry
        Sentry.init({
            dsn: 'https://xxxxx@o123456.ingest.sentry.io/1234567',
            integrations: [
                new Sentry.BrowserTracing(),
                new Sentry.Replay()
            ],
            
            // 性能监控采样率
            tracesSampleRate: 1.0,
            
            // 会话回放采样率
            replaysSessionSampleRate: 0.1,
            replaysOnErrorSampleRate: 1.0,
            
            // 环境
            environment: 'production',
            
            // 发布版本
            release: 'calculator@1.0.0',
            
            // 忽略特定错误
            ignoreErrors: [
                'ResizeObserver loop completed with undelivered notifications'
            ],
            
            // 权限策略
            allowUrls: [
                /https:\/\/.*\.github\.io\/calculator/
            ]
        });

        // 设置用户信息 (可选)
        Sentry.setUser({
            id: navigator.userAgent,
            browser: navigator.browser,
        });

        // 添加上下文
        Sentry.setContext('page', {
            title: document.title,
            url: window.location.href
        });
    </script>
</head>
```

#### 3.3.2 自定义错误边界

```javascript
/**
 * 错误边界组件 - 捕获渲染错误
 */
class ErrorBoundary {
    constructor() {
        this.error = null;
        this.errorInfo = null;
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        console.error('ErrorBoundary caught an error:', error, errorInfo);
        
        if (typeof Sentry !== 'undefined') {
            Sentry.captureException(error, {
                extra: errorInfo
            });
        }
    }
}

// 使用示例
try {
    // 可能有问题的代码
    calculator.calculate();
} catch (error) {
    Sentry.captureException(error, {
        tags: {
            feature: 'calculator'
        },
        extra: {
            currentValue: calculator.currentValue,
            operator: calculator.operator
        }
    });
}
```

### 3.4 GitHub 内置监控

#### 3.4.1 GitHub Pages 部署状态

```
# 检查部署状态
.github/workflows/deploy.yml 会在每次部署后显示状态

# 查看部署历史
仓库 → Actions → Workflow runs → 查看每次部署记录
```

#### 3.4.2 使用 GitHub Issues 进行问题跟踪

```markdown
## Bug 报告模板

**描述**: 
[清晰描述问题]

**步骤复现**:
1. 
2. 
3. 

**预期行为**: 
[期望发生什么]

**实际行为**: 
[实际发生什么]

**环境信息**:
- 浏览器:
- 版本:
- 操作系统:

**截图**:
[如果有的话]
```

---

## 4. 维护建议

### 4.1 维护计划

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           维护计划表                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  日常维护 (每日/每周)                                                        │
│  ├── 检查 GitHub Actions 部署状态                                          │
│  ├── 关注用户反馈和Issue报告                                                │
│  ├── 检查监控告警 (如配置)                                                  │
│  └── 确认服务可用性                                                          │
│                                                                             │
│  周期性维护 (每月)                                                           │
│  ├── 检查外部CDN依赖可用性                                                   │
│  ├── 更新依赖库版本 (如有)                                                   │
│  ├── 运行完整测试套件                                                        │
│  ├── 性能回归测试                                                            │
│  ├── 分析用户使用数据 (如配置分析)                                           │
│  └── 安全漏洞扫描                                                            │
│                                                                             │
│  版本维护 (按需)                                                            │
│  ├── 功能迭代开发                                                            │
│  ├── Bug修复发布                                                             │
│  ├── 性能优化发布                                                            │
│  ├── 安全补丁发布                                                            │
│  └── 依赖库大版本升级                                                         │
│                                                                             │
│  长期维护 (季度/年度)                                                        │
│  ├── 架构评估                                                                │
│  ├── 技术栈更新评估                                                          │
│  ├── 用户调研                                                                │
│  └── 竞争对手分析                                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 依赖管理

#### 4.2.1 CDN 依赖清单

| 依赖 | 用途 | CDN地址 | 监控状态 |
|-----|------|--------|---------|
| BigNumber.js | 高精度计算 | cdnjs.cloudflare.com | ✅ 稳定 |
| Font Awesome | 图标 | cdnjs.cloudflare.com | ✅ 稳定 |

#### 4.2.2 依赖更新检查清单

```markdown
## 依赖更新检查清单

### 更新前
□ 检查当前版本
□ 阅读版本更新日志
□ 评估更新风险
□ 准备回滚方案

### 更新后
□ 运行完整测试
□ 验证功能正常
□ 检查性能指标
□ 确认无控制台错误

### 回滚（如有问题）
□ 立即回退代码
□ 通知相关人员
□ 分析问题原因
□ 修复后重新发布
```

### 4.3 备份策略

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           备份策略                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  源代码备份                                                                  │
│  ├── 位置: GitHub 仓库                                                       │
│  ├── 频率: 每次提交自动备份                                                   │
│  ├── 保留: 完整历史记录                                                       │
│  └── 恢复: 可回滚到任意版本                                                   │
│                                                                             │
│  配置备份                                                                   │
│  ├── 位置: GitHub Secrets (敏感)                                            │
│  ├── 位置: 代码仓库 (非敏感)                                                 │
│  └── 包含: CI/CD配置、环境变量                                               │
│                                                                             │
│  文档备份                                                                   │
│  ├── 位置: 代码仓库 README                                                   │
│  ├── 包含: 部署说明、API文档                                                 │
│  └── 更新: 随版本更新                                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.4 安全建议

#### 4.4.1 安全检查清单

| 检查项 | 说明 | 频率 | 状态 |
|-------|------|------|------|
| HTTPS | 确保使用HTTPS | 部署时确认 | ✅ |
| CSP | 配置内容安全策略 | 部署时确认 | ✅ |
| 依赖安全 | 检查CDN依赖漏洞 | 每月 | ⬜ |
| XSS防护 | 防止XSS攻击 | 代码审查 | ✅ |
| CSP报告 | 监控CSP违规 | 持续监控 | ⬜ |

#### 4.4.2 CSP 配置示例

在 `index.html` 中添加：

```html
<meta http-equiv="Content-Security-Policy" content="
    default-src 'self';
    script-src 'self' 
        https://browser.sentry-cdn.com
        https://cdnjs.cloudflare.com;
    style-src 'self' 
        'unsafe-inline'
        https://cdnjs.cloudflare.com;
    font-src 'self' 
        https://cdnjs.cloudflare.com;
    img-src 'self' data:;
    connect-src 'self' 
        https://o123456.ingest.sentry.io;
    frame-ancestors 'none';
">
```

### 4.5 性能优化建议

#### 4.5.1 优化清单

| 优化项 | 当前状态 | 建议目标 | 优先级 |
|-------|---------|---------|--------|
| 首字节时间 | ~200ms | < 200ms | P1 |
| FCP | ~500ms | < 800ms | P1 |
| LCP | ~1s | < 1.5s | P1 |
| CLS | 0 | < 0.05 | P1 |
| 总资源大小 | ~45KB | < 50KB | P2 |
| JS执行时间 | < 50ms | < 30ms | P2 |

#### 4.5.2 长期优化建议

```markdown
## 性能优化路线图

### P0 (立即)
- [x] 使用CDN加载外部依赖
- [x] 启用Gzip压缩 (GitHub Pages自动支持)
- [x] 优化图片资源

### P1 (短期)
- [ ] 添加Service Worker实现离线缓存
- [ ] 实现资源预加载
- [ ] 添加骨架屏/加载动画

### P2 (中期)
- [ ] 考虑PWA支持
- [ ] 分析是否需要框架重构
- [ ] 添加更多自动化测试

### P3 (长期)
- [ ] 考虑SSR方案
- [ ] 多语言支持
- [ ] 高级功能 (科学计算、汇率转换等)
```

### 4.6 扩展性建议

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           功能扩展路线图                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Phase 1: 基础功能完善                                                       │
│  ├── 添加计算历史记录                                                        │
│  ├── 添加快捷键提示                                                          │
│  └── 暗黑模式切换                                                           │
│                                                                             │
│  Phase 2: 增强功能                                                           │
│  ├── 科学计算模式 (三角函数、幂运算等)                                        │
│  ├── 汇率转换                                                                │
│  ├── 单位转换                                                                │
│  └── 百分比计算器                                                           │
│                                                                             │
│  Phase 3: 高级功能                                                           │
│  ├── 表达式输入 (如 2+3*4)                                                   │
│  ├── 括号支持                                                                │
│  ├── 计算历史导出                                                            │
│  └── 云端同步 (需要后端服务)                                                  │
│                                                                             │
│  Phase 4: 生态扩展                                                           │
│  ├── 浏览器扩展                                                              │
│  ├── iOS/Android App                                                         │
│  ├── 小程序版本                                                              │
│  └── API服务                                                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. 运维检查清单

### 5.1 每日检查

```
□ GitHub Actions 部署状态正常
□ 用户反馈渠道无紧急问题
□ 监控仪表盘无告警 (如配置)
□ 核心计算功能正常
□ 页面可正常访问
```

### 5.2 每周检查

```
□ 分析本周用户反馈
□ 检查GitHub Issues
□ 确认无安全告警
□ 检查依赖可用性
□ 备份重要文档
```

### 5.3 每月检查

```
□ 运行完整测试套件
□ 性能回归测试
□ 检查CDN依赖更新
□ 更新监控阈值
□ 安全漏洞扫描
□ 文档更新
```

### 5.4 发布检查清单

```
发布前检查:
□ 所有测试用例通过
□ 代码已通过Review
□ CHANGELOG已更新
□ 版本号已更新
□ 部署文档已准备
□ 回滚方案已确认

发布中检查:
□ CI/CD流程正常
□ 部署状态成功
□ 页面可访问
□ 核心功能正常

发布后检查:
□ 功能验证通过
□ 性能指标正常
□ 无错误告警
□ 用户反馈正常
□ 监控数据正常
```

---

## 附录

### A. 紧急联系人

| 角色 | 职责 | 联系方式 |
|-----|------|---------|
| 项目负责人 | 重大决策 | |
| 开发者 | 技术支持 | |
| 运维 | 基础设施 | |

### B. 常用链接

```
GitHub 仓库: https://github.com/用户名/calculator
部署地址: https://用户名.github.io/calculator/
Sentry后台: https://sentry.io/organizations/项目
GitHub Actions: https://github.com/用户名/calculator/actions
```

### C. 版本历史

| 版本 | 日期 | 更新内容 | 作者 |
|-----|------|---------|------|
| 1.0.0 | YYYY-MM-DD | 初始版本发布 | |
| | | | |

---

**文档版本**：V1.0  
**最后更新**：2024年  
**下次评审**：2024年XX月