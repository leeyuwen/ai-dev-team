import requests
import json

def get_logs(lines=50):
    try:
        response = requests.get(f"http://localhost:8000/logs?lines={lines}")
        if response.status_code == 200:
            data = response.json()
            return data.get("logs", "")
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Connection failed: {e}"

if __name__ == "__main__":
    print("=" * 60)
    print("AI 开发团队 - 后端日志")
    print("=" * 60)
    print()
    logs = get_logs(50)
    print(logs if logs else "暂无日志")
    print()
    print("-" * 60)
    print("提示: 也可以直接在浏览器访问 http://localhost:8000/logs?lines=100 查看完整日志")
    print("或者查看日志文件: logs/ai_team_*.log")