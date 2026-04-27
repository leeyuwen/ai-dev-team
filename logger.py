import logging
import os
from datetime import datetime
from pathlib import Path

log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

log_file = log_dir / f"ai_team_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("AI_Team")

def log_request(requirement: str):
    logger.info(f"=" * 60)
    logger.info(f"新请求开始 | 需求: {requirement[:100]}...")

def log_agent_start(agent_name: str):
    logger.info(f"[{agent_name}] 开始执行")

def log_agent_complete(agent_name: str, content_preview: str = ""):
    preview = content_preview[:200].replace("\n", " ") + "..." if len(content_preview) > 200 else content_preview.replace("\n", " ")
    logger.info(f"[{agent_name}] 完成 | 预览: {preview}")

def log_agent_error(agent_name: str, error: str, traceback_text: str = ""):
    logger.error(f"[{agent_name}] 错误: {error}")
    if traceback_text:
        for line in traceback_text.strip().splitlines()[-5:]:
            logger.error(f"  └ {line}")

def log_llm_call(agent_name: str, model: str, duration_ms: int, tokens: int = 0, status: str = "OK"):
    logger.info(f"[LLM] [{agent_name}] 调用 | 模型: {model} | 耗时: {duration_ms}ms | tokens: {tokens} | 状态: {status}")

def log_request_complete(history_count: int):
    logger.info(f"请求完成 | 共 {history_count} 个Agent参与")

def log_error(error: str, traceback: str = ""):
    logger.error(f"系统错误: {error}")
    if traceback:
        logger.error(f"堆栈: {traceback}")

def get_recent_logs(lines: int = 100) -> str:
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            return ''.join(all_lines[-lines:])
    except Exception as e:
        return f"读取日志失败: {e}"

def get_log_file_path() -> str:
    return str(log_file)