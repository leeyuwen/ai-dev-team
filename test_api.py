from config import create_llm, Settings
import sys
import os

os.environ['PYTHONIOENCODING'] = 'utf-8'

def test_api():
    settings = Settings()
    print(f"Current Provider: {settings.ai_provider}")
    print(f"Model: {settings.minimax_model if settings.ai_provider == 'minimax' else settings.openai_model}")
    print(f"Base URL: {settings.minimax_base_url if settings.ai_provider == 'minimax' else 'N/A'}")
    print(f"Temperature: {settings.temperature}")
    print()

    try:
        print("Testing API connection...")
        llm = create_llm()

        messages = [{"role": "user", "content": "Hello, please introduce yourself briefly."}]
        response = llm.invoke(messages)

        print("SUCCESS: API connection successful!")
        print(f"\nModel response:")
        print(str(response.content))
        return True

    except Exception as e:
        print(f"FAILED: API connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_api()
    sys.exit(0 if success else 1)