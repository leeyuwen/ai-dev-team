"""
AI 开发团队 — FastAPI 路由层（app.py）

只负责：HTTP 请求/响应、参数校验、调用 services 层。

目录结构:
  app.py              ← HTTP 入口（本文件）
  services/
    project.py        ← 数据访问层
    workflow.py       ← Agent 编排逻辑
  agents.py           ← Agent prompts
  workflow.py         ← LangGraph workflow（保留，暂未集成）
  project_store.py    ← 旧版存储（保留兼容，逐步迁移）
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel
import json, os, traceback

from logger import log_agent_error, get_recent_logs
from services import ProjectService
from services.workflow import run_pm_only, run_approve_workflow, run_full_workflow
import project_store  # 保留兼容，临时

# ── app init ─────────────────────────────────────────────────────────────────

app = FastAPI(title="AI 开发团队", version="2.0.0")

# 确保存储初始化
project_store.init()

# ── request/response models ─────────────────────────────────────────────────

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


# ── 辅助 ─────────────────────────────────────────────────────────────────────

def load_env():
    from config import Settings
    s = Settings()
    if s.ai_provider == "minimax" and s.minimax_api_key:
        os.environ["MINIMAX_API_KEY"] = s.minimax_api_key


# ── 路由 ─────────────────────────────────────────────────────────────────────

@app.post("/prd", response_model=PRDResponse)
async def generate_prd(request: PRDRequest):
    """仅运行产品经理 Agent，生成 PRD 规格文档，不继续后续流程。"""
    try:
        result = run_pm_only(request.requirement)
        return PRDResponse(**result)
    except Exception as e:
        log_agent_error("产品经理", str(e), traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"内部错误: {str(e)}")


@app.post("/develop", response_model=DevelopmentResponse)
async def develop(request: DevelopmentRequest):
    """运行完整开发流程（PM → Architect → Dev → Test → DevOps），同步返回所有产出。"""
    try:
        result = run_full_workflow(request.requirement)
        return DevelopmentResponse(
            project_id=result["project_id"],
            name=result["name"],
            requirement=result["requirement"],
            architecture=result["architecture"],
            spec=result["spec"],
            code=result["code"],
            test_report=result["test_report"],
            deployment_plan=result["deployment_plan"],
            history=[],  # 暂未实现 history 追踪
        )
    except Exception as e:
        log_agent_error("开发流程", str(e), traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"内部错误: {str(e)}")


@app.post("/develop/stream")
async def develop_stream(request: DevelopmentRequest):
    """
    流式开发流程：PM 阶段逐 token 流式返回，用户实时看到 PRD 生成过程。
    完成 后等待用户 approval 继续后续 Agent 流程。
    """
    load_env()
    from skill_manager import build_skill_context
    from services.workflow import stream_pm_only

    async def event_generator():
        try:
            import asyncio
            from concurrent.futures import ThreadPoolExecutor
            loop = asyncio.get_event_loop()
            executor = ThreadPoolExecutor(max_workers=2)

            skill_context = build_skill_context(request.requirement)

            # PM 阶段：流式返回（不过滤 thinking，用户实时看到思考过程）
            spec_text = ""
            project_id = None
            project_name = None

            for token, is_done, result in stream_pm_only(request.requirement):
                if token:
                    spec_text += token
                    yield f"event: pm_token\ndata: {json.dumps({'type': 'pm_token', 'token': token}, ensure_ascii=False)}\n\n"
                if is_done and result:
                    project_id = result["project_id"]
                    project_name = result["name"]
                    # 过滤存储用的 spec（用户已看到完整 thinking，无需再过滤）
                    project_store.update_project(project_id, spec=spec_text, status="draft")

            yield f"event: product_manager\ndata: {json.dumps({'type': 'product_manager', 'data': spec_text, 'project_id': project_id, 'name': project_name, 'done': False}, ensure_ascii=False)}\n\n"
            yield f"event: await_approval\ndata: {json.dumps({'type': 'await_approval', 'data': spec_text, 'project_id': project_id, 'name': project_name, 'skill_context': skill_context, 'done': True}, ensure_ascii=False)}\n\n"

        except Exception as e:
            log_agent_error("PM 阶段", str(e), traceback.format_exc())
            yield f"event: error\ndata: {json.dumps({'type': 'error', 'data': str(e), 'done': True}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/approve")
async def approve_spec(request: dict):
    """
    用户确认 PRD 后，继续 Architect → Dev → Test → DevOps 全流程。
    request: { "project_id": "...", "spec": "...", "skill_context": "..." }
    """
    project_id = request.get("project_id", "")
    spec = request.get("spec", "")
    skill_context = request.get("skill_context", "")

    if not project_id or not spec:
        raise HTTPException(status_code=400, detail="project_id 和 spec 为必填项")

    proj = project_store.get_project(project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="项目不存在")

    project_store.update_project(project_id, spec=spec, status="approved")

    async def event_generator():
        try:
            import asyncio
            from concurrent.futures import ThreadPoolExecutor
            loop = asyncio.get_event_loop()
            executor = ThreadPoolExecutor(max_workers=2)

            result = await loop.run_in_executor(
                executor,
                lambda: run_approve_workflow(project_id, spec, skill_context),
            )
            executor.shutdown(wait=False)

            final_result = {
                "spec": spec,
                "architecture": result["architecture"],
                "code": result["code"],
                "test_report": result["test_report"],
                "deployment_plan": result["deployment_plan"],
            }

            yield f"event: complete\ndata: {json.dumps({'type': 'complete', 'data': final_result, 'done': True}, ensure_ascii=False)}\n\n"

        except Exception as e:
            log_agent_error("Approval 流程", str(e), traceback.format_exc())
            yield f"event: error\ndata: {json.dumps({'type': 'error', 'data': str(e), 'done': True}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ── 项目管理 ─────────────────────────────────────────────────────────────────

@app.get("/projects")
async def list_projects(limit: int = 50, offset: int = 0):
    return project_store.list_projects(limit=limit, offset=offset)

@app.get("/projects/{pid}")
async def get_project(pid: str):
    proj = project_store.get_project(pid)
    if not proj:
        raise HTTPException(status_code=404, detail="项目不存在")
    return proj

@app.get("/projects/{pid}/code")
async def get_project_code(pid: str):
    code_path = project_store.get_code_path(pid)
    if not code_path:
        raise HTTPException(status_code=404, detail="代码文件不存在")
    if not os.path.exists(code_path):
        raise HTTPException(status_code=404, detail="代码文件丢失")
    with open(code_path, "r", encoding="utf-8") as f:
        content = f.read()
    return {"project_id": pid, "code": content, "path": code_path}

@app.post("/projects/{pid}/approve")
async def approve_project(pid: str, request: dict):
    """仅更新项目状态，不触发 workflow。"""
    proj = project_store.get_project(pid)
    if not proj:
        raise HTTPException(status_code=404, detail="项目不存在")
    spec = request.get("spec", proj.get("spec", ""))
    project_store.update_project(pid, spec=spec, status="approved")
    return {"project_id": pid, "status": "approved"}


# ── 其他 ─────────────────────────────────────────────────────────────────────

@app.get("/skills")
async def list_skills():
    from skill_manager import list_skills
    return {"skills": list_skills()}

@app.get("/")
def root():
    return {
        "message": "AI 开发团队服务",
        "version": "2.0.0",
        "endpoints": ["/", "/prd", "/develop", "/develop/stream", "/approve", "/projects", "/projects/{pid}", "/projects/{pid}/code"],
    }

@app.get("/logs")
def get_logs():
    logs = get_recent_logs(100)
    return {"logs": logs}

# ── Vue SPA ─────────────────────────────────────────────────────────────────

DIST_DIR = os.path.join(os.path.dirname(__file__), "frontend-vue", "dist")

@app.get("/app")
async def serve_app():
    index = os.path.join(DIST_DIR, "index.html")
    if os.path.exists(index):
        return HTMLResponse(open(index).read())
    return {"error": "Frontend not built. Run: cd frontend-vue && npm install && npm run build"}

@app.get("/app/assets/{path:path}")
async def serve_assets(path: str):
    from fastapi.responses import FileResponse
    file_path = os.path.join(DIST_DIR, "assets", path)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return HTTPException(status_code=404, detail="Asset not found")

# ── uvicorn 入口 ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, workers=1, timeout_keep_alive=600)
