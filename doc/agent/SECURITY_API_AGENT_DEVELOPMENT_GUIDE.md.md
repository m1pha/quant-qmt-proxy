# 证券 API 智能体开发经验总结

> 基于 LongPort 项目的实战经验，为证券 API 项目提供开发指南和提示词模板。

---

## 目录

1. [项目架构设计](#项目架构设计)
2. [工具定义模式](#工具定义模式)
3. [REST API 封装](#rest-api-封装)
4. [gRPC 接口封装](#grpc-接口封装)
5. [参数处理与类型转换](#参数处理与类型转换)
6. [错误处理最佳实践](#错误处理最佳实践)
7. [智能推断与容错](#智能推断与容错)
8. [系统提示词编写](#系统提示词编写)
9. [用户手册模板](#用户手册模板)
10. [测试验证流程](#测试验证流程)
11. [常见问题与解决方案](#常见问题与解决方案)

---

## 项目架构设计

### 推荐目录结构

```
project/
├── src/
│   ├── agents/
│   │   └── agent.py              # Agent 主逻辑
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── quote_tools.py        # 行情工具
│   │   ├── trade_tools.py        # 交易工具
│   │   └── account_tools.py      # 账户工具
│   ├── api/
│   │   ├── __init__.py
│   │   ├── rest_client.py        # REST API 客户端
│   │   ├── grpc_client.py        # gRPC 客户端
│   │   └── auth.py               # 认证模块
│   ├── models/
│   │   ├── __init__.py
│   │   ├── enums.py              # 枚举定义
│   │   └── schemas.py            # 数据模型
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── cache.py              # 缓存工具
│   │   └── helpers.py            # 辅助函数
│   ├── storage/
│   │   └── memory/
│   │       └── memory_saver.py   # 记忆管理
│   └── main.py                   # 入口文件
├── config/
│   └── agent_llm_config.json     # LLM 配置
├── docs/
│   ├── USER_MANUAL.md            # 用户手册
│   └── API_REFERENCE.md          # API 参考
├── tests/
│   └── test_tools.py             # 工具测试
├── .env                          # 环境变量
├── requirements.txt              # 依赖
└── README.md
```

### 模块职责

| 模块 | 职责 |
|------|------|
| `agents/` | Agent 构建和配置 |
| `tools/` | LangChain 工具定义 |
| `api/` | REST/gRPC 客户端封装 |
| `models/` | 数据模型和枚举 |
| `utils/` | 工具函数 |
| `storage/` | 记忆持久化 |

---

## 工具定义模式

### 基础模板

```python
from langchain.tools import tool, ToolRuntime
from langchain_core.exceptions import LangChainException
from coze_coding_utils.runtime_ctx.context import new_context
from typing import Optional
import json

@tool
def query_stock_quote(symbol: str, runtime: ToolRuntime = None) -> str:
    """
    查询股票实时行情。
    
    参数：
        symbol: 股票代码，支持格式：TSLA、700.HK、600036.SH
    
    返回：
        JSON 格式的行情数据
    """
    ctx = runtime.context if runtime else new_context(method="query_stock_quote")
    
    try:
        # 1. 参数验证
        if not symbol or not symbol.strip():
            raise LangChainException("股票代码不能为空")
        
        # 2. 参数预处理
        symbol = symbol.strip().upper()
        
        # 3. 调用 API
        client = get_rest_client()
        response = client.get_quote(symbol)
        
        # 4. 处理响应
        result = {
            "symbol": response.get("symbol"),
            "price": float(response.get("price", 0)),
            "change": float(response.get("change", 0)),
            "volume": int(response.get("volume", 0)),
        }
        
        # 5. 返回 JSON
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except LangChainException:
        raise
    except Exception as e:
        error_msg = f"查询行情失败: {str(e)}"
        if "not found" in str(e).lower():
            error_msg = f"股票代码无效: {symbol}"
        raise LangChainException(error_msg)
```

### 关键要点

1. **必须有文档字符串**：描述功能、参数、返回值
2. **参数必须有类型注解**：便于 LangChain 生成工具描述
3. **返回 JSON 字符串**：便于大模型理解和展示
4. **使用 LangChainException**：统一的异常处理
5. **runtime 参数**：支持上下文传递（可选）

---

## REST API 封装

### REST 客户端基类

```python
import os
import requests
from typing import Optional, Dict, Any
from functools import lru_cache

class RESTClient:
    """REST API 客户端基类"""
    
    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30
    ):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or os.getenv("API_KEY")
        self.timeout = timeout
        self.session = requests.Session()
        
        # 设置默认请求头
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        
        if self.api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}"
            })
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """发送请求"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            raise Exception("请求超时，请稍后重试")
        except requests.exceptions.ConnectionError:
            raise Exception("网络连接失败，请检查网络")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise Exception("认证失败，请检查 API Key")
            elif e.response.status_code == 404:
                raise Exception(f"资源不存在: {endpoint}")
            elif e.response.status_code == 429:
                raise Exception("请求频率超限，请稍后重试")
            else:
                try:
                    error_data = e.response.json()
                    raise Exception(error_data.get("message", str(e)))
                except:
                    raise Exception(str(e))
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """GET 请求"""
        return self._request("GET", endpoint, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """POST 请求"""
        return self._request("POST", endpoint, data=data)
    
    def put(self, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """PUT 请求"""
        return self._request("PUT", endpoint, data=data)
    
    def delete(self, endpoint: str) -> Dict:
        """DELETE 请求"""
        return self._request("DELETE", endpoint)


# 缓存客户端实例
@lru_cache(maxsize=1)
def get_rest_client() -> RESTClient:
    """获取 REST 客户端实例"""
    base_url = os.getenv("API_BASE_URL")
    api_key = os.getenv("API_KEY")
    
    if not base_url:
        raise ValueError("未配置 API_BASE_URL 环境变量")
    
    return RESTClient(base_url=base_url, api_key=api_key)
```

### 使用示例

```python
@tool
def get_account_info(runtime: ToolRuntime = None) -> str:
    """查询账户信息"""
    ctx = runtime.context if runtime else new_context(method="get_account_info")
    
    try:
        client = get_rest_client()
        response = client.get("/api/v1/account/info")
        
        result = {
            "account_id": response.get("accountId"),
            "balance": float(response.get("balance", 0)),
            "available": float(response.get("available", 0)),
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        raise LangChainException(f"查询账户信息失败: {str(e)}")
```

---

## gRPC 接口封装

### gRPC 客户端封装

```python
import os
import grpc
from typing import Optional, Any
from functools import lru_cache
from concurrent import futures

# 导入生成的 protobuf 代码
# from proto import quote_pb2
# from proto import quote_pb2_grpc

class GRPCClient:
    """gRPC 客户端封装"""
    
    def __init__(
        self,
        host: str,
        port: int,
        api_key: Optional[str] = None,
        use_ssl: bool = True
    ):
        self.host = host
        self.port = port
        self.api_key = api_key or os.getenv("API_KEY")
        self.use_ssl = use_ssl
        self._channel = None
        self._stubs = {}
    
    @property
    def channel(self):
        """获取 gRPC 通道"""
        if self._channel is None:
            address = f"{self.host}:{self.port}"
            
            if self.use_ssl:
                # 使用 SSL/TLS
                credentials = grpc.ssl_channel_credentials()
                self._channel = grpc.secure_channel(address, credentials)
            else:
                # 不使用 SSL（仅用于开发环境）
                self._channel = grpc.insecure_channel(address)
        
        return self._channel
    
    def get_metadata(self) -> list:
        """获取认证元数据"""
        metadata = []
        if self.api_key:
            metadata.append(("authorization", f"Bearer {self.api_key}"))
        return metadata
    
    def call(self, stub_class, method_name: str, request, timeout: int = 30):
        """
        调用 gRPC 方法
        
        Args:
            stub_class: Stub 类
            method_name: 方法名
            request: 请求对象
            timeout: 超时时间（秒）
        """
        # 获取或创建 stub
        stub_key = stub_class.__name__
        if stub_key not in self._stubs:
            self._stubs[stub_key] = stub_class(self.channel)
        
        stub = self._stubs[stub_key]
        method = getattr(stub, method_name)
        
        try:
            response = method(
                request,
                metadata=self.get_metadata(),
                timeout=timeout
            )
            return response
            
        except grpc.RpcError as e:
            # 处理 gRPC 错误
            if e.code() == grpc.StatusCode.UNAUTHENTICATED:
                raise Exception("认证失败，请检查 API Key")
            elif e.code() == grpc.StatusCode.NOT_FOUND:
                raise Exception("资源不存在")
            elif e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                raise Exception("请求超时")
            elif e.code() == grpc.StatusCode.RESOURCE_EXHAUSTED:
                raise Exception("请求频率超限")
            else:
                raise Exception(f"gRPC 错误: {e.details()}")
    
    def close(self):
        """关闭连接"""
        if self._channel:
            self._channel.close()
            self._channel = None


# 缓存客户端实例
_grpc_client = None

def get_grpc_client() -> GRPCClient:
    """获取 gRPC 客户端实例"""
    global _grpc_client
    
    if _grpc_client is None:
        host = os.getenv("GRPC_HOST")
        port = int(os.getenv("GRPC_PORT", "443"))
        api_key = os.getenv("API_KEY")
        use_ssl = os.getenv("GRPC_USE_SSL", "true").lower() == "true"
        
        if not host:
            raise ValueError("未配置 GRPC_HOST 环境变量")
        
        _grpc_client = GRPCClient(
            host=host,
            port=port,
            api_key=api_key,
            use_ssl=use_ssl
        )
    
    return _grpc_client
```

### gRPC 工具示例

```python
@tool
def get_realtime_quote(symbol: str, runtime: ToolRuntime = None) -> str:
    """通过 gRPC 获取实时行情"""
    ctx = runtime.context if runtime else new_context(method="get_realtime_quote")
    
    try:
        client = get_grpc_client()
        
        # 创建请求
        request = quote_pb2.QuoteRequest(symbol=symbol)
        
        # 调用 gRPC
        response = client.call(
            quote_pb2_grpc.QuoteStub,
            "GetQuote",
            request
        )
        
        # 处理响应
        result = {
            "symbol": response.symbol,
            "price": float(response.price),
            "volume": int(response.volume),
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        raise LangChainException(f"获取实时行情失败: {str(e)}")
```

### Protobuf 文件处理

```python
# 编译 protobuf 文件
# python -m grpc_tools.protoc -I./proto --python_out=./src/proto --grpc_python_out=./src/proto ./proto/*.proto

# 使用示例
# src/proto/
# ├── __init__.py
# ├── quote_pb2.py
# └── quote_pb2_grpc.py
```

---

## 参数处理与类型转换

### 枚举类型定义

```python
from enum import Enum
from typing import Dict, Any

class OrderType(str, Enum):
    """订单类型"""
    LIMIT = "LO"          # 限价单
    MARKET = "MO"         # 市价单
    STOP_LIMIT = "SLO"    # 止损限价单
    STOP_MARKET = "SMO"   # 止损市价单

class OrderSide(str, Enum):
    """交易方向"""
    BUY = "Buy"
    SELL = "Sell"

class TimeInForce(str, Enum):
    """有效期类型"""
    DAY = "Day"
    GTC = "GTC"
    IOC = "IOC"
    FOK = "FOK"


# 枚举映射表（字符串 -> 枚举）
ORDER_TYPE_MAP: Dict[str, OrderType] = {
    "LO": OrderType.LIMIT,
    "LIMIT": OrderType.LIMIT,
    "MO": OrderType.MARKET,
    "MARKET": OrderType.MARKET,
    "SLO": OrderType.STOP_LIMIT,
    "STOP_LIMIT": OrderType.STOP_LIMIT,
}

ORDER_SIDE_MAP: Dict[str, OrderSide] = {
    "Buy": OrderSide.BUY,
    "buy": OrderSide.BUY,
    "BUY": OrderSide.BUY,
    "Sell": OrderSide.SELL,
    "sell": OrderSide.SELL,
    "SELL": OrderSide.SELL,
}
```

### 参数转换函数

```python
from typing import TypeVar, Type, Dict, Any

T = TypeVar('T', bound=Enum)

def str_to_enum(
    value: str,
    enum_map: Dict[str, T],
    field_name: str = "参数"
) -> T:
    """
    字符串转枚举
    
    Args:
        value: 字符串值
        enum_map: 映射表
        field_name: 字段名称（用于错误提示）
    
    Returns:
        枚举值
    
    Raises:
        LangChainException: 转换失败
    """
    if not value:
        raise LangChainException(f"{field_name}不能为空")
    
    if value in enum_map:
        return enum_map[value]
    
    # 支持的值列表
    supported = ", ".join(sorted(set(enum_map.keys())))
    raise LangChainException(
        f"无效的{field_name}: {value}，支持的值: {supported}"
    )


def safe_float(value: Any, default: float = 0.0) -> float:
    """安全转换为浮点数"""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """安全转换为整数"""
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default
```

### 使用示例

```python
@tool
def submit_order(
    symbol: str,
    order_type: str,
    side: str,
    quantity: int,
    price: Optional[float] = None,
    runtime: ToolRuntime = None
) -> str:
    """提交订单"""
    
    # 转换枚举
    order_type_enum = str_to_enum(order_type, ORDER_TYPE_MAP, "订单类型")
    side_enum = str_to_enum(side, ORDER_SIDE_MAP, "交易方向")
    
    # 验证限价单
    if order_type_enum == OrderType.LIMIT and price is None:
        raise LangChainException("限价单必须提供价格参数")
    
    # 调用 API
    client = get_rest_client()
    response = client.post("/api/v1/orders", {
        "symbol": symbol,
        "type": order_type_enum.value,
        "side": side_enum.value,
        "quantity": quantity,
        "price": price
    })
    
    return json.dumps(response, ensure_ascii=False, indent=2)
```

---

## 错误处理最佳实践

### 错误处理中间件

```python
from langchain.agents.middleware import wrap_tool_call
from langchain.messages import ToolMessage

@wrap_tool_call
def handle_tool_errors(request, handler):
    """统一的工具错误处理中间件"""
    try:
        return handler(request)
    except LangChainException as e:
        # 已知的业务错误
        return ToolMessage(
            content=f"❌ {str(e)}",
            tool_call_id=request.tool_call["id"]
        )
    except Exception as e:
        # 未知错误
        error_msg = f"工具执行错误: {str(e)}"
        return ToolMessage(
            content=error_msg,
            tool_call_id=request.tool_call["id"]
        )


# 在 Agent 中使用
agent = create_agent(
    model=llm,
    tools=tools,
    middleware=[handle_tool_errors]
)
```

### 错误消息映射

```python
ERROR_MESSAGES = {
    # 认证相关
    "unauthorized": "认证失败，请检查 API Key 配置",
    "forbidden": "无权限执行此操作",
    "invalid_token": "Token 无效或已过期",
    
    # 资源相关
    "not_found": "资源不存在",
    "symbol_not_found": "股票代码无效",
    "order_not_found": "订单不存在",
    
    # 交易相关
    "insufficient_funds": "资金不足，无法完成交易",
    "insufficient_position": "持仓不足，无法卖出",
    "market_closed": "市场休市，无法交易",
    "price_limit": "价格超出涨跌幅限制",
    
    # 频率限制
    "rate_limit": "请求频率超限，请稍后重试",
    "timeout": "请求超时，请稍后重试",
}

def get_friendly_error(error: Exception) -> str:
    """获取友好的错误提示"""
    error_str = str(error).lower()
    
    for key, message in ERROR_MESSAGES.items():
        if key in error_str:
            return message
    
    return f"操作失败: {str(error)}"
```

---

## 智能推断与容错

### 股票代码智能推断

```python
from functools import lru_cache

# 推断缓存
_symbol_cache = {}

def infer_symbol_suffix(symbol: str) -> str:
    """
    智能推断股票代码后缀
    
    支持:
    - TSLA -> TSLA.US
    - 700 -> 700.HK
    - 600036 -> 600036.SH
    """
    # 检查缓存
    if symbol in _symbol_cache:
        return _symbol_cache[symbol]
    
    # 已有后缀，直接返回
    if '.' in symbol:
        return symbol
    
    # 推断规则
    if symbol.isdigit():
        # 纯数字
        if symbol.startswith('6'):
            full_symbol = f"{symbol}.SH"  # 上海
        elif symbol.startswith(('0', '3')):
            full_symbol = f"{symbol}.SZ"  # 深圳
        else:
            full_symbol = f"{symbol}.HK"  # 港股
    else:
        # 字母开头，默认美股
        full_symbol = f"{symbol}.US"
    
    # 缓存结果
    _symbol_cache[symbol] = full_symbol
    return full_symbol


def normalize_symbols(symbols_str: str) -> list:
    """批量规范化股票代码"""
    symbols = [s.strip() for s in symbols_str.split(',')]
    return [infer_symbol_suffix(s) for s in symbols if s.strip()]
```

### 响应数据规范化

```python
def normalize_response(data: dict) -> dict:
    """规范化 API 响应数据"""
    result = {}
    
    for key, value in data.items():
        # 处理枚举类型
        if hasattr(value, 'value'):
            result[key] = value.value
        # 处理日期时间
        elif hasattr(value, 'isoformat'):
            result[key] = value.isoformat()
        # 处理其他类型
        else:
            result[key] = value
    
    return result
```

---

## 系统提示词编写

### 提示词模板

```python
SYSTEM_PROMPT = """
# 角色定义
你是专业的证券交易助手，基于 [API名称] OpenAPI 提供智能化服务。
你具备专业的金融知识，能够帮助用户进行行情查询、账户管理、交易执行等操作。

# 核心能力

## 1. 行情查询
- 股票实时报价（支持港股、美股、A股）
- K线图表数据
- 深度盘口数据
- 资金流向分析

## 2. 账户管理
- 查询账户余额
- 查询持仓情况
- 查询订单状态

## 3. 交易执行
- 提交买卖订单
- 撤销订单
- 查询成交记录

# 工作流程

1. **理解意图**：分析用户需求，确定需要执行的操作
2. **选择工具**：根据需求选择合适的工具
3. **执行操作**：调用工具完成任务
4. **呈现结果**：以清晰易懂的方式展示结果

# 交易规则

1. **风险提示**：交易前必须提示风险
2. **确认机制**：重要操作需用户确认
3. **参数验证**：严格验证所有参数
4. **错误处理**：提供清晰的错误提示

# 输出格式

- 行情数据：表格 + 关键指标
- 账户信息：结构化展示
- 交易结果：订单ID + 状态

# 约束条件

1. 仅支持已开通的市场和权限
2. 交易时间为各市场交易时段
3. 所有金额单位为对应货币
4. 遵守相关法律法规

# 注意事项

- 查询行情时，支持简化的股票代码（如 TSLA、700）
- 交易时必须使用完整的股票代码格式
- 限价单必须提供价格参数
- 市价单不需要价格参数
"""
```

---

## 用户手册模板

```markdown
# [API名称] 智能助手使用手册

## 概述

本助手对接了 [API名称] OpenAPI，提供 XX 个专业工具，支持行情查询、账户管理、交易执行等功能。

---

## 工具列表

### 1. query_stock_quote - 查询股票实时报价

**功能说明**：查询股票的最新价格、涨跌幅、成交量等实时行情数据

**参数**：
- `symbol`: 股票代码
  - 支持完整格式：`TSLA.US`、`700.HK`
  - 支持简化格式：`TSLA`、`700`（自动推断）

**用户提问示例**：
- "特斯拉现在的股价是多少？"
- "帮我查一下 TSLA 和 AAPL 的股票价格"
- "腾讯今天涨了多少？"

**返回数据示例**：
```json
{
  "symbol": "TSLA.US",
  "price": 398.58,
  "change": -10.12,
  "change_percent": -2.47,
  "volume": 12345678
}
```

**注意事项**：
- 需要订阅相应市场的行情权限
- 查询频率可能有限制

---

### 2. submit_order - 提交订单

...（其他工具类似）
```

---

## 测试验证流程

### 单元测试模板

```python
import pytest
from unittest.mock import Mock, patch
from tools.quote_tools import query_stock_quote

class TestQuoteTools:
    """行情工具测试"""
    
    @patch('tools.quote_tools.get_rest_client')
    def test_query_stock_quote_success(self, mock_client):
        """测试正常查询"""
        # 模拟响应
        mock_client.return_value.get.return_value = {
            "symbol": "TSLA.US",
            "price": 398.58,
            "change": -10.12,
            "volume": 12345678
        }
        
        # 执行测试
        result = query_stock_quote.func(symbol="TSLA")
        
        # 验证结果
        assert "TSLA.US" in result
        assert "398.58" in result
    
    def test_query_stock_quote_empty_symbol(self):
        """测试空股票代码"""
        with pytest.raises(Exception):
            query_stock_quote.func(symbol="")
```

### 集成测试脚本

```python
#!/usr/bin/env python3
"""
工具集成测试
"""
import os
import sys
import json
from pathlib import Path

# 加载环境变量
env_file = Path("/workspace/projects/.env")
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

sys.path.insert(0, '/workspace/projects/src')

from tools.quote_tools import query_stock_quote
from tools.trade_tools import submit_order

def test_quote():
    """测试行情查询"""
    print("测试行情查询...")
    result = query_stock_quote.func(symbol="TSLA")
    print(f"✅ 成功: {result[:100]}")

def test_order():
    """测试订单提交"""
    print("测试订单提交...")
    # 注意：实际测试时可能需要 mock

if __name__ == "__main__":
    test_quote()
```

---

## 常见问题与解决方案

### 问题 1：JSON 序列化错误

**症状**：`Object of type XXX is not JSON serializable`

**原因**：返回数据包含枚举、日期等不可序列化类型

**解决方案**：
```python
# 方案1：转换为字符串
"market": str(market_enum)

# 方案2：使用 .value
"market": market_enum.value

# 方案3：日期格式化
"date": date_obj.isoformat()
```

### 问题 2：枚举类型参数错误

**症状**：`'str' object cannot be cast as 'EnumType'`

**原因**：API 需要枚举类型，但传入了字符串

**解决方案**：
```python
# 创建映射表
ENUM_MAP = {
    "VALUE": EnumType.VALUE,
}

# 转换
enum_value = ENUM_MAP.get(string_value)
```

### 问题 3：API 认证失败

**症状**：401 Unauthorized

**原因**：API Key 配置错误或过期

**解决方案**：
```python
# 检查环境变量
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("未配置 API_KEY")

# 检查请求头
headers = {
    "Authorization": f"Bearer {api_key}"
}
```

### 问题 4：请求超时

**症状**：Timeout error

**解决方案**：
```python
# 增加超时时间
response = requests.get(url, timeout=60)

# 使用异步请求
import aiohttp
async with aiohttp.ClientSession() as session:
    async with session.get(url, timeout=60) as response:
        ...
```

---

## 关键经验总结

### ✅ 必须做的

1. **参数验证**：验证所有必需参数
2. **类型转换**：正确处理枚举和日期类型
3. **错误处理**：提供友好的错误提示
4. **JSON 序列化**：确保返回数据可序列化
5. **测试验证**：每个工具都要测试

### ❌ 禁止做的

1. **禁止 Mock 数据**：所有工具必须调用真实 API
2. **禁止忽略错误**：所有异常都要处理
3. **禁止硬编码**：使用环境变量配置
4. **禁止阻塞调用**：长时间操作使用异步

### 💡 最佳实践

1. **使用缓存**：减少重复请求
2. **智能推断**：自动处理参数格式
3. **中间件**：统一处理错误和日志
4. **文档完善**：每个工具都有清晰说明

---

## 附录：完整工具示例

```python
from langchain.tools import tool, ToolRuntime
from langchain_core.exceptions import LangChainException
from coze_coding_utils.runtime_ctx.context import new_context
from typing import Optional
import json
import os

@tool
def submit_order(
    symbol: str,
    order_type: str,
    side: str,
    quantity: int,
    price: Optional[float] = None,
    time_in_force: str = "Day",
    runtime: ToolRuntime = None
) -> str:
    """
    提交股票订单。
    
    参数：
        symbol: 股票代码（支持 TSLA、700.HK 等格式）
        order_type: 订单类型（LO-限价单, MO-市价单）
        side: 交易方向（Buy-买入, Sell-卖出）
        quantity: 数量
        price: 价格（限价单必填）
        time_in_force: 有效期（Day-当日, GTC-撤销前）
    """
    ctx = runtime.context if runtime else new_context(method="submit_order")
    
    try:
        # 1. 参数验证
        if not symbol:
            raise LangChainException("股票代码不能为空")
        if quantity <= 0:
            raise LangChainException("数量必须大于 0")
        
        # 2. 参数转换
        order_type_enum = ORDER_TYPE_MAP.get(order_type.upper())
        if not order_type_enum:
            raise LangChainException(
                f"无效的订单类型: {order_type}，支持: LO, MO"
            )
        
        side_enum = ORDER_SIDE_MAP.get(side)
        if not side_enum:
            raise LangChainException(
                f"无效的交易方向: {side}，支持: Buy, Sell"
            )
        
        # 3. 限价单价格检查
        if order_type_enum == OrderType.LIMIT and price is None:
            raise LangChainException("限价单必须提供价格参数")
        
        # 4. 智能推断股票代码
        full_symbol = infer_symbol_suffix(symbol)
        
        # 5. 调用 API
        client = get_rest_client()
        response = client.post("/api/v1/orders", {
            "symbol": full_symbol,
            "type": order_type_enum.value,
            "side": side_enum.value,
            "quantity": quantity,
            "price": price,
            "timeInForce": time_in_force
        })
        
        # 6. 处理响应
        result = {
            "order_id": response.get("orderId"),
            "symbol": full_symbol,
            "type": order_type,
            "side": side,
            "quantity": quantity,
            "price": price,
            "status": "submitted",
            "message": "订单提交成功"
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except LangChainException:
        raise
    except Exception as e:
        error_msg = get_friendly_error(e)
        raise LangChainException(error_msg)
```

---

> 📝 **提示**：这份文档是根据 LongPort 项目的实战经验总结的，适用于各类证券 API 项目。请根据实际 API 特点进行调整。
