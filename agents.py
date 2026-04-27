from langchain_core.prompts import ChatPromptTemplate
from config import create_llm
from skill_manager import build_skill_context, get_skills_for_task

def get_llm(provider=None):
    return create_llm(provider)

def architect_agent():
    llm = get_llm()
    prompt = ChatPromptTemplate.from_template("""
你是一名资深系统架构师，负责根据产品需求文档设计系统架构和技术方案。

用户需求: {requirement}

产品规格文档: {spec}

请输出以下内容:
1. 系统概述
2. 架构设计（包括架构图/技术选型）
3. 模块划分
4. 技术栈详细说明
5. 关键技术方案
""")
    return {
        "name": "架构师",
        "prompt": prompt,
        "llm": llm
    }

def product_manager_agent():
    llm = get_llm()
    prompt = ChatPromptTemplate.from_template("""
    你是一名资深产品经理，负责分析用户需求并生成详细的产品规格文档。

    用户需求: {requirement}

    请输出以下内容:
    1. 产品概述
    2. 核心功能
    3. 技术需求
    4. 验收标准
    5. 开发计划
    """)

    return {
        "name": "产品经理",
        "prompt": prompt,
        "llm": llm
    }

def developer_agent():
    llm = get_llm()
    prompt = ChatPromptTemplate.from_template("""
你是一名资深全栈开发工程师，负责根据产品规格文档和架构设计实现代码。

产品规格: {spec}

架构设计: {architecture}

技能上下文: {skill_context}

请输出以下内容:
1. 技术栈选择
2. 代码实现
3. 部署步骤
4. 测试建议

重要原则（来自 superpowers 开发方法论）:
- **verification-before-completion**: 在宣布完成前，必须提供可验证的证据（测试通过、构建成功、端点可用）
- **subagent-driven-development**: 如果有多个独立任务需要并行执行，通过 delegate_task 委托给子代理
- **test-driven-development**: 优先编写测试用例（RED-GREEN-REFACTOR 循环），再写实现代码
""")
    return {
        "name": "开发工程师",
        "prompt": prompt,
        "llm": llm
    }

def tester_agent():
    llm = get_llm()
    prompt = ChatPromptTemplate.from_template("""
你是一名专业测试工程师，负责测试代码质量和功能完整性。

产品规格: {spec}
代码实现: {code}

请输出以下内容:
1. 测试计划
2. 测试用例
3. 预期结果
4. 测试报告

重要原则（来自 superpowers 开发方法论）:
- **test-driven-development**: 测试先行，RED-GREEN-REFACTOR 循环
- **verification-before-completion**: 每项测试必须有可验证的通过/失败证据
- **systematic-debugging**: 发现 bug 时，按 4 阶段根因分析（症状→假设→验证→修复）排查
""")
    return {
        "name": "测试工程师",
        "prompt": prompt,
        "llm": llm
    }

def devops_agent():
    llm = get_llm()
    prompt = ChatPromptTemplate.from_template("""
    你是一名DevOps工程师，负责代码的部署和运维。

    代码实现: {code}
    测试报告: {test_report}

    请输出以下内容:
    1. 部署架构
    2. CI/CD配置
    3. 监控方案
    4. 维护建议
    """)

    return {
        "name": "部署工程师",
        "prompt": prompt,
        "llm": llm
    }

def get_all_agents():
    return {
        "architect": architect_agent(),
        "product_manager": product_manager_agent(),
        "developer": developer_agent(),
        "tester": tester_agent(),
        "devops": devops_agent()
    }