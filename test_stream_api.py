import requests
import json
import time

url = "http://localhost:8000/develop/stream"
payload = {
    "requirement": "创建一个简单的计算器程序"
}

print("=" * 60)
print("Testing Full Workflow with Streaming API")
print("=" * 60)
print(f"\nRequirement: {payload['requirement']}")
print("\nStarting...")

start_time = time.time()
event_count = 0

try:
    response = requests.post(url, json=payload, stream=True, timeout=600)

    print(f"\nStatus Code: {response.status_code}\n")

    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            print(f"SSE: {line[:100]}...")
            event_count += 1

    elapsed = time.time() - start_time
    print(f"\n{'=' * 60}")
    print(f"COMPLETED!")
    print(f"Total time: {elapsed:.1f} seconds")
    print(f"Total events: {event_count}")
    print(f"{'=' * 60}")

except requests.exceptions.Timeout:
    print(f"\nTIMEOUT after {time.time() - start_time:.1f} seconds")
except requests.exceptions.ConnectionError as e:
    print(f"\nCONNECTION ERROR: {e}")
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()