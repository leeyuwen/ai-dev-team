import requests
import json
import os

url = "http://localhost:8000/develop/stream"
payload = {
    "requirement": "创建一个简单的计算器程序"
}

print("=" * 60)
print("Generating Full Project with AI Development Team")
print("=" * 60)

output_dir = "generated_project"
os.makedirs(output_dir, exist_ok=True)

try:
    response = requests.post(url, json=payload, stream=True, timeout=600)

    result_data = {
        "spec": "",
        "code": "",
        "test_report": "",
        "deployment_plan": ""
    }

    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                data_str = line[6:]
                try:
                    data = json.loads(data_str)
                    if data["type"] == "product_manager":
                        result_data["spec"] = data["data"]
                        print("Product Manager: DONE")
                    elif data["type"] == "developer":
                        result_data["code"] = data["data"]
                        print("Developer: DONE")
                    elif data["type"] == "tester":
                        result_data["test_report"] = data["data"]
                        print("Tester: DONE")
                    elif data["type"] == "devops":
                        result_data["deployment_plan"] = data["data"]
                        print("DevOps: DONE")
                except:
                    pass

    print("\n" + "=" * 60)
    print("Saving Results...")
    print("=" * 60)

    spec = result_data["spec"]
    code = result_data["code"]
    test_report = result_data["test_report"]
    deployment = result_data["deployment_plan"]

    spec_clean = spec.replace("<think>", "").replace("</think>", "").strip() if spec else ""
    code_clean = code.replace("<think>", "").replace("</think>", "").strip() if code else ""
    test_clean = test_report.replace("<think>", "").replace("</think>", "").strip() if test_report else ""
    deploy_clean = deployment.replace("<think>", "").replace("</think>", "").strip() if deployment else ""

    with open(f"{output_dir}/SPEC.md", "w", encoding="utf-8") as f:
        f.write("# 产品规格文档\n\n")
        f.write(spec_clean)

    print(f"Saved: {output_dir}/SPEC.md")

    html_start = code_clean.find("```html")
    html_end = code_clean.find("```", html_start + 6) + 3 if html_start != -1 else -1

    css_start = code_clean.find("```css")
    css_end = code_clean.find("```", css_start + 5) + 3 if css_start != -1 else -1

    js_start = code_clean.find("```javascript")
    js_end = code_clean.find("```", js_start + 14) + 3 if js_start != -1 else -1

    if html_start != -1 and html_end != -1:
        with open(f"{output_dir}/index.html", "w", encoding="utf-8") as f:
            f.write(code_clean[html_start+7:html_end-3].strip())
        print(f"Saved: {output_dir}/index.html")

    if css_start != -1 and css_end != -1:
        with open(f"{output_dir}/styles.css", "w", encoding="utf-8") as f:
            f.write(code_clean[css_start+6:css_end-3].strip())
        print(f"Saved: {output_dir}/styles.css")

    if js_start != -1 and js_end != -1:
        with open(f"{output_dir}/script.js", "w", encoding="utf-8") as f:
            f.write(code_clean[js_start+15:js_end-3].strip())
        print(f"Saved: {output_dir}/script.js")

    with open(f"{output_dir}/TEST_REPORT.md", "w", encoding="utf-8") as f:
        f.write("# 测试报告\n\n")
        f.write(test_clean)

    print(f"Saved: {output_dir}/TEST_REPORT.md")

    with open(f"{output_dir}/DEPLOYMENT.md", "w", encoding="utf-8") as f:
        f.write("# 部署文档\n\n")
        f.write(deploy_clean)

    print(f"Saved: {output_dir}/DEPLOYMENT.md")

    with open(f"{output_dir}/README.md", "w", encoding="utf-8") as f:
        f.write("""# CalcMate - 计算器项目

这是一个由 AI 开发团队自动生成的项目。

## 项目结构

```
generated_project/
  index.html      # 主页面
  styles.css      # 样式文件
  script.js       # 脚本文件
  SPEC.md         # 产品规格文档
  TEST_REPORT.md  # 测试报告
  DEPLOYMENT.md   # 部署文档
  README.md       # 本文件
```

## 运行方式

1. 直接在浏览器打开 `index.html`
2. 或使用 Live Server 等本地服务器

## AI 开发团队

本项目由以下 AI Agent 协作生成：
- 产品经理: 需求分析、规格文档
- 开发工程师: 代码实现
- 测试工程师: 测试用例
- 部署工程师: 部署方案
""")

    print(f"Saved: {output_dir}/README.md")

    print("\n" + "=" * 60)
    print("PROJECT GENERATED SUCCESSFULLY!")
    print("=" * 60)
    print(f"\nOutput directory: {output_dir}/")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()