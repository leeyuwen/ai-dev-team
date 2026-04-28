from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel, ValidationError
from pydantic_core import PydanticCustomError
from workflow import run_development_workflow, create_development_workflow
import logger
from logger import (
    log_request, log_agent_start, log_agent_complete,
    log_agent_error, log_request_complete, log_error, log_llm_call, get_recent_logs
)
import project_store
import traceback
import json
import os

app = FastAPI(title="AI 开发团队", version="1.0.0")

# Initialize project storage on startup
project_store.init()

# Vue SPA dist — served at /app/, assets at /app/assets/
DIST_DIR = os.path.join(os.path.dirname(__file__), "frontend-vue", "dist")


@app.get("/app/")
async def serve_vue_app():
    path = os.path.join(DIST_DIR, "index.html")
    with open(path, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.get("/app/assets/{path:path}")
async def serve_vue_assets(path: str):
    from starlette.responses import FileResponse
    assets_dir = os.path.join(DIST_DIR, "assets")
    file_path = os.path.join(assets_dir, path)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(file_path)

class PRDRequest(BaseModel):
    requirement: str


class PRDResponse(BaseModel):
    project_id: str
    name: str
    spec: str
    requirement: str


class DevelopmentRequest(BaseModel):
    requirement: str

class DevelopmentResponse(BaseModel):
    project_id: str
    name: str
    requirement: str
    architecture: str
    spec: str
    code: str
    test_report: str
    deployment_plan: str
    history: list

def load_env():
    """Force reload .env file into os.environ before each request."""
    from config import Settings
    s = Settings()
    import os
    if s.ai_provider == "minimax" and s.minimax_api_key:
        os.environ["MINIMAX_API_KEY"] = s.minimax_api_key
    return s


@app.post("/prd", response_model=PRDResponse)
async def generate_prd(request: PRDRequest):
    """仅运行产品经理 Agent，生成 PRD 规格文档，不继续后续流程。"""
    import asyncio, time, uuid
    from concurrent.futures import ThreadPoolExecutor

    request_id = str(uuid.uuid4())[:8]
    logger.logger.info(f"[{request_id}] PRD 请求开始 | 需求: {request.requirement[:50]}...")

    # 创建项目记录
    project = project_store.create_project(request.requirement, agents=["产品经理"])

    def _run():
        t0 = time.time()
        load_env()
        from agents import get_all_agents
        from config import Settings
        s = Settings()
        model_name = getattr(s, 'minimax_model', 'minimax')

        agents_dict = get_all_agents()
        pm_agent = agents_dict["product_manager"]
        pm_chain = pm_agent["prompt"] | pm_agent["llm"]

        logger.logger.info(f"[{request_id}] [产品经理] 初始化完成，准备调用 LLM")
        log_agent_start(f"产品经理 [{request_id}]")

        result = pm_chain.invoke({"requirement": request.requirement})
        elapsed = int((time.time() - t0) * 1000)

        content = result.content if hasattr(result, 'content') else str(result)
        log_agent_complete(f"产品经理 [{request_id}]", content)
        log_llm_call(f"产品经理 [{request_id}]", model_name, elapsed, status="OK")

        logger.logger.info(f"[{request_id}] PRD 生成完成，耗时 {elapsed}ms")
        return {"spec": content, "requirement": request.requirement, "project_id": project["id"]}

    try:
        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor(max_workers=2)
        result = await loop.run_in_executor(executor, _run)
        executor.shutdown(wait=False)

        # 持久化 spec 到数据库
        project_store.update_project(project["id"], spec=result["spec"], status="draft")
        logger.logger.info(f"[{request_id}] PRD 请求完成")
        log_request_complete(1)
        return PRDResponse(project_id=project["id"], name=project["name"], spec=result["spec"], requirement=result["requirement"])

    except ValidationError as e:
        log_agent_error(f"产品经理 [{request_id}]", f"ValidationError: {e}", traceback.format_exc())
        raise HTTPException(status_code=422, detail=f"请求数据验证失败: {e}")
    except TimeoutError as e:
        log_agent_error(f"产品经理 [{request_id}]", f"TimeoutError: {e}", traceback.format_exc())
        raise HTTPException(status_code=408, detail="请求超时，请稍后重试")
    except ConnectionError as e:
        log_agent_error(f"产品经理 [{request_id}]", f"ConnectionError: {e}", traceback.format_exc())
        raise HTTPException(status_code=503, detail="外部服务连接失败")
    except Exception as e:
        log_agent_error(f"产品经理 [{request_id}]", f"Unknown error: {e}", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"内部服务器错误: {str(e)}")


@app.post("/develop", response_model=DevelopmentResponse)
async def develop(request: DevelopmentRequest):
    import asyncio
    from concurrent.futures import ThreadPoolExecutor

    # 创建项目并关联需求
    project = project_store.create_project(request.requirement, agents=["产品经理", "架构师", "开发工程师", "测试工程师", "部署工程师"])

    async def _run():
        load_env()
        return run_development_workflow(request.requirement)

    try:
        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor(max_workers=2)
        result = await loop.run_in_executor(executor, _run)
        executor.shutdown(wait=False)

        # 持久化所有产出到数据库
        project_store.update_project(project["id"],
            spec=result.get("spec", ""),
            architecture=result.get("architecture", ""),
            test_report=result.get("test_report", ""),
            deployment_plan=result.get("deployment_plan", ""),
            status="coding",
        )
        # 保存代码到文件系统
        if result.get("code"):
            project_store.save_code(project["id"], result["code"])

        log_request_complete(len(result.get("history", [])))
        return DevelopmentResponse(
            project_id=project["id"],
            name=project["name"],
            requirement=result["requirement"],
            architecture=result.get("architecture", ""),
            spec=result["spec"],
            code=result["code"],
            test_report=result["test_report"],
            deployment_plan=result["deployment_plan"],
            history=result["history"]
        )
    except ValidationError as e:
        log_error(f"ValidationError: {e}", traceback.format_exc())
        raise HTTPException(status_code=422, detail=f"请求数据验证失败: {e}")
    except TimeoutError as e:
        log_error(f"TimeoutError: {e}", traceback.format_exc())
        raise HTTPException(status_code=408, detail="请求超时，请稍后重试")
    except ConnectionError as e:
        log_error(f"ConnectionError: {e}", traceback.format_exc())
        raise HTTPException(status_code=503, detail="外部服务连接失败")
    except Exception as e:
        log_error(f"Unknown error: {e}", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"内部服务器错误: {str(e)}")

@app.post("/develop/stream")
async def develop_stream(request: DevelopmentRequest):
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers=4)

    async def event_generator():
        load_env()
        from agents import get_all_agents
        from skill_manager import build_skill_context

        agents_dict = get_all_agents()
        skill_context = build_skill_context(request.requirement)
        log_request(request.requirement)

        async def send_event(event_type, data, done=False):
            yield f"event: {event_type}\ndata: {json.dumps({'type': event_type, 'data': data, 'done': done}, ensure_ascii=False)}\n\n"

        yield f"event: status\ndata: {json.dumps({'type': 'status', 'data': '开始处理请求...', 'done': False}, ensure_ascii=False)}\n\n"

        try:
            pm_agent = agents_dict["product_manager"]
            pm_chain = pm_agent["prompt"] | pm_agent["llm"]
            status_msg = '产品经理正在分析需求...'
            yield f"event: status\ndata: {json.dumps({'type': 'status', 'data': status_msg, 'done': False}, ensure_ascii=False)}\n\n"
            log_agent_start("产品经理")

            spec_result = await loop.run_in_executor(executor, lambda: pm_chain.invoke({"requirement": request.requirement}))
            log_agent_complete("产品经理", spec_result.content)

            # 持久化 spec 到数据库
            project = project_store.create_project(request.requirement, agents=["产品经理"])
            project_store.update_project(project["id"], spec=spec_result.content, status="draft")

            yield f"event: product_manager\ndata: {json.dumps({'type': 'product_manager', 'data': spec_result.content, 'project_id': project['id'], 'name': project['name'], 'done': False}, ensure_ascii=False)}\n\n"

            yield f"event: await_approval\ndata: {json.dumps({'type': 'await_approval', 'data': spec_result.content, 'project_id': project['id'], 'name': project['name'], 'skill_context': skill_context, 'done': True}, ensure_ascii=False)}\n\n"

            log_request_complete(1)
            executor.shutdown(wait=False)
            return

        except ValidationError as e:
            log_agent_error("ValidationError", str(e))
            yield f"event: error\ndata: {json.dumps({'type': 'error', 'data': f'请求数据验证失败: {e}', 'done': True}, ensure_ascii=False)}\n\n"
        except TimeoutError as e:
            log_agent_error("TimeoutError", str(e))
            yield f"event: error\ndata: {json.dumps({'type': 'error', 'data': '请求超时，请稍后重试', 'done': True}, ensure_ascii=False)}\n\n"
        except ConnectionError as e:
            log_agent_error("ConnectionError", str(e))
            yield f"event: error\ndata: {json.dumps({'type': 'error', 'data': '外部服务连接失败', 'done': True}, ensure_ascii=False)}\n\n"
        except Exception as e:
            log_agent_error("Unknown error", str(e))
            yield f"event: error\ndata: {json.dumps({'type': 'error', 'data': f'内部服务器错误: {str(e)}', 'done': True}, ensure_ascii=False)}\n\n"
            executor.shutdown(wait=False)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/approve")
async def approve_spec(request: dict):
    """
    用户确认/修改 PRD 后，继续后续 Agent 流程（Architect → Dev → Test → DevOps）。
    request: { "project_id": "...", "spec": "...", "skill_context": "..." }
    """
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    from logger import log_agent_start, log_agent_complete, log_request_complete, log_error

    project_id   = request.get("project_id", "")
    modified_spec = request.get("spec", "")
    skill_context = request.get("skill_context", "")

    if not project_id or not modified_spec:
        raise HTTPException(status_code=400, detail="project_id 和 spec 为必填项")

    proj = project_store.get_project(project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 更新 spec 并标记为 approved
    project_store.update_project(project_id, spec=modified_spec, status="approved")

    async def event_generator():
        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor(max_workers=4)

        async def send_event(event_type, data, done=False):
            yield f"event: {event_type}\ndata: {json.dumps({'type': event_type, 'data': data, 'done': done}, ensure_ascii=False)}\n\n"

        try:
            load_env()
            from agents import get_all_agents
            agents_dict = get_all_agents()

            arch_agent = agents_dict["architect"]
            arch_chain = arch_agent["prompt"] | arch_agent["llm"]
            status_msg = '架构师正在设计系统架构...'
            yield f"event: status\ndata: {json.dumps({'type': 'status', 'data': status_msg, 'done': False}, ensure_ascii=False)}\n\n"
            log_agent_start("架构师")

            arch_result = await loop.run_in_executor(executor, lambda: arch_chain.invoke({
                "requirement": "",
                "spec": modified_spec
            }))
            log_agent_complete("架构师", arch_result.content)

            yield f"event: architect\ndata: {json.dumps({'type': 'architect', 'data': arch_result.content, 'done': False}, ensure_ascii=False)}\n\n"

            dev_agent = agents_dict["developer"]
            dev_chain = dev_agent["prompt"] | dev_agent["llm"]
            status_msg = '开发工程师正在编写代码...'
            yield f"event: status\ndata: {json.dumps({'type': 'status', 'data': status_msg, 'done': False}, ensure_ascii=False)}\n\n"
            log_agent_start("开发工程师")

            code_result = await loop.run_in_executor(executor, lambda: dev_chain.invoke({
                "spec": modified_spec,
                "architecture": arch_result.content,
                "skill_context": skill_context
            }))
            log_agent_complete("开发工程师", code_result.content)

            yield f"event: developer\ndata: {json.dumps({'type': 'developer', 'data': code_result.content, 'done': False}, ensure_ascii=False)}\n\n"

            test_agent = agents_dict["tester"]
            test_chain = test_agent["prompt"] | test_agent["llm"]
            status_msg = '测试工程师正在编写测试用例...'
            yield f"event: status\ndata: {json.dumps({'type': 'status', 'data': status_msg, 'done': False}, ensure_ascii=False)}\n\n"
            log_agent_start("测试工程师")

            test_result = await loop.run_in_executor(executor, lambda: test_chain.invoke({
                "spec": modified_spec,
                "code": code_result.content
            }))
            log_agent_complete("测试工程师", test_result.content)

            yield f"event: tester\ndata: {json.dumps({'type': 'tester', 'data': test_result.content, 'done': False}, ensure_ascii=False)}\n\n"

            devops_agent = agents_dict["devops"]
            devops_chain = devops_agent["prompt"] | devops_agent["llm"]
            status_msg = '部署工程师正在制定部署方案...'
            yield f"event: status\ndata: {json.dumps({'type': 'status', 'data': status_msg, 'done': False}, ensure_ascii=False)}\n\n"
            log_agent_start("部署工程师")

            deploy_result = await loop.run_in_executor(executor, lambda: devops_chain.invoke({
                "code": code_result.content,
                "test_report": test_result.content
            }))
            log_agent_complete("部署工程师", deploy_result.content)

            yield f"event: devops\ndata: {json.dumps({'type': 'devops', 'data': deploy_result.content, 'done': False}, ensure_ascii=False)}\n\n"

            final_result = {
                "spec": modified_spec,
                "architecture": arch_result.content,
                "code": code_result.content,
                "test_report": test_result.content,
                "deployment_plan": deploy_result.content,
            }

            # 持久化所有产出
            project_store.update_project(project_id,
                architecture=arch_result.content,
                code=code_result.content,
                test_report=test_result.content,
                deployment_plan=deploy_result.content,
                status="coding",
            )
            if code_result.content:
                project_store.save_code(project_id, code_result.content)

            yield f"event: complete\ndata: {json.dumps({'type': 'complete', 'data': final_result, 'done': True}, ensure_ascii=False)}\n\n"
            log_request_complete(4)
            executor.shutdown(wait=False)

        except Exception as e:
            log_error(f"Approve error: {e}", traceback.format_exc())
            yield f"event: error\ndata: {json.dumps({'type': 'error', 'data': f'继续流程出错: {str(e)}', 'done': True}, ensure_ascii=False)}\n\n"
            executor.shutdown(wait=False)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/logs")
async def get_logs(lines: int = 100):
    return {"logs": get_recent_logs(lines)}

@app.get("/skills")
async def list_skills():
    """列出所有可用的 Skills"""
    from skill_manager import list_skills, get_skills_for_task
    skills = list_skills()
    return {"skills": skills}


# ── Project storage endpoints ─────────────────────────────────────────────────

@app.get("/projects", response_model=list)
async def list_projects(limit: int = 50, offset: int = 0):
    """列出所有项目（按创建时间倒序）"""
    return project_store.list_projects(limit=limit, offset=offset)


@app.get("/projects/{pid}")
async def get_project(pid: str):
    """获取单个项目详情（含元信息，不含 code）"""
    proj = project_store.get_project(pid)
    if not proj:
        raise HTTPException(status_code=404, detail="项目不存在")
    return proj


@app.get("/projects/{pid}/code")
async def get_project_code(pid: str):
    """获取项目生成的代码内容"""
    code_path = project_store.get_code_path(pid)
    if not code_path:
        raise HTTPException(status_code=404, detail="代码文件不存在")
    if not os.path.exists(code_path):
        raise HTTPException(status_code=404, detail="代码文件丢失")
    with open(code_path, "r", encoding="utf-8") as f:
        content = f.read()
    return {"project_id": pid, "code": content, "path": code_path}


@app.post("/projects/{pid}/approve")
async def approve_and_continue(pid: str, request: dict):
    """
    用户确认 PRD 后，更新 spec 并继续后续 Agent 流程。
    request: { "spec": "...", "skill_context": "..." }
    """
    proj = project_store.get_project(pid)
    if not proj:
        raise HTTPException(status_code=404, detail="项目不存在")

    modified_spec = request.get("spec", "")
    skill_context = request.get("skill_context", "")

    # 更新 spec 和状态
    project_store.update_project(pid, spec=modified_spec, status="approved")

    return {"project_id": pid, "status": "approved", "message": "PRD 已确认，后续流程请使用 /develop/stream?pid=..."}

@app.get("/")
def root():
    return {
        "message": "AI 开发团队服务",
        "version": "1.0.0",
        "endpoints": ["/develop", "/develop/stream", "/logs"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, workers=4, timeout_keep_alive=600)