"""策略计算引擎 — 可扩展的投资策略计算"""
from typing import Callable

STRATEGY_REGISTRY: dict[str, Callable] = {}


def register_strategy(name: str):
    """装饰器：注册新的计算策略"""
    def decorator(func):
        STRATEGY_REGISTRY[name] = func
        return func
    return decorator


def calculate(strategy: str, **kwargs) -> dict:
    """统一入口：根据 strategy 名称分发到对应计算函数"""
    if strategy not in STRATEGY_REGISTRY:
        raise ValueError(
            f"未知策略: {strategy}，可用: {list(STRATEGY_REGISTRY.keys())}"
        )
    return STRATEGY_REGISTRY[strategy](**kwargs)


@register_strategy("DCA")
def calculate_dca(
    m: float,
    ma: float,
    quote: float,
    k: float = 2,
    max_amount: float | None = None,
    **kwargs,
) -> dict:
    """DCA 均线偏离法: suggested = M × (MA / Quote) ^ k"""
    ratio = ma / quote
    suggested = m * (ratio ** k)
    capped = False
    if max_amount is not None and suggested > max_amount:
        suggested = max_amount
        capped = True
    shares = suggested / quote
    return {
        "suggested_amount": round(suggested, 2),
        "shares": round(shares, 4),
        "capped": capped,
        "ratio": round(ratio, 4),
    }


@register_strategy("VA")
def calculate_va(
    m: float,
    quote: float,
    n: int,
    total_shares: float,
    fee_rate: float = 0,
    **kwargs,
) -> dict:
    """Value Averaging: 本月操作额 = 目标总资产 - 当前市值

    Args:
        m: 每月应增加的资产额
        quote: 当前价格
        n: 当前是第几个月 (从 1 开始)
        total_shares: 累计持有份额
        fee_rate: 手续费率
    """
    vn = n * m                            # 目标总资产
    current_value = quote * total_shares   # 当前市值
    investment = vn - current_value        # 需要操作的金额 (正=买入, 负=卖出)

    if investment > 0:
        # 买入: 扣除手续费后计算份额
        fees = round(investment * fee_rate, 4)
        shares = round((investment - fees) / quote, 4)
        action = "Buy"
    elif investment < 0:
        # 卖出: 份额按卖出金额计算，手续费从所得中扣
        fees = round(abs(investment) * fee_rate, 4)
        shares = round(abs(investment) / quote, 4)
        action = "Sell"
    else:
        # 无需操作
        fees = 0
        shares = 0
        action = "Buy"

    new_total_shares = total_shares + shares if action == "Buy" else total_shares - shares

    return {
        "investment": round(investment, 2),
        "suggested_amount": round(abs(investment), 2),
        "shares": shares,
        "fees": fees,
        "action": action,
        "target_value": round(vn, 2),
        "current_value": round(current_value, 2),
        "new_total_shares": round(new_total_shares, 4),
        "n": n,
    }
