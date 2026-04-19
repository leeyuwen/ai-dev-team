from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ValidationError
from pydantic_core import PydanticCustomError
from workflow import run_development_workflow, create_development_workflow
from logger import (
    log_request, log_agent_start, log_agent_complete,
    log_agent_error, log_request_complete, log_error, get_recent_logs
)
import traceback
import json

app = FastAPI(
    title="AI 开发团队",
    version="1.0.0"
)

class DevelopmentRequest(BaseModel):
    requirement: str

class DevelopmentResponse(BaseModel):
    requirement: str
    spec: str
    code: str
    test_report: str
    deployment_plan: str
    history: list

@app.post("/develop", response_model=DevelopmentResponse)
async def develop(request: DevelopmentRequest):
    try:
        log_request(request.requirement)
        result = run_development_workflow(request.requirement)
        log_request_complete(len(result.get("history", [])))
        return DevelopmentResponse(
            requirement=result["requirement"],
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
    async def event_generator():
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

            spec_result = pm_chain.invoke({"requirement": request.requirement})
            log_agent_complete("产品经理", spec_result.content)

            yield f"event: product_manager\ndata: {json.dumps({'type': 'product_manager', 'data': spec_result.content, 'done': False}, ensure_ascii=False)}\n\n"

            dev_agent = agents_dict["developer"]
            dev_chain = dev_agent["prompt"] | dev_agent["llm"]
            status_msg = '开发工程师正在编写代码...'
            yield f"event: status\ndata: {json.dumps({'type': 'status', 'data': status_msg, 'done': False}, ensure_ascii=False)}\n\n"
            log_agent_start("开发工程师")

            code_result = dev_chain.invoke({"spec": spec_result.content})
            log_agent_complete("开发工程师", code_result.content)

            yield f"event: developer\ndata: {json.dumps({'type': 'developer', 'data': code_result.content, 'done': False}, ensure_ascii=False)}\n\n"

            test_agent = agents_dict["tester"]
            test_chain = test_agent["prompt"] | test_agent["llm"]
            status_msg = '测试工程师正在编写测试用例...'
            yield f"event: status\ndata: {json.dumps({'type': 'status', 'data': status_msg, 'done': False}, ensure_ascii=False)}\n\n"
            log_agent_start("测试工程师")

            test_result = test_chain.invoke({"spec": spec_result.content, "code": code_result.content})
            log_agent_complete("测试工程师", test_result.content)

            yield f"event: tester\ndata: {json.dumps({'type': 'tester', 'data': test_result.content, 'done': False}, ensure_ascii=False)}\n\n"

            devops_agent = agents_dict["devops"]
            devops_chain = devops_agent["prompt"] | devops_agent["llm"]
            status_msg = '部署工程师正在制定部署方案...'
            yield f"event: status\ndata: {json.dumps({'type': 'status', 'data': status_msg, 'done': False}, ensure_ascii=False)}\n\n"
            log_agent_start("部署工程师")

            deploy_result = devops_chain.invoke({"code": code_result.content, "test_report": test_result.content})
            log_agent_complete("部署工程师", deploy_result.content)

            yield f"event: devops\ndata: {json.dumps({'type': 'devops', 'data': deploy_result.content, 'done': False}, ensure_ascii=False)}\n\n"

            final_result = {
                "requirement": request.requirement,
                "spec": spec_result.content,
                "code": code_result.content,
                "test_report": test_result.content,
                "deployment_plan": deploy_result.content,
                "history": [
                    f"产品经理: {spec_result.content}",
                    f"开发工程师: {code_result.content}",
                    f"测试工程师: {test_result.content}",
                    f"部署工程师: {deploy_result.content}"
                ]
            }

            yield f"event: status\ndata: {json.dumps({'type': 'status', 'data': '开发完成!', 'done': False}, ensure_ascii=False)}\n\n"
            yield f"event: complete\ndata: {json.dumps({'type': 'complete', 'data': final_result, 'done': True}, ensure_ascii=False)}\n\n"

            log_request_complete(4)

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
    uvicorn.run(app, host="0.0.0.0", port=8000)