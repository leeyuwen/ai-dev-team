import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ['PYTHONIOENCODING'] = 'utf-8'

from config import create_llm
from langchain_core.prompts import ChatPromptTemplate

def test_product_manager_direct():
    print("=" * 60)
    print("TEST: Product Manager Direct Call")
    print("=" * 60)

    llm = create_llm("minimax")
    print(f"LLM Config:")
    print(f"  - Model: {llm.model_name}")
    print(f"  - API Base: {llm.openai_api_base}")

    prompt = ChatPromptTemplate.from_template("""
    You are a senior product manager. Please create a product spec document based on the following requirement:

    Requirement: {requirement}

    Please output briefly:
    1. Product name
    2. Core features (3 points)
    3. Tech stack suggestions
    """)

    chain = prompt | llm

    print("\nCalling MiniMax API...")

    result = chain.invoke({"requirement": "Create a simple calculator program"})

    print(f"\nResult:")
    print(f"  Type: {type(result)}")
    print(f"  Content length: {len(result.content)} chars")

    content_for_log = f"  Content:\n{result.content}"
    with open("test_output.txt", "w", encoding="utf-8") as f:
        f.write(content_for_log)
    print("  Content saved to test_output.txt")

    assert result is not None
    assert hasattr(result, 'content')
    assert len(result.content) > 0

    print("\n" + "=" * 60)
    print("TEST PASSED!")
    print("=" * 60)

    return result.content

if __name__ == "__main__":
    try:
        test_product_manager_direct()
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)