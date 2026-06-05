"""calculator 模块测试"""
from dca_va_tracker.calculator import calculate


def test_dca_basic():
    """MA == Quote 时，suggested == M"""
    result = calculate("DCA", m=500, ma=10.0, quote=10.0, k=2)
    assert result["suggested_amount"] == 500.0
    assert result["capped"] is False


def test_dca_undervalued():
    """MA > Quote 时，suggested > M"""
    result = calculate("DCA", m=500, ma=12.0, quote=10.0, k=2)
    expected = 500 * (12.0 / 10.0) ** 2  # 720
    assert abs(result["suggested_amount"] - expected) < 0.01


def test_dca_overvalued():
    """MA < Quote 时，suggested < M"""
    result = calculate("DCA", m=500, ma=8.0, quote=10.0, k=2)
    expected = 500 * (8.0 / 10.0) ** 2  # 320
    assert abs(result["suggested_amount"] - expected) < 0.01


def test_dca_capped():
    """超过 max_amount 时触顶"""
    result = calculate("DCA", m=500, ma=20.0, quote=10.0, k=2, max_amount=1000)
    assert result["suggested_amount"] == 1000.0
    assert result["capped"] is True


def test_dca_shares():
    """份额计算正确"""
    result = calculate("DCA", m=500, ma=10.0, quote=10.0, k=2)
    assert abs(result["shares"] - 50.0) < 0.01


def test_unknown_strategy():
    """未知策略应报错"""
    try:
        calculate("UNKNOWN", m=500, ma=10.0, quote=10.0)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


# ---- VA 策略测试 ----

def test_va_first_month():
    """第1月 (n=1): 首月应买入 M 金额 (total_shares=0)"""
    result = calculate("VA", m=1000, quote=10.0, n=1, total_shares=0)
    assert result["suggested_amount"] == 1000.0
    assert result["action"] == "Buy"
    assert result["shares"] == 100.0       # 1000 / 10
    assert result["new_total_shares"] == 100.0
    assert result["n"] == 1


def test_va_buy_when_price_drops():
    """价格下跌时，需要买入更多以达到目标"""
    # 第1月: 买了 100 份 @ 10 = 1000
    # 第2月: 价格跌到 8, 市值 = 100*8 = 800, 目标 = 2000, 需买入 1200
    result = calculate("VA", m=1000, quote=8.0, n=2, total_shares=100)
    assert result["target_value"] == 2000.0
    assert result["current_value"] == 800.0
    assert result["investment"] == 1200.0
    assert result["action"] == "Buy"
    assert result["shares"] == 150.0       # 1200 / 8


def test_va_sell_when_price_rises():
    """价格大涨时，需要卖出以维持目标"""
    # 第1月: 买了 100 份 @ 10 = 1000
    # 第2月: 价格涨到 25, 市值 = 100*25 = 2500, 目标 = 2000, 需卖出 500
    result = calculate("VA", m=1000, quote=25.0, n=2, total_shares=100)
    assert result["target_value"] == 2000.0
    assert result["current_value"] == 2500.0
    assert result["investment"] == -500.0
    assert result["action"] == "Sell"
    assert result["shares"] == 20.0        # 500 / 25
    assert result["new_total_shares"] == 80.0


def test_va_no_action():
    """目标恰好等于市值时，无需操作"""
    result = calculate("VA", m=1000, quote=10.0, n=2, total_shares=200)
    assert result["investment"] == 0
    assert result["action"] == "Buy"
    assert result["shares"] == 0
    assert result["new_total_shares"] == 200.0


def test_va_with_fees():
    """手续费应从操作金额中扣除"""
    # 买入 1000, fee_rate=0.001, fees=1, shares = (1000-1)/10 = 99.9
    result = calculate("VA", m=1000, quote=10.0, n=1, total_shares=0, fee_rate=0.001)
    assert result["fees"] == 1.0
    assert result["shares"] == 99.9
    assert result["new_total_shares"] == 99.9
