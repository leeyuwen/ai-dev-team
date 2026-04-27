from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel, ValidationError
from pydantic_core import PydanticCustomError
from workflow import run_development_workflow, create_development_workflow
from logger import (
    log_request, log_agent_start, log_agent_complete,
    log_agent_error, log_request_complete, log_error, get_recent_logs
)
import traceback
import json
import os

app = FastAPI(title="AI 开发团队", version="1.0.0")

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
    spec: str
    requirement: str


class DevelopmentRequest(BaseModel):
    requirement: str

class DevelopmentResponse(BaseModel):
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
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    from logger import log_agent_start, log_agent_complete, log_request_complete, log_error

    def _run():
        load_env()
        from agents import get_all_agents
        agents_dict = get_all_agents()
        pm_agent = agents_dict["product_manager"]
        pm_chain = pm_agent["prompt"] | pm_agent["llm"]
        log_agent_start("产品经理")
        result = pm_chain.invoke({"requirement": request.requirement})
        log_agent_complete("产品经理", result.content)
        return {"spec": result.content, "requirement": request.requirement}

    try:
        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor(max_workers=2)
        result = await loop.run_in_executor(executor, _run)
        executor.shutdown(wait=False)
        log_request_complete(1)
        return PRDResponse(spec=result["spec"], requirement=result["requirement"])
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


@app.post("/develop", response_model=DevelopmentResponse)
async def develop(request: DevelopmentRequest):
    import asyncio
    from concurrent.futures import ThreadPoolExecutor

    async def _run():
        load_env()
        return run_development_workflow(request.requirement)

    try:
        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor(max_workers=2)
        result = await loop.run_in_executor(executor, _run)
        executor.shutdown(wait=False)
        log_request_complete(len(result.get("history", [])))
        return DevelopmentResponse(
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

        agents_dict = get_all_agents()
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

            yield f"event: product_manager\ndata: {json.dumps({'type': 'product_manager', 'data': spec_result.content, 'done': False}, ensure_ascii=False)}\n\n"

            yield f"event: await_approval\ndata: {json.dumps({'type': 'await_approval', 'data': spec_result.content, 'done': True}, ensure_ascii=False)}\n\n"

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
    """用户确认/修改 PRD 后，继续后续 Agent 流程（Architect → Dev → Test → DevOps）"""
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    from logger import log_agent_start, log_agent_complete, log_request_complete, log_error

    session_id = request.get("session_id", "default")
    modified_spec = request.get("spec", "")

    if not session_id or not modified_spec:
        raise HTTPException(status_code=400, detail="session_id 和 spec 为必填项")

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
                "architecture": arch_result.content
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