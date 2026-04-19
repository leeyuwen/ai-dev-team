from langchain_core.prompts import ChatPromptTemplate
from config import create_llm

def get_llm():
    return create_llm()

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
    你是一名资深全栈开发工程师，负责根据产品规格文档实现代码。

    产品规格: {spec}

    请输出以下内容:
    1. 技术栈选择
    2. 代码实现
    3. 部署步骤
    4. 测试建议
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
        "product_manager": product_manager_agent(),
        "developer": developer_agent(),
        "tester": tester_agent(),
        "devops": devops_agent()
    }