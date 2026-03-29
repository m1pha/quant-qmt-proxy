#!/usr/bin/env python3
"""
新项目工具测试脚本模板

使用方法：
1. 将此脚本复制到新项目的 scripts/ 目录
2. 根据实际工具名称修改测试用例
3. 运行测试：python scripts/test_tools.py
"""
import os
import sys
import json
from pathlib import Path

# 加载环境变量
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def print_result(tool_name, result, error=None):
    """打印测试结果"""
    print(f"\n{'='*60}")
    print(f"测试工具: {tool_name}")
    print(f"{'='*60}")
    
    if error:
        print(f"❌ 失败: {error}")
        return False
    else:
        print(f"✅ 成功")
        try:
            data = json.loads(result)
            print(f"返回数据预览:")
            preview = json.dumps(data, ensure_ascii=False, indent=2)[:500]
            print(preview)
            return True
        except:
            print(f"返回数据预览:")
            print(result[:500])
            return True


def test_rest_client():
    """测试 REST 客户端"""
    print("\n" + "="*60)
    print("测试 REST 客户端")
    print("="*60)
    
    try:
        from api.rest_client import get_rest_client
        
        client = get_rest_client()
        print(f"✅ REST 客户端初始化成功")
        print(f"   Base URL: {client.base_url}")
        return True
    except Exception as e:
        print(f"❌ REST 客户端初始化失败: {str(e)}")
        return False


def test_quote_tools():
    """测试行情工具"""
    success = True
    
    try:
        from tools.quote_tools import query_quote
        
        # 测试查询行情
        result = query_quote.func(symbol="TSLA")
        if not print_result("query_quote", result):
            success = False
    except Exception as e:
        print_result("query_quote", None, str(e))
        success = False
    
    return success


def test_account_tools():
    """测试账户工具"""
    success = True
    
    try:
        from tools.account_tools import get_balance
        
        result = get_balance.func()
        if not print_result("get_balance", result):
            success = False
    except Exception as e:
        print_result("get_balance", None, str(e))
        success = False
    
    return success


def test_trade_tools():
    """测试交易工具（模拟）"""
    print("\n" + "="*60)
    print("测试交易工具")
    print("="*60)
    
    print("⚠️  注意：交易工具需要实际测试环境")
    print("   建议在测试账户中验证")
    
    # 可以添加模拟测试
    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("开始运行工具测试")
    print("="*60)
    
    results = {
        "REST 客户端": test_rest_client(),
        "行情工具": test_quote_tools(),
        "账户工具": test_account_tools(),
        "交易工具": test_trade_tools(),
    }
    
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    for name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 所有测试通过！")
    else:
        print("\n⚠️  部分测试失败，请检查错误日志")
    
    return all_passed


if __name__ == "__main__":
    run_all_tests()
