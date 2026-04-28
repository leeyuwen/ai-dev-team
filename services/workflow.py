"""
Workflow 服务层 — 封装所有 Agent 编排逻辑。

职责划分:
  - workflow.py (本文件): 纯函数，ThreadPoolExecutor 内执行，无 FastAPI 依赖
  - app.py: 调用本文件函数，结果写入 ProjectService

两步流程:
  1. PM 阶段   → run_pm_only(requirement)          → (spec, project_id)
  2. 全流程     → run_full_workflow(spec, ...)      → (architecture, code, test_report, deployment_plan)

SSE 流程用 run_pm_only + approve 端点串联；
同步 /develop 用 run_full_workflow。
"""
import json
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from logger import (
    log_agent_start,
    log_agent_complete,
    log_agent_error,
    log_llm_call,
)
from skill_manager import build_skill_context


# ── 内部工具 ─────────────────────────────────────────────────────────────────

def _load_env_and_agents():
    from config import Settings
    from agents import get_all_agents
    from app import load_env  # 延迟导入避免循环

    load_env()
    s = Settings()
    model_name = getattr(s, "minimax_model", "minimax")
    agents = get_all_agents()
    return agents, model_name


def _call_agent(chain, inputs: dict, agent_name: str, model_name: str):
    """执行一次 LLM 调用，返回 content 并记录日志。"""
    t0 = time.time()
    result = chain.invoke(inputs)
    elapsed = int((time.time() - t0) * 1000)
    content = result.content if hasattr(result, "content") else str(result)
    log_agent_complete(agent_name, content)
    log_llm_call(agent_name, model_name, elapsed, status="OK")
    return content


# ── PM 阶段（第一步）──────────────────────────────────────────────────────────

def run_pm_only(requirement: str) -> dict:
    """
    仅运行产品经理 Agent，生成 PRD。
    返回 {"spec": ..., "requirement": ..., "project_id": ..., "name": ...}
    """
    from services.project import svc
    import app  # 延迟导入，避免循环

    request_id = str(uuid.uuid4())[:8]
    agents, model_name = _load_env_and_agents()

    # 创建项目记录
    project = svc.create(requirement, agents=["产品经理"])
    pid = project["id"]

    log_agent_start(f"产品经理 [{request_id}]")
    pm_agent = agents["product_manager"]
    pm_chain = pm_agent["prompt"] | pm_agent["llm"]

    spec = _call_agent(
        pm_chain,
        {"requirement": requirement},
        f"产品经理 [{request_id}]",
        model_name,
    )

    # 持久化 spec
    svc.update(pid, spec=spec, status="draft")

    return {
        "spec": spec,
        "requirement": requirement,
        "project_id": pid,
        "name": project["name"],
    }


# ── 后续流程（第二步：Architect → Dev → Test → DevOps）─────────────────────

def run_approve_workflow(project_id: str, spec: str, skill_context: str = "") -> dict:
    """
    用户 approve 后，执行 Architect → Dev → Test → DevOps 全流程。
    返回 {"architecture": ..., "code": ..., "test_report": ..., "deployment_plan": ...}
    """
    from services.project import svc

    agents, model_name = _load_env_and_agents()

    # Architect
    arch_agent = agents["architect"]
    arch_chain = arch_agent["prompt"] | arch_agent["llm"]
    log_agent_start("架构师")
    architecture = _call_agent(
        arch_chain,
        {"requirement": "", "spec": spec},
        "架构师",
        model_name,
    )

    # Developer
    dev_agent = agents["developer"]
    dev_chain = dev_agent["prompt"] | dev_agent["llm"]
    log_agent_start("开发工程师")
    code = _call_agent(
        dev_chain,
        {"spec": spec, "architecture": architecture, "skill_context": skill_context},
        "开发工程师",
        model_name,
    )

    # Tester
    test_agent = agents["tester"]
    test_chain = test_agent["prompt"] | test_agent["llm"]
    log_agent_start("测试工程师")
    test_report = _call_agent(
        test_chain,
        {"spec": spec, "code": code},
        "测试工程师",
        model_name,
    )

    # DevOps
    devops_agent = agents["devops"]
    devops_chain = devops_agent["prompt"] | devops_agent["llm"]
    log_agent_start("部署工程师")
    deployment_plan = _call_agent(
        devops_chain,
        {"code": code, "test_report": test_report},
        "部署工程师",
        model_name,
    )

    # 持久化所有产出
    svc.update(project_id,
        spec=spec,
        architecture=architecture,
        code=code,
        test_report=test_report,
        deployment_plan=deployment_plan,
        status="coding",
        agents=["产品经理", "架构师", "开发工程师", "测试工程师", "部署工程师"],
    )
    svc.save_code(project_id, code)

    return {
        "architecture": architecture,
        "code": code,
        "test_report": test_report,
        "deployment_plan": deployment_plan,
    }


# ── 完整流程（同步 /develop 调用）────────────────────────────────────────────

def run_full_workflow(requirement: str) -> dict:
    """
    运行完整流程：PM → Architect → Dev → Test → DevOps（不等待用户 approval）。
    返回包含所有产出的 dict。
    """
    # 1. PM
    pm_result = run_pm_only(requirement)
    spec = pm_result["spec"]
    project_id = pm_result["project_id"]

    # 2. 全流程
    skill_context = build_skill_context(requirement)
    workflow_result = run_approve_workflow(project_id, spec, skill_context)

    return {
        "project_id": project_id,
        "name": pm_result["name"],
        "requirement": requirement,
        "spec": spec,
        "architecture": workflow_result["architecture"],
        "code": workflow_result["code"],
        "test_report": workflow_result["test_report"],
        "deployment_plan": workflow_result["deployment_plan"],
    }
