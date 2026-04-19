import requests
import json

url = "http://localhost:8000/develop"
payload = {
    "requirement": "创建一个简单的计算器程序"
}

print("Testing AI Development Team API...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, ensure_ascii=False)}")
print()

try:
    response = requests.post(url, json=payload, timeout=300)
    print(f"Status Code: {response.status_code}")
    print()

    if response.status_code == 200:
        result = response.json()
        print("=" * 60)
        print("RESULT:")
        print("=" * 60)
        print(f"\n[Requirement]\n{result.get('requirement', 'N/A')}")
        print(f"\n[Product Spec]\n{result.get('spec', 'N/A')[:1000]}...")
        print(f"\n[Code]\n{result.get('code', 'N/A')[:1000]}...")
        print(f"\n[Test Report]\n{result.get('test_report', 'N/A')[:500]}...")
        print(f"\n[Deployment Plan]\n{result.get('deployment_plan', 'N/A')[:500]}...")
        print(f"\n[History Items]: {len(result.get('history', []))}")
    else:
        print(f"Error: {response.text}")

except Exception as e:
    print(f"Request failed: {e}")