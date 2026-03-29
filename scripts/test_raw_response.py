"""
测试原始响应内容
"""
import httpx

base_url = "http://localhost:8000"

print("测试 /health/ 端点")
print("=" * 80)

try:
    response = httpx.get(f"{base_url}/health/", timeout=5.0)
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print(f"响应文本: {response.text}")
    print(f"响应字节: {response.content}")
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
