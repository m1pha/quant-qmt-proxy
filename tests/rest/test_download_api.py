"""
数据下载接口测试

测试历史数据下载、财务数据下载、板块数据下载等接口
"""

import pytest
import httpx
from datetime import datetime, timedelta


class TestDownloadAPI:
    """数据下载接口测试类"""
    
    def test_download_history_data(self, http_client: httpx.Client, sample_stock_codes):
        """测试下载历史行情数据"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        data = {
            "stock_code": sample_stock_codes[0],
            "period": "1d",
            "start_time": start_date.strftime("%Y%m%d"),
            "end_time": end_date.strftime("%Y%m%d"),
            "incrementally": False
        }
        
        response = http_client.post("/api/v1/data/download/history-data", json=data)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("📥 下载历史数据测试:")
        print("="*80)
        print(f"  - 任务ID: {result.get('task_id')}")
        print(f"  - 状态: {result.get('status')}")
        print(f"  - 进度: {result.get('progress')}%")
        print(f"  - 消息: {result.get('message')}")
        
        assert 'task_id' in result
        assert 'status' in result
        assert result['status'] in ['pending', 'running', 'completed', 'failed']
        print("="*80)
    
    def test_download_history_data_batch(self, http_client: httpx.Client, sample_stock_codes):
        """测试批量下载历史数据"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        data = {
            "stock_list": sample_stock_codes[:3],
            "period": "1d",
            "start_time": start_date.strftime("%Y%m%d"),
            "end_time": end_date.strftime("%Y%m%d")
        }
        
        response = http_client.post("/api/v1/data/download/history-data-batch", json=data)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("📥 批量下载历史数据测试:")
        print("="*80)
        print(f"  - 任务ID: {result.get('task_id')}")
        print(f"  - 状态: {result.get('status')}")
        print(f"  - 股票数量: {len(sample_stock_codes[:3])}")
        print(f"  - 消息: {result.get('message')}")
        
        assert 'task_id' in result
        print("="*80)
    
    def test_download_financial_data(self, http_client: httpx.Client, sample_stock_codes):
        """测试下载财务数据"""
        data = {
            "stock_list": sample_stock_codes[:2],
            "table_list": ["Balance", "Income"],
            "start_date": "20230101",
            "end_date": "20231231"
        }
        
        response = http_client.post("/api/v1/data/download/financial-data", json=data)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("📥 下载财务数据测试:")
        print("="*80)
        print(f"  - 任务ID: {result.get('task_id')}")
        print(f"  - 状态: {result.get('status')}")
        print(f"  - 股票数量: {len(sample_stock_codes[:2])}")
        print(f"  - 财务表数量: 2")
        print(f"  - 消息: {result.get('message')}")
        
        assert 'task_id' in result
        assert 'status' in result
        print("="*80)
    
    def test_download_sector_data(self, http_client: httpx.Client):
        """测试下载板块数据"""
        response = http_client.post("/api/v1/data/download/sector-data")
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("📥 下载板块数据测试:")
        print("="*80)
        print(f"  - 任务ID: {result.get('task_id')}")
        print(f"  - 状态: {result.get('status')}")
        print(f"  - 消息: {result.get('message')}")
        
        assert 'task_id' in result
        print("="*80)
    
    def test_download_index_weight(self, http_client: httpx.Client):
        """测试下载指数权重"""
        data = {
            "index_code": "000300.SH"  # 沪深300
        }
        
        response = http_client.post("/api/v1/data/download/index-weight", json=data)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("📥 下载指数权重测试:")
        print("="*80)
        print(f"  - 任务ID: {result.get('task_id')}")
        print(f"  - 状态: {result.get('status')}")
        print(f"  - 消息: {result.get('message')}")
        
        assert 'task_id' in result
        print("="*80)
    
    def test_download_cb_data(self, http_client: httpx.Client):
        """测试下载可转债数据"""
        response = http_client.post("/api/v1/data/download/cb-data")
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("📥 下载可转债数据测试:")
        print("="*80)
        print(f"  - 任务ID: {result.get('task_id')}")
        print(f"  - 状态: {result.get('status')}")
        print(f"  - 消息: {result.get('message')}")
        
        assert 'task_id' in result
        assert 'status' in result
        print("="*80)
    
    def test_download_etf_info(self, http_client: httpx.Client):
        """测试下载ETF申赎清单"""
        response = http_client.post("/api/v1/data/download/etf-info")
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("📥 下载ETF数据测试:")
        print("="*80)
        print(f"  - 任务ID: {result.get('task_id')}")
        print(f"  - 状态: {result.get('status')}")
        print(f"  - 消息: {result.get('message')}")
        
        assert 'task_id' in result
        print("="*80)
    
    def test_download_holiday_data(self, http_client: httpx.Client):
        """测试下载节假日数据"""
        response = http_client.post("/api/v1/data/download/holiday-data")
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("📥 下载节假日数据测试:")
        print("="*80)
        print(f"  - 任务ID: {result.get('task_id')}")
        print(f"  - 状态: {result.get('status')}")
        print(f"  - 消息: {result.get('message')}")
        
        assert 'task_id' in result
        print("="*80)
