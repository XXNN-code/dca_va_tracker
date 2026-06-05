# DCA VA Tracker — 自动定投追踪系统

AI Agent 驱动的智能定投计算与记录工具。

## 功能

- 📊 **自动定投计算** — 批量计算所有产品的建议买入/卖出金额
- ➕ **添加新产品** — 自动获取行情并写入 Google Sheet
- 📈 **双市场支持** — 中国场外基金（akshare）+ 加拿大股票（yfinance）
- 🔄 **双策略支持** — DCA 均线偏离法 + VA 价值平均法
- 📉 **买卖追踪** — 统一跟踪 n（操作次数）和 Total Shares（累计份额）

## 安装

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

## Google API 设置

详见 [setup_guide.md](setup_guide.md)

## 使用方式（通过 AI Agent）

### 执行定投（DCA + VA）
```python
from dca_va_tracker.main import run_dca
results = run_dca()
```

### 添加 DCA 产品
```python
from dca_va_tracker.main import add_product
add_product('易方达中小盘', '110011', 'China', category='基金', m=500, fee_rate=0.001)
```

### 添加 VA 产品
```python
from dca_va_tracker.main import add_va_product
add_va_product('XEQT', 'XEQT.TO', 'Canada', category='ETF', m=1000, fee_rate=0.001)
```

### 确认交易（DCA / VA 通用）
```python
from dca_va_tracker.main import confirm_and_save
confirm_and_save('110011', suggested_amount=523.4)
# 或指定实际金额
confirm_and_save('110011', suggested_amount=523.4, actual_amount=500)
```

## 策略公式

### DCA — 均线偏离法
```
Suggested Amount = M × (MA / Quote) ^ k
```
- **M**: 基准定投额
- **MA**: 200日均线
- **Quote**: 当日价格
- **k**: 敏感度系数（默认 2）

### VA — 价值平均法
```
Vn = n × M          (目标总资产)
C  = Quote × Total Shares  (当前市值)
In = Vn - C          (本月操作金额)

In > 0 → 买入    In < 0 → 卖出    In = 0 → 无需操作
```
- **M**: 每月应增加的资产额
- **n**: 操作次数（按次递增）
- **Total Shares**: 累计持有份额
