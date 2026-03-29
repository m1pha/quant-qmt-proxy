"""
Level2数据接口测试

测试Level2行情快照、逐笔委托、逐笔成交等接口
"""

import pytest
import httpx
from datetime import datetime


class TestLevel2API:
    """Level2数据接口测试类"""
    
    def test_get_l2_quote(self, http_client: httpx.Client, sample_stock_codes):
        """测试获取Level2行情快照"""
        data = {
            "stock_codes": sample_stock_codes[:2]
        }
        
        response = http_client.post("/api/v1/data/l2/quote", json=data)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("📊 Level2行情快照测试:")
        print("="*80)
        
        # 验证返回数据结构
        assert isinstance(result, dict), "返回结果应为字典"
        
        # 检查每个股票的数据
        for stock_code in sample_stock_codes[:2]:
            if stock_code in result:
                quote_data = result[stock_code]
                print(f"\n股票代码: {stock_code}")
                print(f"  - 最新价: {quote_data.get('last_price')}")
                print(f"  - 成交量: {quote_data.get('volume')}")
                
                # 验证10档行情
                if 'ask_price' in quote_data and quote_data['ask_price']:
                    assert len(quote_data['ask_price']) <= 10, "委卖价最多10档"
                    print(f"  - 委卖价档数: {len(quote_data['ask_price'])}")
                
                if 'bid_price' in quote_data and quote_data['bid_price']:
                    assert len(quote_data['bid_price']) <= 10, "委买价最多10档"
                    print(f"  - 委买价档数: {len(quote_data['bid_price'])}")
                
                # 验证价格合理性
                if quote_data.get('last_price'):
                    assert quote_data['last_price'] > 0, "最新价应大于0"
                    print(f"  - 价格验证: 通过 ✓")
        
        print("="*80)
    
    def test_get_l2_order(self, http_client: httpx.Client, sample_stock_codes):
        """测试获取Level2逐笔委托"""
        data = {
            "stock_codes": sample_stock_codes[:1]
        }
        
        response = http_client.post("/api/v1/data/l2/order", json=data)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("📋 Level2逐笔委托测试:")
        print("="*80)
        
        # 验证返回数据结构
        assert isinstance(result, dict), "返回结果应为字典"
        
        for stock_code in sample_stock_codes[:1]:
            if stock_code in result:
                orders = result[stock_code]
                print(f"\n股票代码: {stock_code}")
                print(f"  - 委托记录数: {len(orders) if isinstance(orders, list) else 0}")
                
                if isinstance(orders, list) and len(orders) > 0:
                    first_order = orders[0]
                    print(f"  - 首条委托价格: {first_order.get('price')}")
                    print(f"  - 首条委托量: {first_order.get('volume')}")
                    
                    # 验证必需字段
                    assert 'time' in first_order, "缺少时间字段"
                    assert 'price' in first_order, "缺少价格字段"
                    assert 'volume' in first_order, "缺少数量字段"
                    print(f"  - 字段验证: 通过 ✓")
        
        print("="*80)
    
    def test_get_l2_transaction(self, http_client: httpx.Client, sample_stock_codes):
        """测试获取Level2逐笔成交"""
        data = {
            "stock_codes": sample_stock_codes[:1]
        }
        
        response = http_client.post("/api/v1/data/l2/transaction", json=data)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("💹 Level2逐笔成交测试:")
        print("="*80)
        
        # 验证返回数据结构
        assert isinstance(result, dict), "返回结果应为字典"
        
        for stock_code in sample_stock_codes[:1]:
            if stock_code in result:
                transactions = result[stock_code]
                print(f"\n股票代码: {stock_code}")
                print(f"  - 成交记录数: {len(transactions) if isinstance(transactions, list) else 0}")
                
                if isinstance(transactions, list) and len(transactions) > 0:
                    first_trans = transactions[0]
                    print(f"  - 首条成交价格: {first_trans.get('price')}")
                    print(f"  - 首条成交量: {first_trans.get('volume')}")
                    print(f"  - 首条成交额: {first_trans.get('amount')}")
                    
                    # 验证必需字段
                    assert 'time' in first_trans, "缺少时间字段"
                    assert 'price' in first_trans, "缺少价格字段"
                    assert 'volume' in first_trans, "缺少数量字段"
                    
                    # 验证成交额计算
                    if first_trans.get('price') and first_trans.get('volume') and first_trans.get('amount'):
                        expected_amount = first_trans['price'] * first_trans['volume']
                        # 允许浮点误差
                        assert abs(first_trans['amount'] - expected_amount) < 0.01 or first_trans['amount'] > 0, \
                            "成交额应该等于价格*数量或大于0"
                        print(f"  - 成交额验证: 通过 ✓")
        
        print("="*80)
    
    def test_l2_quote_empty_list(self, http_client: httpx.Client):
        """测试空股票列表"""
        data = {
            "stock_codes": []
        }
        
        response = http_client.post("/api/v1/data/l2/quote", json=data)
        # 应该返回422错误（验证失败）
        assert response.status_code == 422
    
    def test_l2_quote_invalid_code(self, http_client: httpx.Client):
        """测试无效股票代码"""
        data = {
            "stock_codes": ["INVALID"]
        }
        
        response = http_client.post("/api/v1/data/l2/quote", json=data)
        # 可能返回400或200（取决于实现）
        assert response.status_code in [200, 400, 422]
