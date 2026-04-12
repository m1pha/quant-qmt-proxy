"""
交易服务层
"""
import os
import random
import sys
from datetime import datetime
from typing import Dict, List, Optional
from app.utils.logger import logger

# 添加xtquant包到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
    from xtquant.xttype import StockAccount
    from xtquant import xtconstant
    XTQUANT_AVAILABLE = True
except ImportError:
    logger.error("xtquant模块未正确安装")
    XTQUANT_AVAILABLE = False
    XtQuantTrader = None
    XtQuantTraderCallback = None
    StockAccount = None
    xtconstant = None

from app.config import Settings, XTQuantMode
from app.models.trading_models import (
    AccountInfo,
    AccountType,
    AssetInfo,
    CancelOrderRequest,
    ConnectRequest,
    ConnectResponse,
    OrderRequest,
    OrderResponse,
    OrderStatus,
    PositionInfo,
    RiskInfo,
    StrategyInfo,
    TradeInfo,
)
from app.utils.exceptions import TradingServiceException
from app.utils.helpers import validate_stock_code
from app.utils.logger import logger


# xtconstant 买卖方向映射
_ORDER_SIDE_MAP = {
    "BUY": 23,   # xtconstant.STOCK_BUY
    "SELL": 24,  # xtconstant.STOCK_SELL
}

# xtconstant 报价类型映射
_PRICE_TYPE_MAP = {
    "LIMIT": 11,    # xtconstant.FIX_PRICE
    "MARKET": 5,    # xtconstant.MARKET_SH_CONVERT_5_CANCEL（上交所最优五档转撤）
    "STOP": 11,
    "STOP_LIMIT": 11,
}

# xtconstant 委托状态映射
_ORDER_STATUS_MAP = {
    48: OrderStatus.PENDING.value,
    49: OrderStatus.SUBMITTED.value,   # 已报
    50: OrderStatus.SUBMITTED.value,   # 部分成交
    51: OrderStatus.FILLED.value,      # 全部成交
    52: OrderStatus.CANCELLED.value,   # 已撤销
    53: OrderStatus.REJECTED.value,    # 废单
    54: OrderStatus.PARTIAL_FILLED.value,
}


class TradingService:
    """交易服务类"""
    
    def __init__(self, settings: Settings):
        """初始化交易服务"""
        self.settings = settings
        self._initialized = False
        self._xt_trader: Optional[XtQuantTrader] = None
        # session_id -> {"account": StockAccount, "account_id": str, "connected_time": datetime}
        self._connected_accounts: Dict[str, dict] = {}
        self._orders: Dict[str, OrderResponse] = {}
        self._order_counter = 1000
        self._try_initialize()
    
    def _try_initialize(self):
        """尝试初始化 XtQuantTrader 全局实例"""
        if not XTQUANT_AVAILABLE:
            self._initialized = False
            return
        
        if self.settings.xtquant.mode == XTQuantMode.MOCK:
            self._initialized = False
            return
        
        try:
            path = self.settings.xtquant.data.qmt_userdata_path
            if not path:
                logger.warning("未配置 qmt_userdata_path，xttrader 无法初始化")
                self._initialized = False
                return
            
            # 全局唯一 session_id（服务级别，与账户 session 区分）
            trader_session_id = random.randint(100000, 999999)
            self._xt_trader = XtQuantTrader(path, trader_session_id)
            self._xt_trader.start()
            connect_result = self._xt_trader.connect()
            if connect_result != 0:
                logger.warning(f"xttrader 连接 MiniQMT 失败，返回码: {connect_result}")
                self._initialized = False
                return
            
            self._initialized = True
            logger.info("xttrader 已初始化")
        except Exception as e:
            logger.warning(f"xttrader 初始化失败: {e}")
            self._initialized = False
    
    def _should_use_real_trading(self) -> bool:
        """
        判断是否使用真实交易
        只有在 prod 模式且配置允许时才允许真实交易
        """
        return (
            self.settings.xtquant.mode == XTQuantMode.PROD and
            self.settings.xtquant.trading.allow_real_trading
        )
    
    def _should_use_real_data(self) -> bool:
        """
        判断是否连接xtquant获取真实数据（但不一定允许交易）
        dev 和 prod 模式都连接 xtquant
        """
        return (            
            self.settings.xtquant.mode in [XTQuantMode.DEV, XTQuantMode.PROD]
        )

    def _get_stock_account(self, session_id: str) -> StockAccount:
        """根据 session_id 获取 StockAccount 对象"""
        if session_id not in self._connected_accounts:
            raise TradingServiceException("账户未连接")
        return self._connected_accounts[session_id]["account"]
    
    def connect_account(self, request: ConnectRequest) -> ConnectResponse:
        """连接交易账户"""
        try:
            if self._initialized and self._xt_trader is not None:
                # 真实模式：订阅账户
                acc = StockAccount(request.account_id)
                subscribe_result = self._xt_trader.subscribe(acc)
                if not subscribe_result:
                    logger.warning(f"订阅账户 {request.account_id} 失败，subscribe 返回: {subscribe_result}")
                
                # 查询真实资产
                asset = self._xt_trader.query_stock_asset(acc)
                if asset:
                    account_info = AccountInfo(
                        account_id=request.account_id,
                        account_type=AccountType.SECURITY,
                        account_name=f"账户{request.account_id}",
                        status="CONNECTED",
                        balance=asset.total_asset,
                        available_balance=asset.cash,
                        frozen_balance=asset.frozen_cash,
                        market_value=asset.market_value,
                        total_asset=asset.total_asset,
                    )
                else:
                    logger.warning(f"查询账户 {request.account_id} 资产返回 None，使用默认值")
                    account_info = AccountInfo(
                        account_id=request.account_id,
                        account_type=AccountType.SECURITY,
                        account_name=f"账户{request.account_id}",
                        status="CONNECTED",
                        balance=0.0,
                        available_balance=0.0,
                        frozen_balance=0.0,
                        market_value=0.0,
                        total_asset=0.0,
                    )
                
                session_id = f"session_{request.account_id}_{datetime.now().timestamp()}"
                self._connected_accounts[session_id] = {
                    "account": acc,
                    "account_id": request.account_id,
                    "account_info": account_info,
                    "connected_time": datetime.now(),
                }
                logger.info(f"真实账户已连接: {request.account_id}, session_id={session_id}")
            else:
                # mock/dev 无 xttrader：模拟连接
                account_info = AccountInfo(
                    account_id=request.account_id,
                    account_type=AccountType.SECURITY,
                    account_name=f"账户{request.account_id}",
                    status="CONNECTED",
                    balance=1000000.0,
                    available_balance=950000.0,
                    frozen_balance=50000.0,
                    market_value=800000.0,
                    total_asset=1800000.0,
                )
                session_id = f"session_{request.account_id}_{datetime.now().timestamp()}"
                self._connected_accounts[session_id] = {
                    "account": None,
                    "account_id": request.account_id,
                    "account_info": account_info,
                    "connected_time": datetime.now(),
                }
            
            return ConnectResponse(
                success=True,
                message="账户连接成功",
                session_id=session_id,
                account_info=account_info,
            )
            
        except Exception as e:
            return ConnectResponse(
                success=False,
                message=f"账户连接失败: {str(e)}"
            )
    
    def disconnect_account(self, session_id: str) -> bool:
        """断开交易账户"""
        try:
            if session_id in self._connected_accounts:
                entry = self._connected_accounts.pop(session_id)
                if self._xt_trader and entry.get("account"):
                    try:
                        self._xt_trader.unsubscribe(entry["account"])
                    except Exception:
                        pass
                return True
            return False
        except Exception as e:
            raise TradingServiceException(f"断开账户失败: {str(e)}")
    
    def get_account_info(self, session_id: str) -> AccountInfo:
        """获取账户信息"""
        if session_id not in self._connected_accounts:
            raise TradingServiceException("账户未连接")
        
        if self._initialized and self._xt_trader is not None:
            acc = self._get_stock_account(session_id)
            asset = self._xt_trader.query_stock_asset(acc)
            if asset:
                account_id = self._connected_accounts[session_id]["account_id"]
                return AccountInfo(
                    account_id=account_id,
                    account_type=AccountType.SECURITY,
                    account_name=f"账户{account_id}",
                    status="CONNECTED",
                    balance=asset.total_asset,
                    available_balance=asset.cash,
                    frozen_balance=asset.frozen_cash,
                    market_value=asset.market_value,
                    total_asset=asset.total_asset,
                )
        
        return self._connected_accounts[session_id]["account_info"]
    
    def get_positions(self, session_id: str) -> List[PositionInfo]:
        """获取持仓信息"""
        if session_id not in self._connected_accounts:
            raise TradingServiceException("账户未连接")
        
        try:
            if self._initialized and self._xt_trader is not None:
                acc = self._get_stock_account(session_id)
                positions = self._xt_trader.query_stock_positions(acc)
                if positions is None:
                    return []
                return [
                    PositionInfo(
                        stock_code=p.stock_code,
                        stock_name=p.stock_code,
                        volume=p.volume,
                        available_volume=p.can_use_volume,
                        frozen_volume=p.volume - p.can_use_volume,
                        cost_price=p.open_price,
                        market_price=p.market_value / p.volume if p.volume > 0 else 0.0,
                        market_value=p.market_value,
                        profit_loss=p.market_value - p.open_price * p.volume,
                        profit_loss_ratio=(p.market_value - p.open_price * p.volume) / (p.open_price * p.volume)
                        if p.open_price * p.volume > 0 else 0.0,
                    )
                    for p in positions
                ]
            
            # mock 模拟数据
            return [
                PositionInfo(
                    stock_code="000001.SZ",
                    stock_name="平安银行",
                    volume=10000,
                    available_volume=10000,
                    frozen_volume=0,
                    cost_price=12.50,
                    market_price=13.20,
                    market_value=132000.0,
                    profit_loss=7000.0,
                    profit_loss_ratio=0.056,
                ),
                PositionInfo(
                    stock_code="000002.SZ",
                    stock_name="万科A",
                    volume=5000,
                    available_volume=5000,
                    frozen_volume=0,
                    cost_price=18.80,
                    market_price=19.50,
                    market_value=97500.0,
                    profit_loss=3500.0,
                    profit_loss_ratio=0.037,
                ),
            ]
            
        except TradingServiceException:
            raise
        except Exception as e:
            raise TradingServiceException(f"获取持仓信息失败: {str(e)}")
    
    def submit_order(self, session_id: str, request: OrderRequest) -> OrderResponse:
        """提交订单"""
        if session_id not in self._connected_accounts:
            raise TradingServiceException("账户未连接")
        
        try:
            if not validate_stock_code(request.stock_code):
                raise TradingServiceException(f"无效的股票代码: {request.stock_code}")
            
            # 🔒 关键拦截点：检查是否允许真实交易
            if not self._should_use_real_trading() or not self._initialized or self._xt_trader is None:
                logger.warning(f"当前模式[{self.settings.xtquant.mode.value}]不允许真实交易，返回模拟订单")
                return self._get_mock_order_response(request)
            
            # ✅ 允许真实交易，调用 XtQuantTrader 提交订单
            logger.info(f"真实交易模式：提交订单 {request.stock_code} {request.side.value} {request.volume}股")
            acc = self._get_stock_account(session_id)
            order_type_int = _ORDER_SIDE_MAP.get(request.side.value, 23)
            price_type_int = _PRICE_TYPE_MAP.get(request.order_type.value, 11)
            price = request.price if request.price is not None else 0.0
            
            order_id = self._xt_trader.order_stock(
                acc,
                request.stock_code,
                order_type_int,
                request.volume,
                price_type_int,
                price,
                request.strategy_name or "",
                "",
            )
            
            if order_id == -1:
                raise TradingServiceException("下单失败，xttrader 返回 -1")
            
            order_response = OrderResponse(
                order_id=str(order_id),
                stock_code=request.stock_code,
                side=request.side.value,
                order_type=request.order_type.value,
                volume=request.volume,
                price=request.price,
                status=OrderStatus.SUBMITTED.value,
                submitted_time=datetime.now(),
            )
            
            self._orders[str(order_id)] = order_response
            return order_response
            
        except TradingServiceException:
            raise
        except Exception as e:
            raise TradingServiceException(f"提交订单失败: {str(e)}")
    
    def _get_mock_order_response(self, request: OrderRequest) -> OrderResponse:
        """生成模拟订单响应"""
        order_id = f"mock_order_{self._order_counter}"
        self._order_counter += 1
        
        order_response = OrderResponse(
            order_id=order_id,
            stock_code=request.stock_code,
            side=request.side.value,
            order_type=request.order_type.value,
            volume=request.volume,
            price=request.price,
            status=OrderStatus.SUBMITTED.value,
            submitted_time=datetime.now(),
        )
        
        self._orders[order_id] = order_response
        return order_response
    
    def cancel_order(self, session_id: str, request: CancelOrderRequest) -> bool:
        """撤销订单（dev/mock模式下总是拦截并返回True）"""
        if session_id not in self._connected_accounts:
            raise TradingServiceException("账户未连接")
        
        # dev/mock模式下直接拦截，始终返回True
        if not self._should_use_real_trading() or not self._initialized or self._xt_trader is None:
            logger.warning(f"当前模式[{self.settings.xtquant.mode.value}]不允许真实交易，撤单请求已拦截，直接返回True")
            if request.order_id in self._orders:
                self._orders[request.order_id].status = OrderStatus.CANCELLED.value
            return True
        
        # prod模式下才做真实撤单
        try:
            logger.info(f"真实交易模式：撤销订单 {request.order_id}")
            acc = self._get_stock_account(session_id)
            result = self._xt_trader.cancel_order_stock(acc, int(request.order_id))
            success = result == 0
            if success and request.order_id in self._orders:
                self._orders[request.order_id].status = OrderStatus.CANCELLED.value
            return success
        except Exception as e:
            raise TradingServiceException(f"撤销订单失败: {str(e)}")
    
    def get_orders(self, session_id: str) -> List[OrderResponse]:
        """获取订单列表"""
        if session_id not in self._connected_accounts:
            raise TradingServiceException("账户未连接")
        
        try:
            if self._initialized and self._xt_trader is not None:
                acc = self._get_stock_account(session_id)
                orders = self._xt_trader.query_stock_orders(acc)
                if orders is None:
                    return []
                result = []
                for o in orders:
                    status = _ORDER_STATUS_MAP.get(o.order_status, OrderStatus.SUBMITTED.value)
                    resp = OrderResponse(
                        order_id=str(o.order_id),
                        stock_code=o.stock_code,
                        side="BUY" if o.order_type == _ORDER_SIDE_MAP["BUY"] else "SELL",
                        order_type="LIMIT",
                        volume=o.order_volume,
                        price=o.price,
                        status=status,
                        submitted_time=datetime.fromtimestamp(o.order_time) if o.order_time else datetime.now(),
                        filled_volume=o.traded_volume,
                        average_price=o.traded_price if o.traded_price else None,
                    )
                    result.append(resp)
                    self._orders[str(o.order_id)] = resp
                return result
            
            # mock：返回内存订单
            return list(self._orders.values())
            
        except TradingServiceException:
            raise
        except Exception as e:
            raise TradingServiceException(f"获取订单列表失败: {str(e)}")
    
    def get_trades(self, session_id: str) -> List[TradeInfo]:
        """获取成交记录"""
        if session_id not in self._connected_accounts:
            raise TradingServiceException("账户未连接")
        
        try:
            if self._initialized and self._xt_trader is not None:
                acc = self._get_stock_account(session_id)
                trades = self._xt_trader.query_stock_trades(acc)
                if trades is None:
                    return []
                return [
                    TradeInfo(
                        trade_id=t.traded_id,
                        order_id=str(t.order_id),
                        stock_code=t.stock_code,
                        side="BUY" if t.order_type == _ORDER_SIDE_MAP["BUY"] else "SELL",
                        volume=t.traded_volume,
                        price=t.traded_price,
                        amount=t.traded_amount,
                        trade_time=datetime.fromtimestamp(t.traded_time) if t.traded_time else datetime.now(),
                        commission=0.0,
                    )
                    for t in trades
                ]
            
            # mock 模拟成交数据
            return [
                TradeInfo(
                    trade_id="trade_001",
                    order_id="order_1001",
                    stock_code="000001.SZ",
                    side="BUY",
                    volume=1000,
                    price=13.20,
                    amount=13200.0,
                    trade_time=datetime.now(),
                    commission=13.20,
                )
            ]
            
        except TradingServiceException:
            raise
        except Exception as e:
            raise TradingServiceException(f"获取成交记录失败: {str(e)}")
    
    def get_asset_info(self, session_id: str) -> AssetInfo:
        """获取资产信息"""
        if session_id not in self._connected_accounts:
            raise TradingServiceException("账户未连接")
        
        try:
            if self._initialized and self._xt_trader is not None:
                acc = self._get_stock_account(session_id)
                asset = self._xt_trader.query_stock_asset(acc)
                if asset:
                    return AssetInfo(
                        total_asset=asset.total_asset,
                        market_value=asset.market_value,
                        cash=asset.cash,
                        frozen_cash=asset.frozen_cash,
                        available_cash=asset.cash,
                        profit_loss=0.0,
                        profit_loss_ratio=0.0,
                    )
            
            # mock 模拟资产数据
            return AssetInfo(
                total_asset=1800000.0,
                market_value=800000.0,
                cash=950000.0,
                frozen_cash=50000.0,
                available_cash=900000.0,
                profit_loss=50000.0,
                profit_loss_ratio=0.028,
            )
            
        except TradingServiceException:
            raise
        except Exception as e:
            raise TradingServiceException(f"获取资产信息失败: {str(e)}")
    
    def get_risk_info(self, session_id: str) -> RiskInfo:
        """获取风险信息"""
        if session_id not in self._connected_accounts:
            raise TradingServiceException("账户未连接")
        
        try:
            # 这里可以添加风险计算逻辑
            return RiskInfo(
                position_ratio=0.44,  # 持仓比例
                cash_ratio=0.56,      # 现金比例
                max_drawdown=0.05,    # 最大回撤
                var_95=0.02,          # 95% VaR
                var_99=0.03           # 99% VaR
            )
            
        except Exception as e:
            raise TradingServiceException(f"获取风险信息失败: {str(e)}")
    
    def get_strategies(self, session_id: str) -> List[StrategyInfo]:
        """获取策略列表"""
        if session_id not in self._connected_accounts:
            raise TradingServiceException("账户未连接")
        
        try:
            # 模拟策略数据
            mock_strategies = [
                StrategyInfo(
                    strategy_name="MA策略",
                    strategy_type="TREND_FOLLOWING",
                    status="RUNNING",
                    created_time=datetime.now(),
                    last_update_time=datetime.now(),
                    parameters={"period": 20, "threshold": 0.02}
                ),
                StrategyInfo(
                    strategy_name="均值回归策略",
                    strategy_type="MEAN_REVERSION",
                    status="STOPPED",
                    created_time=datetime.now(),
                    last_update_time=datetime.now(),
                    parameters={"lookback": 10, "entry_threshold": 0.05}
                )
            ]
            
            return mock_strategies
            
        except Exception as e:
            raise TradingServiceException(f"获取策略列表失败: {str(e)}")
    
    def is_connected(self, session_id: str) -> bool:
        """检查账户是否连接"""
        return session_id in self._connected_accounts
