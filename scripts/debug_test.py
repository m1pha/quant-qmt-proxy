"""
调试测试配置问题
"""
import httpx
import sys

def test_connection():
    print("=" * 80)
    print("测试HTTP连接配置")
    print("=" * 80)
    
    base_url = "http://localhost:8000"
    api_key = "dev-api-key-001"
    
    # 测试1: 不带认证头
    print("\n[测试1] 不带认证头访问 /health/")
    try:
        client = httpx.Client(base_url=base_url, timeout=5.0)
        response = client.get("/health/")
        print(f"  状态码: {response.status_code}")
        print(f"  响应: {response.json()}")
    except Exception as e:
        print(f"  错误: {type(e).__name__}: {e}")
    
    # 测试2: 使用 X-API-Key 认证头
    print("\n[测试2] 使用 X-API-Key 认证头访问 /health/")
    try:
        headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
        client = httpx.Client(base_url=base_url, headers=headers, timeout=5.0)
        response = client.get("/health/")
        print(f"  状态码: {response.status_code}")
        print(f"  响应: {response.json()}")
    except Exception as e:
        print(f"  错误: {type(e).__name__}: {e}")
    
    # 测试3: 使用 Bearer Token 认证头
    print("\n[测试3] 使用 Bearer Token 认证头访问 /health/")
    try:
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        client = httpx.Client(base_url=base_url, headers=headers, timeout=5.0)
        response = client.get("/health/")
        print(f"  状态码: {response.status_code}")
        print(f"  响应: {response.json()}")
    except Exception as e:
        print(f"  错误: {type(e).__name__}: {e}")
    
    # 测试4: 访问需要认证的端点
    print("\n[测试4] 使用 X-API-Key 访问 /api/v1/data/sectors")
    try:
        headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
        client = httpx.Client(base_url=base_url, headers=headers, timeout=5.0)
        response = client.get("/api/v1/data/sectors")
        print(f"  状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  响应类型: {type(data)}")
            if isinstance(data, list):
                print(f"  数据条数: {len(data)}")
        else:
            print(f"  响应: {response.text[:200]}")
    except Exception as e:
        print(f"  错误: {type(e).__name__}: {e}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_connection()
