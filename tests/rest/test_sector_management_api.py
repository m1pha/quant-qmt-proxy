"""
板块管理接口测试

测试板块创建、添加、移除、重置等接口
"""

import pytest
import httpx
from datetime import datetime


class TestSectorManagementAPI:
    """板块管理接口测试类"""
    
    def test_create_sector_folder(self, http_client: httpx.Client):
        """测试创建板块目录"""
        data = {
            "parent_node": "",  # 空字符串表示"我的"
            "folder_name": f"测试目录_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "overwrite": True
        }
        
        response = http_client.post("/api/v1/data/sector/create-folder", json=data)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("📁 创建板块目录测试:")
        print("="*80)
        print(f"  - 创建的目录名: {result.get('created_name')}")
        print(f"  - 是否成功: {result.get('success')}")
        print(f"  - 消息: {result.get('message')}")
        
        assert 'created_name' in result
        assert result.get('success') is not None
        print("="*80)
    
    def test_create_sector(self, http_client: httpx.Client):
        """测试创建板块"""
        data = {
            "parent_node": "",
            "sector_name": f"测试板块_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "overwrite": True
        }
        
        response = http_client.post("/api/v1/data/sector/create", json=data)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("📊 创建板块测试:")
        print("="*80)
        print(f"  - 创建的板块名: {result.get('created_name')}")
        print(f"  - 是否成功: {result.get('success')}")
        print(f"  - 消息: {result.get('message')}")
        
        assert 'created_name' in result
        print("="*80)
    
    def test_add_sector(self, http_client: httpx.Client, sample_stock_codes):
        """测试添加自定义板块"""
        sector_name = f"测试板块_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        data = {
            "sector_name": sector_name,
            "stock_list": sample_stock_codes[:3]
        }
        
        response = http_client.post("/api/v1/data/sector/add-stocks", json=data)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("➕ 添加板块测试:")
        print("="*80)
        print(f"  - 板块名称: {sector_name}")
        print(f"  - 添加股票数: {len(sample_stock_codes[:3])}")
        print(f"  - 返回结果: {result}")
        
        # 验证返回值
        assert result.get('success') is True or isinstance(result, bool)
        print("="*80)
    
    def test_remove_stock_from_sector(self, http_client: httpx.Client, sample_stock_codes):
        """测试从板块移除成分股"""
        sector_name = f"测试板块_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 先添加板块
        add_data = {
            "sector_name": sector_name,
            "stock_list": sample_stock_codes[:3]
        }
        http_client.post("/api/v1/data/sector/add-stocks", json=add_data)
        
        # 再移除部分股票
        remove_data = {
            "sector_name": sector_name,
            "stock_list": [sample_stock_codes[0]]
        }
        
        response = http_client.post("/api/v1/data/sector/remove-stocks", json=remove_data)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("➖ 移除板块成分股测试:")
        print("="*80)
        print(f"  - 板块名称: {sector_name}")
        print(f"  - 移除股票: {sample_stock_codes[0]}")
        print(f"  - 返回结果: {result}")
        
        assert result.get('success') is True or isinstance(result, bool)
        print("="*80)
    
    def test_reset_sector(self, http_client: httpx.Client, sample_stock_codes):
        """测试重置板块"""
        sector_name = f"测试板块_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 先添加板块
        add_data = {
            "sector_name": sector_name,
            "stock_list": sample_stock_codes[:2]
        }
        http_client.post("/api/v1/data/sector/add-stocks", json=add_data)
        
        # 重置板块（替换成分股）
        reset_data = {
            "sector_name": sector_name,
            "stock_list": sample_stock_codes[2:4]
        }
        
        response = http_client.post("/api/v1/data/sector/reset", json=reset_data)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("🔄 重置板块测试:")
        print("="*80)
        print(f"  - 板块名称: {sector_name}")
        print(f"  - 新股票列表: {sample_stock_codes[2:4]}")
        print(f"  - 返回结果: {result}")
        
        assert result.get('success') is True or isinstance(result, bool)
        print("="*80)
    
    def test_remove_sector(self, http_client: httpx.Client, sample_stock_codes):
        """测试移除板块"""
        sector_name = f"测试板块_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 先添加板块
        add_data = {
            "sector_name": sector_name,
            "stock_list": sample_stock_codes[:2]
        }
        http_client.post("/api/v1/data/sector/add-stocks", json=add_data)
        
        # 移除板块
        response = http_client.delete(f"/api/v1/data/sector/{sector_name}")
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("🗑️ 移除板块测试:")
        print("="*80)
        print(f"  - 板块名称: {sector_name}")
        print(f"  - 返回结果: {result}")
        
        assert result.get('success') is True or isinstance(result, bool)
        print("="*80)
