"""
快速检查服务是否可用
"""
import httpx
import sys

def check_service():
    """检查服务状态"""
    base_url = "http://localhost:8000"
    api_key = "dev-api-key-001"
    
    print("=" * 80)
    print("检查服务状态...")
    print("=" * 80)
    
    # 1. 检查健康端点（不需要API密钥）
    try:
        print(f"\n[1] 检查健康端点: {base_url}/health")
        response = httpx.get(f"{base_url}/health", timeout=5.0)
        print(f"   状态码: {response.status_code}")
        try:
            print(f"   响应: {response.json()}")
        except:
            print(f"   响应文本: {response.text}")
        if response.status_code == 200:
            print("   [OK] 健康检查通过")
        else:
            print("   [FAIL] 健康检查失败")
    except httpx.ConnectError as e:
        print(f"   [FAIL] 连接失败: {e}")
        print("\n[提示] 可能的原因:")
        print("   1. 服务未启动")
        print("   2. 端口不是 8000")
        print("   3. 服务启动失败（检查另一个终端的错误信息）")
        sys.exit(1)
    except Exception as e:
        print(f"   [FAIL] 请求失败: {e}")
        sys.exit(1)
    
    # 2. 检查根路径
    try:
        print(f"\n[2] 检查根路径: {base_url}/")
        response = httpx.get(f"{base_url}/", timeout=5.0)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print("   [OK] 根路径访问成功")
    except Exception as e:
        print(f"   [FAIL] 请求失败: {e}")
    
    # 3. 检查需要API密钥的端点
    try:
        print(f"\n[3] 检查API密钥认证: {base_url}/api/v1/data/sectors")
        headers = {"X-API-Key": api_key}
        response = httpx.get(f"{base_url}/api/v1/data/sectors", headers=headers, timeout=5.0)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print("   [OK] API密钥认证成功")
            result = response.json()
            print(f"   响应数据类型: {type(result)}")
        elif response.status_code == 401:
            print("   [FAIL] API密钥认证失败")
        else:
            print(f"   [WARN] 未预期的状态码: {response.status_code}")
    except Exception as e:
        print(f"   [FAIL] 请求失败: {e}")
    
    print("\n" + "=" * 80)
    print("[完成] 服务检查完成！")
    print("=" * 80)
    print("\n[提示] 如果所有检查都通过，可以运行测试:")
    print("   pytest tests/rest/ -v")
    print("\n[提示] 如果健康检查失败，请检查:")
    print("   1. 另一个终端中 python run.py 的输出")
    print("   2. 是否有错误信息（特别是 xtdata 连接错误）")
    print("   3. QMT 是否正在运行")
    print("=" * 80)

if __name__ == "__main__":
    check_service()
