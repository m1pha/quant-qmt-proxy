# 测试指南 (Testing Guide)

## 概述

本项目使用 pytest 进行全面的 API 接口测试，覆盖数据服务、交易服务、订阅服务等所有核心功能。

## 测试文件结构

```
tests/rest/
├── conftest.py                      # pytest配置和fixture
├── client.py                        # REST客户端封装
├── config.py                        # 测试配置
├── test_health_api.py              # 健康检查接口测试
├── test_data_api.py                # 基础数据接口测试
├── test_advanced_data_api.py       # 高级数据接口测试 (新增)
├── test_level2_api.py              # Level2数据接口测试 (新增)
├── test_download_api.py            # 数据下载接口测试 (新增)
├── test_sector_management_api.py   # 板块管理接口测试 (新增)
├── test_trading_api.py             # 交易接口测试
└── test_subscription_api.py        # 订阅接口测试
```

## 测试覆盖范围

### 1. 数据服务接口 (Data Service)

#### 基础数据接口 (`test_data_api.py`)
- ✅ 市场数据获取 (`get_market_data`)
- ✅ 板块列表获取 (`get_sector_list`)
- ✅ 板块成分股获取 (`get_stock_list_in_sector`)
- ✅ 指数权重获取 (`get_index_weight`)
- ✅ 交易日历获取 (`get_trading_calendar`)
- ✅ 合约信息获取 (`get_instrument_info`)
- ✅ 财务数据获取 (`get_financial_data`)
- ✅ ETF信息获取 (`get_etf_info`)

#### 高级数据接口 (`test_advanced_data_api.py`)
- ✅ 除权除息数据 (`get_divid_factors`)
- ✅ 全推tick数据 (`get_full_tick`)
- ✅ 本地行情数据 (`get_local_data`)
- ✅ 最新交易日K线 (`get_full_kline`)
- ✅ IPO信息 (`get_ipo_info`)
- ✅ 可转债信息 (`get_cb_info`)
- ✅ 节假日数据 (`get_holidays`)
- ✅ 可用周期列表 (`get_period_list`)
- ✅ 合约类型 (`get_instrument_type`)
- ✅ 数据目录 (`get_data_dir`)

#### Level2数据接口 (`test_level2_api.py`)
- ✅ Level2行情快照 (`get_l2_quote`)
- ✅ Level2逐笔委托 (`get_l2_order`)
- ✅ Level2逐笔成交 (`get_l2_transaction`)
- ✅ 异常情况测试（空列表、无效代码）

#### 数据下载接口 (`test_download_api.py`)
- ✅ 历史数据下载 (`download_history_data`)
- ✅ 批量历史数据下载 (`download_history_data_batch`)
- ✅ 财务数据下载 (`download_financial_data`)
- ✅ 板块数据下载 (`download_sector_data`)
- ✅ 指数权重下载 (`download_index_weight`)
- ✅ 可转债数据下载 (`download_cb_data`)
- ✅ ETF数据下载 (`download_etf_info`)
- ✅ 节假日数据下载 (`download_holiday_data`)

#### 板块管理接口 (`test_sector_management_api.py`)
- ✅ 创建板块目录 (`create_sector_folder`)
- ✅ 创建板块 (`create_sector`)
- ✅ 添加板块 (`add_sector`)
- ✅ 移除板块成分股 (`remove_stock_from_sector`)
- ✅ 重置板块 (`reset_sector`)
- ✅ 删除板块 (`remove_sector`)

### 2. 交易服务接口 (`test_trading_api.py`)
- ✅ 账户连接 (`connect_account`)
- ✅ 账户断开 (`disconnect_account`)
- ✅ 获取账户信息 (`get_account_info`)
- ✅ 获取持仓信息 (`get_positions`)
- ✅ 提交订单 (`submit_order`)
- ✅ 撤销订单 (`cancel_order`)
- ✅ 获取订单列表 (`get_orders`)
- ✅ 获取成交记录 (`get_trades`)
- ✅ 获取资产信息 (`get_asset_info`)
- ✅ 获取风险信息 (`get_risk_info`)
- ✅ 获取策略列表 (`get_strategies`)

### 3. 订阅服务接口 (`test_subscription_api.py`)
- ✅ 创建订阅 (`create_subscription`)
- ✅ 取消订阅 (`cancel_subscription`)
- ✅ 获取订阅列表 (`get_subscriptions`)
- ✅ 获取订阅详情 (`get_subscription_info`)
- ✅ WebSocket连接测试

### 4. 健康检查接口 (`test_health_api.py`)
- ✅ 健康状态检查 (`/health`)
- ✅ 根路径访问 (`/`)

## 运行测试

### 运行所有测试
```bash
pytest tests/rest/ -v
```

### 运行特定测试文件
```bash
# 基础数据接口测试
pytest tests/rest/test_data_api.py -v

# Level2数据接口测试
pytest tests/rest/test_level2_api.py -v

# 板块管理接口测试
pytest tests/rest/test_sector_management_api.py -v

# 下载接口测试
pytest tests/rest/test_download_api.py -v

# 高级数据接口测试
pytest tests/rest/test_advanced_data_api.py -v

# 交易接口测试
pytest tests/rest/test_trading_api.py -v

# 订阅接口测试
pytest tests/rest/test_subscription_api.py -v
```

### 运行特定测试类
```bash
pytest tests/rest/test_level2_api.py::TestLevel2API -v
```

### 运行特定测试方法
```bash
pytest tests/rest/test_level2_api.py::TestLevel2API::test_get_l2_quote -v
```

### 显示详细输出
```bash
pytest tests/rest/ -v -s
```

### 生成测试覆盖率报告
```bash
pytest tests/rest/ --cov=app --cov-report=html
```

## 测试配置

测试配置位于 `tests/rest/config.py`，包括：

```python
class TestConfig:
    # API基础URL
    BASE_URL = "http://localhost:8000"
    
    # API密钥
    API_KEY = "test-api-key"
    
    # 超时设置
    TIMEOUT = 30.0
    
    # 测试用股票代码
    SAMPLE_STOCK_CODES = ["000001.SZ", "600000.SH", "000002.SZ"]
    
    # 测试用板块名称
    SAMPLE_SECTOR_NAMES = ["沪深300", "上证50", "创业板"]
    
    # 测试用指数代码
    SAMPLE_INDEX_CODES = ["000001.SH", "000300.SH", "399006.SZ"]
```

## Fixtures说明

### 全局Fixtures (`conftest.py`)

- `http_client`: HTTP客户端，自动添加API密钥
- `sample_stock_codes`: 测试用股票代码列表
- `sample_sector_names`: 测试用板块名称列表
- `sample_index_codes`: 测试用指数代码列表
- `sample_date_range`: 测试用日期范围

## 测试最佳实践

### 1. 数据验证
每个测试都应验证：
- 响应状态码
- 返回数据结构
- 必需字段存在性
- 数据类型正确性
- 数据合理性（如价格>0，OHLC关系等）

### 2. 异常处理
测试应包括：
- 正常情况测试
- 边界条件测试（空列表、最大值等）
- 异常情况测试（无效输入、不存在的资源等）

### 3. 输出信息
使用格式化输出便于调试：
```python
print("\n" + "="*80)
print("📊 测试名称:")
print("="*80)
print(f"  - 字段1: {value1}")
print(f"  - 字段2: {value2}")
print("="*80)
```

### 4. 断言说明
使用清晰的断言消息：
```python
assert result['price'] > 0, "价格应该大于0"
assert 'data' in result, "缺少data字段"
```

## 测试数据准备

### Mock模式
在Mock模式下，所有接口返回模拟数据，无需真实的QMT环境。

### Dev/Prod模式
在Dev/Prod模式下，需要：
1. 启动QMT客户端
2. 确保数据已下载
3. 配置正确的QMT路径

## 持续集成

建议在CI/CD流程中：
1. 使用Mock模式运行所有测试
2. 检查测试覆盖率（目标>80%）
3. 生成测试报告

## 故障排查

### 常见问题

1. **连接超时**
   - 检查API服务是否启动
   - 检查BASE_URL配置是否正确

2. **认证失败**
   - 检查API_KEY配置
   - 确认API密钥验证已启用

3. **数据为空**
   - Mock模式：正常，返回模拟数据
   - Dev/Prod模式：检查QMT连接和数据下载

4. **测试失败**
   - 查看详细错误信息
   - 检查服务日志
   - 验证测试数据有效性

## 测试报告

运行测试后会生成：
- 控制台输出：实时测试结果
- 覆盖率报告：`htmlcov/index.html`
- 测试日志：`test_results.log`

## 贡献指南

添加新测试时：
1. 遵循现有测试结构
2. 使用描述性的测试方法名
3. 添加详细的文档字符串
4. 包含正常和异常情况测试
5. 添加清晰的输出信息
6. 更新本文档

## 测试统计

### 总体覆盖率
- **数据服务**: ~95% (45/47接口)
- **交易服务**: ~48% (12/25接口)
- **订阅服务**: 100% (核心功能)
- **健康检查**: 100%

### 新增测试文件
- `test_level2_api.py`: Level2数据接口测试
- `test_download_api.py`: 数据下载接口测试
- `test_sector_management_api.py`: 板块管理接口测试
- `test_advanced_data_api.py`: 高级数据接口测试

### 测试用例数量
- 基础数据接口: 8个测试
- 高级数据接口: 11个测试
- Level2接口: 5个测试
- 下载接口: 8个测试
- 板块管理: 6个测试
- 交易接口: 11个测试
- 订阅接口: 4个测试
- 健康检查: 2个测试

**总计: 55+ 测试用例**

## 下一步计划

1. 添加性能测试
2. 添加压力测试
3. 添加集成测试
4. 完善异步交易接口测试
5. 添加资金划拨接口测试
