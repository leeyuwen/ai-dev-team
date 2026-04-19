import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ['PYTHONIOENCODING'] = 'utf-8'

from config import create_llm
from langchain_core.prompts import ChatPromptTemplate

def save_to_file(filename, content):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

def test_agent(agent_name, prompt_template, input_vars, test_input, filename):
    print(f"\n{'=' * 60}")
    print(f"TEST: {agent_name}")
    print(f"{'=' * 60}")

    llm = create_llm("minimax")
    print(f"LLM: {llm.model_name} @ {llm.openai_api_base}")

    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | llm

    print(f"Input variables: {list(input_vars.keys())}")
    print(f"Calling API...")

    result = chain.invoke(input_vars)

    print(f"\nResult:")
    print(f"  Type: {type(result)}")
    print(f"  Length: {len(result.content)} chars")

    save_to_file(filename, result.content)
    print(f"  Saved to: {filename}")

    assert result is not None
    assert hasattr(result, 'content')
    assert len(result.content) > 0

    print(f"\n{'=' * 60}")
    print(f"TEST PASSED!")
    print(f"{'=' * 60}")

    return result.content

if __name__ == "__main__":
    all_results = {}

    try:
        print("\n" + "#" * 60)
        print("# AI Development Team - Unit Tests")
        print("#" * 60)

        print("\n" + "=" * 60)
        print("STEP 1: Product Manager Agent")
        print("=" * 60)

        pm_result = test_agent(
            agent_name="Product Manager",
            prompt_template="""
You are a senior product manager. Create a product specification document for:

Requirement: {requirement}

Output:
1. Product name
2. Core features (3 points)
3. Tech stack suggestions
            """,
            input_vars={"requirement": "Create a simple calculator program"},
            test_input="calculator",
            filename="output_1_product_manager.txt"
        )
        all_results["spec"] = pm_result

        print("\n" + "=" * 60)
        print("STEP 2: Developer Agent")
        print("=" * 60)

        dev_result = test_agent(
            agent_name="Developer",
            prompt_template="""
You are a senior full-stack developer. Implement code based on this specification:

{spec}

Output:
1. Tech stack choice
2. Code implementation
3. Deployment steps
            """,
            input_vars={"spec": pm_result},
            test_input="code",
            filename="output_2_developer.txt"
        )
        all_results["code"] = dev_result

        print("\n" + "=" * 60)
        print("STEP 3: Tester Agent")
        print("=" * 60)

        test_result = test_agent(
            agent_name="Tester",
            prompt_template="""
You are a QA engineer. Create test cases for this implementation:

Specification: {spec}
Code: {code}

Output:
1. Test plan
2. Test cases
3. Expected results
            """,
            input_vars={"spec": pm_result, "code": dev_result},
            test_input="test",
            filename="output_3_tester.txt"
        )
        all_results["test_report"] = test_result

        print("\n" + "=" * 60)
        print("STEP 4: DevOps Agent")
        print("=" * 60)

        devops_result = test_agent(
            agent_name="DevOps",
            prompt_template="""
You are a DevOps engineer. Create deployment plan for:

Code: {code}
Test Report: {test_report}

Output:
1. Deployment architecture
2. CI/CD configuration
3. Monitoring plan
            """,
            input_vars={"code": dev_result, "test_report": test_result},
            test_input="deploy",
            filename="output_4_devops.txt"
        )
        all_results["deployment_plan"] = devops_result

        print("\n" + "#" * 60)
        print("# ALL TESTS PASSED!")
        print("#" * 60)
        print(f"\nOutput files:")
        for key, filename in [
            ("Product Manager", "output_1_product_manager.txt"),
            ("Developer", "output_2_developer.txt"),
            ("Tester", "output_3_tester.txt"),
            ("DevOps", "output_4_devops.txt")
        ]:
            print(f"  - {key}: {filename}")

    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)