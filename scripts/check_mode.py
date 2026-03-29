"""
检查当前运行模式
"""
import httpx

def check_mode():
    base_url = "http://localhost:8000"
    
    try:
        # 检查根路径，会显示运行模式
        response = httpx.get(f"{base_url}/", timeout=5.0)
        print(f"状态码: {response.status_code}")
        print(f"响应内容:\n{response.text}")
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    check_mode()
