# 🤖 AI 开发团队

一个由多个AI Agent组成的开发团队，从需求到部署全流程自动化。

## 🎯 项目功能

- **产品经理**：分析用户需求，生成详细的产品规格文档
- **开发工程师**：根据产品规格实现代码
- **测试工程师**：测试代码质量和功能完整性
- **部署工程师**：负责代码的部署和运维

## 🛠️ 技术栈

- **后端**：FastAPI + Python
- **AI框架**：LangChain + LangGraph
- **LLM**：OpenAI GPT-4
- **前端**：Streamlit
- **部署**：Docker（可选）

## 📁 项目结构

```
├── app.py              # FastAPI后端服务
├── frontend.py         # Streamlit前端应用
├── agents.py           # AI Agent定义
├── workflow.py         # 工作流管理
├── config.py           # 配置管理
├── requirements.txt    # 依赖管理
├── .env.example        # 环境变量模板
└── README.md           # 项目说明
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制环境变量模板并添加您的OpenAI API密钥：

```bash
copy .env.example .env
# 编辑.env文件，添加OPENAI_API_KEY
```

### 3. 启动后端服务

```bash
python app.py
```

后端服务将在 `http://localhost:8000` 启动。

### 4. 启动前端应用

```bash
streamlit run frontend.py
```

前端应用将在 `http://localhost:8501` 启动。

## 📖 使用说明

1. **输入项目需求**：在前端界面中详细描述您的项目需求
2. **点击开始开发**：AI开发团队会自动处理
3. **查看结果**：系统会生成以下内容：
   - 产品规格文档
   - 代码实现
   - 测试报告
   - 部署计划

## 📝 示例需求

```
创建一个基于FastAPI的用户管理系统，包含以下功能：
1. 用户注册和登录
2. JWT认证
3. 用户信息管理
4. 角色权限控制
5. 数据持久化使用PostgreSQL
```

## 🔧 API接口

### POST /develop

**请求体**：
```json
{
  "requirement": "创建一个用户管理系统..."
}
```

**响应**：
```json
{
  "requirement": "创建一个用户管理系统...",
  "spec": "产品规格文档...",
  "code": "代码实现...",
  "test_report": "测试报告...",
  "deployment_plan": "部署计划...",
  "history": ["产品经理: 产品规格文档...", ...]
}
```

## 📈 扩展功能

- **添加更多Agent**：如UI设计师、数据分析师等
- **集成更多工具**：如代码执行、搜索等
- **优化工作流**：支持并行处理和条件分支
- **添加内存系统**：保存历史项目和学习经验

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License