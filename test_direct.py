import sys
sys.path.insert(0, 'g:/PythonProject/New_ai')

from workflow import run_development_workflow
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

print("Testing Development Workflow...")
print("This will call the AI 4 times, please wait...")
print()

try:
    result = run_development_workflow("创建一个简单的计算器程序")

    print("=" * 60)
    print("SUCCESS! Workflow completed!")
    print("=" * 60)

    print(f"\n[Requirement]\n{result.get('requirement', 'N/A')[:200]}")

    spec = result.get('spec', 'N/A')
    print(f"\n[Product Manager Output - Spec]\n{spec[:800]}...")

    code = result.get('code', 'N/A')
    print(f"\n[Developer Output - Code]\n{code[:800]}...")

    test_report = result.get('test_report', 'N/A')
    print(f"\n[Tester Output - Test Report]\n{test_report[:400]}...")

    deployment = result.get('deployment_plan', 'N/A')
    print(f"\n[DevOps Output - Deployment Plan]\n{deployment[:400]}...")

    print(f"\n[Total History Items]: {len(result.get('history', []))}")
    print("\nAll 4 agents completed successfully!")

except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()