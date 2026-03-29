# quant-qmt-proxy 智能 Agent 生成提示词

> 用于在 Coze 平台生成 quant-qmt-proxy 量化交易智能体项目代码

---

## 完整提示词

```markdown
# 项目需求

创建一个基于 quant-qmt-proxy API 的智能量化交易 Agent，支持通过 Chat 进行自然语言交互，具备以下功能：

- 行情查询：K 线数据、实时 Tick、Level2 深度数据、板块/指数成分
- 账户管理：账户信息、资产汇总、持仓查询、风险指标
- 交易执行：下单（限价/市价）、撤单、查询订单/成交记录
- 数据下载：历史数据下载、财务数据下载、节假日/板块数据更新
- 订阅管理：创建/查询/取消行情订阅

## API 文档

### 基本信息

- REST API Base URL：`http://{HOST}`（由环境变量 `API_BASE_URL` 配置）
- 认证方式：请求头 `X-API-Key: <your-key>`（除健康检查外所有接口均需要）
- 健康检查：`GET /health/`（无需认证）

### 通用响应格式

```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": { ... }
}
```

错误时 `success: false`，`code` 为 400/401/404/500。

---

### 行情接口

#### POST /api/v1/data/market
获取 K 线 / Tick 历史数据（多支股票）。

请求体：
```json
{
  "stock_codes": ["000001.SZ", "600000.SH"],
  "start_date": "20240101",
  "end_date": "20240331",
  "period": "1d",
  "fields": null,
  "adjust_type": "none",
  "fill_data": true,
  "disable_download": false
}
```

`period` 可选值：`tick` `1m` `5m` `15m` `30m` `1h` `1d` `1w` `1mon` `1q` `1hy` `1y`
`adjust_type` 可选值：`none` `front` `back` `front_ratio` `back_ratio`

响应：`List[MarketDataResponse]`，每项包含 `stock_code`、`period`、`fields`、`data[]`（每条含 `time(ms)` `open` `high` `low` `close` `volume` `amount`）

#### POST /api/v1/data/full-tick
获取实时 Tick 快照（含5档买卖盘）。

请求体：`{"stock_codes": ["000001.SZ"]}`

响应：包含 `last_price` `open` `high` `low` `volume` `amount` `ask_price[5]` `bid_price[5]` `ask_vol[5]` `bid_vol[5]` `transaction_num`

#### POST /api/v1/data/l2/quote
获取 Level2 快照（10档买卖盘）。

请求体：`{"stock_codes": ["000001.SZ"], "start_time": "", "end_time": ""}`

#### POST /api/v1/data/l2/order
获取 Level2 逐笔委托数据。

#### POST /api/v1/data/l2/transaction
获取 Level2 逐笔成交数据。

#### POST /api/v1/data/financial
获取财务报表数据（Balance/Income/CashFlow）。

请求体：
```json
{"stock_codes": ["000001.SZ"], "table_list": ["Balance", "Income", "CashFlow"], "start_date": "20230101", "end_date": "20231231"}
```

#### GET /api/v1/data/sectors
获取全部板块/指数列表。

#### POST /api/v1/data/sector
获取某板块的成分股列表。请求体：`{"sector_name": "沪深300"}`

#### POST /api/v1/data/index-weight
获取指数成分权重。请求体：`{"index_code": "000300.SH", "date": "20240101"}`

#### GET /api/v1/data/trading-calendar/{year}
获取交易日历。

#### GET /api/v1/data/instrument/{stock_code}
获取合约/股票基本信息（名称、涨跌停价、流通股本、是否交易中）。

#### GET /api/v1/data/instrument-type/{stock_code}
获取合约类型（stock/index/fund/etf/bond/option/futures）。

#### GET /api/v1/data/etf/{etf_code}
获取 ETF 基本信息。

#### GET /api/v1/data/holidays
获取节假日列表。

#### GET /api/v1/data/period-list
获取当前 QMT 支持的数据周期列表。

---

### 订阅接口

#### POST /api/v1/data/subscription
创建行情订阅，返回 `subscription_id`。

请求体：
```json
{"symbols": ["000001.SZ"], "period": "tick", "start_date": "", "adjust_type": "none", "subscription_type": "quote"}
```

`subscription_type`：`quote`（指定股票）或 `whole_quote`（全市场推送）

#### GET /api/v1/data/subscriptions
列出所有活跃订阅。

#### GET /api/v1/data/subscription/{subscription_id}
查询单个订阅详情（含 `queue_size` `active` `last_heartbeat`）。

#### DELETE /api/v1/data/subscription/{subscription_id}
取消订阅。

---

### 数据下载接口

#### POST /api/v1/data/download/history-data
下载单支股票历史 K 线（建议 `incrementally: true`）。

请求体：
```json
{"stock_code": "000001.SZ", "period": "1d", "start_time": "20230101", "end_time": "20231231", "incrementally": true}
```

#### POST /api/v1/data/download/history-data-batch
批量下载多支股票历史数据。

请求体：
```json
{"stock_list": ["000001.SZ", "600000.SH"], "period": "1d", "start_time": "20230101", "end_time": "20231231"}
```

#### POST /api/v1/data/download/financial-data
下载财务报表数据。

#### POST /api/v1/data/download/sector-data
下载板块成分数据。

#### POST /api/v1/data/download/index-weight
下载指数权重数据。请求体：`{"index_code": "000300.SH"}`（null 表示全部）

#### POST /api/v1/data/download/holiday-data
下载/更新节假日数据。

---

### 交易接口

#### POST /api/v1/trading/connect
连接交易账户。

请求体：
```json
{"account_id": "1000000365", "account_type": "STOCK", "path": "D:/QMT/userdata_mini", "session_id": 123456}
```

响应：含 `session_id` 和 `connected`

#### POST /api/v1/trading/disconnect/{session_id}
断开交易会话。

#### GET /api/v1/trading/account/{session_id}
获取账户信息。

#### GET /api/v1/trading/positions/{session_id}
获取持仓列表（`stock_code` `volume` `can_use_volume` `avg_price` `market_value` `profit_rate`）。

#### GET /api/v1/trading/asset/{session_id}
获取资产汇总（`total_asset` `cash` `market_value` `frozen_cash` `profit`）。

#### POST /api/v1/trading/order/{session_id}
提交订单。

请求体：
```json
{"stock_code": "000001.SZ", "order_type": "buy", "price": 9.50, "volume": 100, "price_type": "LO"}
```

`order_type`：`buy` | `sell`
`price_type`：`LO`（限价）| `MO`（市价）| `AO`（集合竞价）

响应：`OrderResponse`，含 `order_id` `status` `message`

#### POST /api/v1/trading/cancel/{session_id}
撤销订单。请求体：`{"order_id": "order_abc123"}`

#### GET /api/v1/trading/orders/{session_id}
获取订单列表。

#### GET /api/v1/trading/trades/{session_id}
获取成交记录。

#### GET /api/v1/trading/risk/{session_id}
获取风险指标。

#### GET /api/v1/trading/status/{session_id}
获取连接状态（`{"connected": true}`）。

---

## 股票代码格式

格式：`{代码}.{交易所}`，例如：
- `000001.SZ` — 平安银行（深圳）
- `600000.SH` — 浦发银行（上海）
- `000300.SH` — 沪深 300 指数
- `510300.SH` — 沪深 300 ETF
- `IC2403.CFE` — 中证 500 期货（中金所）

智能推断规则：
- 6 开头的纯数字 → `.SH`（上海）
- 0 或 3 开头的纯数字 → `.SZ`（深圳）
- 其他纯数字 → `.BJ`（北交所）

---

## 技术要求

### 1. 技术栈

- Python 3.12
- LangChain 1.0+（工具定义与 Agent 构建）
- LangGraph 1.0+（Agent 工作流）
- `requests`（REST 客户端）
- `python-dotenv`（环境变量管理）

### 2. 项目结构

```
qmt-agent/
├── src/
│   ├── agents/
│   │   └── agent.py              # Agent 主逻辑与系统提示词
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── market_tools.py       # 行情查询工具
│   │   ├── trade_tools.py        # 交易工具
│   │   ├── account_tools.py      # 账户工具
│   │   ├── download_tools.py     # 数据下载工具
│   │   └── subscription_tools.py # 订阅管理工具
│   ├── api/
│   │   └── rest_client.py        # REST API 客户端（统一封装）
│   ├── models/
│   │   ├── enums.py              # 枚举：PeriodType, AdjustType, PriceType, OrderType
│   │   └── schemas.py            # Pydantic 数据模型
│   └── main.py                   # 入口（Chat 交互循环）
├── config/
│   └── agent_llm_config.json     # LLM 配置
├── docs/
│   └── USER_MANUAL.md            # 用户手册
├── .env                          # 环境变量
├── requirements.txt
└── README.md
```

### 3. REST 客户端封装要求

```python
class QMTRestClient:
    """quant-qmt-proxy REST 客户端"""
    
    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-Key": api_key,
            "Content-Type": "application/json",
        })
        self.timeout = timeout
    
    def _request(self, method: str, endpoint: str, params=None, data=None) -> dict:
        """统一请求方法，处理认证、超时、HTTP 错误"""
        ...
    
    def get(self, endpoint: str, params=None) -> dict: ...
    def post(self, endpoint: str, data=None) -> dict: ...
    def delete(self, endpoint: str) -> dict: ...

@lru_cache(maxsize=1)
def get_client() -> QMTRestClient:
    base_url = os.getenv("API_BASE_URL")
    api_key = os.getenv("API_KEY")
    if not base_url or not api_key:
        raise ValueError("请配置 API_BASE_URL 和 API_KEY 环境变量")
    return QMTRestClient(base_url=base_url, api_key=api_key)
```

HTTP 错误处理：
- 401 → `"认证失败，请检查 API_KEY 配置"`
- 404 → `"资源不存在: {endpoint}"`
- 500 → 解析响应体中的 `message` 字段

### 4. 工具定义要求

每个工具必须：

1. 使用 `@tool` 装饰器
2. 有清晰的中文文档字符串（描述功能、参数含义）
3. 所有参数有类型注解
4. 返回 `json.dumps(result, ensure_ascii=False, indent=2)` 格式的 JSON 字符串
5. 包含完整错误处理，抛出 `LangChainException` 并附友好中文提示

**工具模板：**
```python
from langchain.tools import tool
from langchain_core.exceptions import LangChainException
import json

@tool
def tool_name(param: str) -> str:
    """工具功能描述。参数：param - 参数说明（如 000001.SZ）"""
    try:
        # 参数验证
        if not param or not param.strip():
            raise LangChainException("参数不能为空")
        # 调用 API
        client = get_client()
        response = client.post("/api/v1/...", {"key": param})
        # 提取核心数据
        result = response.get("data") or response
        return json.dumps(result, ensure_ascii=False, indent=2)
    except LangChainException:
        raise
    except Exception as e:
        raise LangChainException(f"操作失败: {str(e)}")
```

### 5. 枚举定义

```python
from enum import Enum

class PeriodType(str, Enum):
    TICK = "tick"
    M1 = "1m";  M5 = "5m";  M15 = "15m";  M30 = "30m"
    H1 = "1h";  D1 = "1d";  W1 = "1w";   MON1 = "1mon"

class AdjustType(str, Enum):
    NONE = "none";  FRONT = "front";  BACK = "back"
    FRONT_RATIO = "front_ratio";  BACK_RATIO = "back_ratio"

class PriceType(str, Enum):
    LIMIT = "LO";  MARKET = "MO";  AUCTION = "AO"

class OrderSide(str, Enum):
    BUY = "buy";  SELL = "sell"
```

### 6. 股票代码智能推断

```python
def normalize_stock_code(code: str) -> str:
    """自动补全股票代码后缀"""
    code = code.strip().upper()
    if '.' in code:
        return code
    if code.isdigit():
        if code.startswith('6'):
            return f"{code}.SH"
        elif code.startswith(('0', '3')):
            return f"{code}.SZ"
        else:
            return f"{code}.BJ"
    return code  # 期货/ETF 等非纯数字代码原样返回
```

### 7. 工具列表（必须全部实现）

#### 行情工具（`src/tools/market_tools.py`）

| 工具名 | 调用接口 | 描述 |
|--------|----------|------|
| `get_kline` | POST /api/v1/data/market | 查询 K 线数据，支持多股、多周期 |
| `get_full_tick` | POST /api/v1/data/full-tick | 查询实时 Tick 快照（含5档盘口） |
| `get_l2_quote` | POST /api/v1/data/l2/quote | 查询 Level2 十档买卖盘 |
| `get_instrument_info` | GET /api/v1/data/instrument/{code} | 查询股票基本信息（名称、涨跌停） |
| `get_instrument_type` | GET /api/v1/data/instrument-type/{code} | 查询合约类型（股票/ETF/期货等） |
| `get_sectors` | GET /api/v1/data/sectors | 获取全部板块列表 |
| `get_sector_stocks` | POST /api/v1/data/sector | 获取板块成分股 |
| `get_index_weight` | POST /api/v1/data/index-weight | 查询指数成分权重 |
| `get_trading_calendar` | GET /api/v1/data/trading-calendar/{year} | 查询交易日历 |
| `get_financial_data` | POST /api/v1/data/financial | 查询财务报表数据 |

#### 账户工具（`src/tools/account_tools.py`）

| 工具名 | 调用接口 | 描述 |
|--------|----------|------|
| `get_account_info` | GET /api/v1/trading/account/{session_id} | 查询账户信息 |
| `get_asset_summary` | GET /api/v1/trading/asset/{session_id} | 查询资产汇总（总资产/现金/市值/浮盈） |
| `get_positions` | GET /api/v1/trading/positions/{session_id} | 查询持仓列表 |
| `get_orders` | GET /api/v1/trading/orders/{session_id} | 查询订单记录 |
| `get_trades` | GET /api/v1/trading/trades/{session_id} | 查询成交记录 |
| `get_risk_metrics` | GET /api/v1/trading/risk/{session_id} | 查询风险指标 |

#### 交易工具（`src/tools/trade_tools.py`）

| 工具名 | 调用接口 | 描述 |
|--------|----------|------|
| `connect_account` | POST /api/v1/trading/connect | 连接 QMT 交易账户 |
| `submit_order` | POST /api/v1/trading/order/{session_id} | 提交买卖订单（支持限价/市价/竞价） |
| `cancel_order` | POST /api/v1/trading/cancel/{session_id} | 撤销指定订单 |

#### 订阅工具（`src/tools/subscription_tools.py`）

| 工具名 | 调用接口 | 描述 |
|--------|----------|------|
| `create_subscription` | POST /api/v1/data/subscription | 创建行情订阅，返回 subscription_id |
| `list_subscriptions` | GET /api/v1/data/subscriptions | 列出全部活跃订阅 |
| `cancel_subscription` | DELETE /api/v1/data/subscription/{id} | 取消订阅 |

#### 数据下载工具（`src/tools/download_tools.py`）

| 工具名 | 调用接口 | 描述 |
|--------|----------|------|
| `download_history` | POST /api/v1/data/download/history-data | 下载单支股票历史数据 |
| `download_history_batch` | POST /api/v1/data/download/history-data-batch | 批量下载历史数据 |
| `download_financial` | POST /api/v1/data/download/financial-data | 下载财务报表数据 |
| `download_sector_data` | POST /api/v1/data/download/sector-data | 下载板块成分数据 |

### 8. 系统提示词

```python
SYSTEM_PROMPT = """
# 角色定义
你是专业的 A 股量化交易助手，基于API调用提供智能化服务。
你具备专业的 A 股金融知识，能够帮助用户进行行情查询、数据分析、账户管理和交易执行等操作。

# 支持的市场
- A 股：沪市（SH）、深市（SZ）、北交所（BJ）
- 期货：中金所（CFE）、上期所（SHF）、大商所（DCE）、郑商所（ZCE）
- 基金与 ETF

# 股票代码格式
格式为 {代码}.{交易所}，例如：000001.SZ、600000.SH、510300.SH。
若用户输入纯数字代码，自动判断：6开头→SH，0/3开头→SZ，其他→BJ。

# 核心能力

## 1. 行情查询
- K 线数据（支持 tick/1m/5m/15m/30m/1h/1d/1w/1mon 等周期）
- 实时 Tick 快照和 Level2 十档盘口
- 财务报表（资产负债表/利润表/现金流量表）
- 板块成分、指数权重、交易日历

## 2. 账户管理
- 查询账户资产（总资产、可用现金、持仓市值、浮动盈亏）
- 查询持仓列表（成本价、现价、盈亏率）
- 查询订单和成交记录

## 3. 交易执行（需要先连接账户）
- 提交限价单（LO）、市价单（MO）、集合竞价单（AO）
- 撤销未成交订单

## 4. 数据下载
- 下载历史 K 线数据到本地缓存（建议用增量模式）
- 下载财务、板块、节假日等基础数据

# 工作流程

1. **理解意图**：分析用户的中文需求，确定需要调用的工具
2. **补全参数**：若用户未提供完整股票代码，自动补全后缀
3. **调用工具**：选择合适的工具完成任务
4. **格式化展示**：将数据以清晰易读的中文 + 表格/列表形式呈现

# 交易规则

1. **风险提示**：任何下单操作前必须明确告知用户风险
2. **确认机制**：下单前必须向用户确认：股票代码、方向、价格、数量
3. **账户连接**：执行交易前必须确认账户已连接（先调用 connect_account 或检查 session_id）
4. **参数验证**：限价单必须有价格；数量必须为正整数且符合最小手数要求（A股1手=100股）

# 输出格式规范

- 行情数据：以表格形式展示 OHLCV，时间显示为 YYYY-MM-DD HH:MM:SS
- 持仓数据：表格展示，包含盈亏率和市值
- 下单结果：显示订单ID、状态
- 错误信息：清晰解释原因和解决建议

# 约束条件

1. 所有操作必须通过工具调用真实 API，禁止编造数据
2. 不提供具体的投资建议，仅提供数据查询和操作执行
3. 遵守 A 股交易规则（T+1、涨跌幅限制、最小交易单位）
"""
```

### 9. 错误处理

认证错误识别：
```python
ERROR_MAP = {
    "401": "API Key 无效或未配置，请检查 API_KEY 环境变量",
    "404": "资源不存在，请检查股票代码或订阅 ID 是否正确",
    "500": "服务内部错误，请检查 quant-qmt-proxy 服务是否正常运行",
    "timeout": "请求超时，请检查 quant-qmt-proxy 服务是否可访问",
    "connection": "无法连接到服务，请检查 API_BASE_URL 配置（当前：{url}）",
}
```

### 10. 用户手册

为每个工具提供：
- 功能说明
- 参数详解
- 用户提问示例（不少于 5 个中文自然语言示例）
- 返回数据示例（精简版）
- 注意事项

---

## 环境变量配置

```bash
# .env 文件
API_BASE_URL=http://127.0.0.1:8000
API_KEY=your_api_key_here
```

---

## 开发步骤

请严格按以下步骤开发，每步完成后输出文件内容和测试结果：

### 第一步：基础框架
1. 创建 `requirements.txt`（langchain, langchain-core, langgraph, requests, python-dotenv, pydantic）
2. 创建 `src/api/rest_client.py`（QMTRestClient 类 + get_client 函数）
3. 创建 `src/models/enums.py`（PeriodType, AdjustType, PriceType, OrderSide）
4. 创建 `.env` 模板
5. 测试：验证 REST 客户端能成功请求 `GET /health/`

### 第二步：行情工具
1. 创建 `src/tools/market_tools.py`，实现行情工具表中全部 10 个工具
2. 所有工具支持股票代码自动推断（normalize_stock_code）
3. 测试：调用 `get_instrument_info("000001")` 和 `get_kline("000001.SZ", "1d", "20240101", "20240331")`

### 第三步：账户工具
1. 创建 `src/tools/account_tools.py`，实现账户工具表中全部 6 个工具
2. session_id 参数来自环境变量 `QMT_SESSION_ID` 或工具参数
3. 测试：查询持仓和资产

### 第四步：交易工具
1. 创建 `src/tools/trade_tools.py`，实现 3 个交易工具
2. submit_order 必须先确认参数再调用 API
3. 测试：用测试账户验证下单和撤单流程

### 第五步：订阅和下载工具
1. 创建 `src/tools/subscription_tools.py`（3 个工具）
2. 创建 `src/tools/download_tools.py`（4 个工具）

### 第六步：Agent 构建
1. 创建 `src/agents/agent.py`，注册全部工具，配置系统提示词
2. 创建 `config/agent_llm_config.json`
3. 创建 `src/main.py`，实现 Chat 交互主循环
4. 测试：完整对话测试（行情查询 + 下单确认流程）

### 第七步：文档完善
1. 编写 `docs/USER_MANUAL.md`（每个工具 5+ 个中文提问示例）
2. 完善 `README.md`（安装、配置、启动说明）

---

## 关键注意事项

### ✅ 必须做的
1. 所有工具调用真实 API，禁止 Mock 数据
2. 返回 JSON 字符串，确保可被 LLM 解析
3. 枚举值传参前转换（如 `PriceType.LIMIT.value` → `"LO"`）
4. 日期时间用 `isoformat()` 或 `YYYYMMDD` 字符串
5. 每步都要有测试验证

### ❌ 禁止做的
1. 禁止硬编码 API Key 或 URL
2. 禁止忽略 API 返回的错误信息
4. 禁止返回 Python 对象（需转为 JSON 字符串）

### 💡 重要经验
1. 时间戳为毫秒级 Unix 时间，展示时需转换为可读格式
2. 下载数据后才能查询历史数据（先调 download_history，再调 get_kline）
3. 实时订阅需要 WebSocket（本 Agent 仅创建订阅、返回 subscription_id，不实现 WS 推送消费）

---

## 预期产出

完成后的项目：
- `src/tools/` — 26 个工具（行情10 + 账户6 + 交易3 + 订阅3 + 下载4）
- `src/api/rest_client.py` — QMT REST 客户端
- `src/agents/agent.py` — Agent 实现（含系统提示词）
- `config/agent_llm_config.json` — LLM 配置
- `docs/USER_MANUAL.md` — 含全部工具的中文使用手册

---

请根据以上要求，从第一步开始逐步创建项目。每完成一步，输出关键文件的核心内容并说明测试方法。
```
