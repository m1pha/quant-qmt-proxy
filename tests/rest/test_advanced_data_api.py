"""
高级数据接口测试

测试除权数据、全推数据、本地数据、IPO信息等高级接口
"""

import pytest
import httpx
from datetime import datetime, timedelta


class TestAdvancedDataAPI:
    """高级数据接口测试类"""
    
    def test_get_divid_factors(self, http_client: httpx.Client, sample_stock_codes):
        """测试获取除权除息数据"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        data = {
            "stock_code": sample_stock_codes[0],
            "start_time": start_date.strftime("%Y%m%d"),
            "end_time": end_date.strftime("%Y%m%d")
        }
        
        response = http_client.post("/api/v1/data/divid-factors", json=data)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("💰 除权除息数据测试:")
        print("="*80)
        
        if isinstance(result, list):
            print(f"  - 除权记录数: {len(result)}")
            if len(result) > 0:
                first_record = result[0]
                print(f"  - 首条记录时间: {first_record.get('time')}")
                print(f"  - 现金红利: {first_record.get('interest')}")
                print(f"  - 送股比例: {first_record.get('stock_bonus')}")
                print(f"  - 转增比例: {first_record.get('stock_gift')}")
        
        print("="*80)
    
    def test_get_full_tick(self, http_client: httpx.Client, sample_stock_codes):
        """测试获取全推tick数据"""
        data = {
            "stock_codes": sample_stock_codes[:2]
        }
        
        response = http_client.post("/api/v1/data/full-tick", json=data)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("⚡ 全推tick数据测试:")
        print("="*80)
        
        assert isinstance(result, dict), "返回结果应为字典"
        
        for stock_code in sample_stock_codes[:2]:
            if stock_code in result:
                tick_data = result[stock_code]
                print(f"\n股票代码: {stock_code}")
                
                if isinstance(tick_data, list) and len(tick_data) > 0:
                    first_tick = tick_data[0]
                    print(f"  - 最新价: {first_tick.get('last_price')}")
                    print(f"  - 成交量: {first_tick.get('volume')}")
                    print(f"  - 时间: {first_tick.get('time')}")
                    
                    # 验证必需字段
                    assert 'last_price' in first_tick
                    assert 'time' in first_tick
        
        print("="*80)
    
    def test_get_local_data(self, http_client: httpx.Client, sample_stock_codes):
        """测试获取本地行情数据"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        data = {
            "stock_codes": sample_stock_codes[:1],
            "period": "1d",
            "start_time": start_date.strftime("%Y%m%d"),
            "end_time": end_date.strftime("%Y%m%d"),
            "fields": ["time", "open", "high", "low", "close", "volume"]
        }
        
        response = http_client.post("/api/v1/data/local-data", json=data)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("💾 本地行情数据测试:")
        print("="*80)
        
        if isinstance(result, list) and len(result) > 0:
            first_result = result[0]
            print(f"  - 股票代码: {first_result.get('stock_code')}")
            print(f"  - 数据条数: {len(first_result.get('data', []))}")
            print(f"  - 周期: {first_result.get('period')}")
        
        print("="*80)
    
    def test_get_full_kline(self, http_client: httpx.Client, sample_stock_codes):
        """测试获取最新交易日K线"""
        data = {
            "stock_codes": sample_stock_codes[:2],
            "period": "1d",
            "fields": ["time", "open", "high", "low", "close", "volume"]
        }
        
        response = http_client.post("/api/v1/data/full-kline", json=data)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("📊 最新交易日K线测试:")
        print("="*80)
        
        if isinstance(result, list):
            print(f"  - 返回股票数: {len(result)}")
            for item in result:
                print(f"  - 股票: {item.get('stock_code')}, 数据条数: {len(item.get('data', []))}")
        
        print("="*80)
    
    def test_get_ipo_info(self, http_client: httpx.Client):
        """测试获取IPO信息"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        params = {
            "start_time": start_date.strftime("%Y%m%d"),
            "end_time": end_date.strftime("%Y%m%d")
        }
        
        response = http_client.get("/api/v1/data/ipo-info", params=params)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("🆕 IPO信息测试:")
        print("="*80)
        
        if isinstance(result, list):
            print(f"  - IPO记录数: {len(result)}")
            if len(result) > 0:
                first_ipo = result[0]
                print(f"  - 首个新股代码: {first_ipo.get('security_code')}")
                print(f"  - 股票名称: {first_ipo.get('code_name')}")
                print(f"  - 发行价: {first_ipo.get('publish_price')}")
                print(f"  - 申购日期: {first_ipo.get('subscribe_date')}")
        
        print("="*80)
    
    def test_get_cb_info(self, http_client: httpx.Client):
        """测试获取可转债信息"""
        response = http_client.get("/api/v1/data/convertible-bonds")
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("🔄 可转债信息测试:")
        print("="*80)
        
        if isinstance(result, list):
            print(f"  - 可转债数量: {len(result)}")
            if len(result) > 0:
                first_cb = result[0]
                print(f"  - 首个转债代码: {first_cb.get('bond_code')}")
                print(f"  - 转债名称: {first_cb.get('bond_name')}")
                print(f"  - 正股代码: {first_cb.get('stock_code')}")
                print(f"  - 转股价: {first_cb.get('conversion_price')}")
        
        print("="*80)
    
    def test_get_holidays(self, http_client: httpx.Client):
        """测试获取节假日数据"""
        response = http_client.get("/api/v1/data/holidays")
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("🎉 节假日数据测试:")
        print("="*80)
        
        if isinstance(result, dict) and 'holidays' in result:
            holidays = result['holidays']
            print(f"  - 节假日数量: {len(holidays)}")
            if len(holidays) > 0:
                print(f"  - 前5个节假日: {holidays[:5]}")
        
        print("="*80)
    
    def test_get_period_list(self, http_client: httpx.Client):
        """测试获取可用周期列表"""
        response = http_client.get("/api/v1/data/period-list")
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("📅 可用周期列表测试:")
        print("="*80)
        
        if isinstance(result, dict) and 'periods' in result:
            periods = result['periods']
            print(f"  - 可用周期数: {len(periods)}")
            print(f"  - 周期列表: {periods}")
            
            # 验证常见周期
            expected_periods = ['tick', '1m', '5m', '1d']
            for period in expected_periods:
                if period in periods:
                    print(f"  - ✓ 包含周期: {period}")
        
        print("="*80)
    
    def test_get_instrument_type(self, http_client: httpx.Client, sample_stock_codes):
        """测试获取合约类型"""
        stock_code = sample_stock_codes[0]
        
        response = http_client.get(f"/api/v1/data/instrument-type/{stock_code}")
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("🏷️ 合约类型测试:")
        print("="*80)
        print(f"  - 股票代码: {result.get('stock_code')}")
        print(f"  - 是否股票: {result.get('stock')}")
        print(f"  - 是否指数: {result.get('index')}")
        print(f"  - 是否基金: {result.get('fund')}")
        print(f"  - 是否ETF: {result.get('etf')}")
        print(f"  - 是否债券: {result.get('bond')}")
        print(f"  - 是否期权: {result.get('option')}")
        print(f"  - 是否期货: {result.get('futures')}")
        
        # 验证至少有一个类型为True
        type_flags = [
            result.get('stock'), result.get('index'), result.get('fund'),
            result.get('etf'), result.get('bond'), result.get('option'), result.get('futures')
        ]
        assert any(type_flags), "至少应该有一个类型为True"
        
        print("="*80)
    
    def test_get_data_dir(self, http_client: httpx.Client):
        """测试获取数据目录"""
        response = http_client.get("/api/v1/data/data-dir")
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("📂 数据目录测试:")
        print("="*80)
        print(f"  - 数据路径: {result.get('data_dir')}")
        
        assert 'data_dir' in result
        assert isinstance(result['data_dir'], str)
        
        print("="*80)
