---
name: dca_va_tracker
description: Use when the user wants to calculate, track, or manage Dollar-Cost Averaging (DCA) or Value Averaging (VA) investments for Chinese funds or Canadian stocks.
---

# DCA Tracker Skill

## Overview
This skill provides an automated investment tracking system supporting two strategies: **DCA (Dollar-Cost Averaging)** and **VA (Value Averaging)**. It integrates with Google Sheets to store records and uses `akshare` and `yfinance` to fetch real-time market data.

## When to Use

- When the user asks to "run DCA", "check investments", or "calculate what to buy today"
- When the user wants to add a new fund or stock to their DCA or VA strategy
- When the user wants to confirm and record an actual investment transaction
- When the user wants to **sell all / 清仓** a product (stops future tracking)
- When the user asks to use **Value Averaging / 价值平均法** strategy

## Strategies

### DCA (Dollar-Cost Averaging) — 均线偏离法

`Suggested Amount = M × (MA / Quote) ^ k`

- **M**: 基准定投额
- **MA**: 200日均线
- **Quote**: 当日价格
- **k**: 敏感度系数（默认 2）

### VA (Value Averaging) — 价值平均法

```
首次: Total Amount = M, n = 1, Total Shares = Shares
后续:
  n = 上次的 n + 1
  Vn = n × M                    (目标总资产)
  C  = Quote × Total Shares      (当前市值)
  In = Vn - C                    (本月操作金额)

  In > 0 → 买入 In 金额, Type = Buy
  In < 0 → 卖出 |In| 金额, Type = Sell
  In = 0 → 无需操作, 留一条 Type = Buy 记录
```

- **M**: 每月应增加的资产额
- **n**: 操作次数（按次数递增，非月份差）
- **Total Shares**: 累计持有份额

## Status Field

Each record has a `Status` column (`On` / `Off`):
- **On** (default): The product is actively tracked and included in calculations.
- **Off**: The product has been sold / 清仓. `run_dca()` will automatically skip it.
- When the user says "卖出", "清仓", "sell all", or "stop tracking" a ticker, use `sell_all()` to mark it as Off.

## Quick Reference

**IMPORTANT:** Always set your working directory to the skill's root when running these commands, and use the virtual environment (`uv run`).

### 1. Run DCA/VA Calculation
Calculates the suggested investment for all **active** (Status=On) products. Skips products updated less than 29 days ago or with Status=Off. Supports both DCA and VA strategies automatically.

```bash
source .venv/bin/activate
uv run python -c "from dca_va_tracker.main import run_dca; run_dca()"
```

### 2. Add a New DCA Product
Adds a DCA investment target. `fee_rate` is the percentage (e.g., 0.0007 for 0.07%). Status defaults to `On`. `n` and `Total Shares` are automatically initialized.

```bash
source .venv/bin/activate
uv run python -c "from dca_va_tracker.main import add_product; add_product('名称', '代码', 'China/Canada', category='类别', m=500, fee_rate=0.001, account='Wealthsimple')"
```

### 3. Add a New VA Product
Adds a Value Averaging investment target. First purchase: Total Amount = M.

```bash
source .venv/bin/activate
uv run python -c "from dca_va_tracker.main import add_va_product; add_va_product('名称', '代码', 'Canada', category='类别', m=1000, fee_rate=0.001, account='Wealthsimple')"
```

### 4. Confirm and Save Transaction
Saves the actual invested amount. Works for both DCA and VA products — automatically detects the strategy and updates `n` and `Total Shares`.

```bash
source .venv/bin/activate
uv run python -c "from dca_va_tracker.main import confirm_and_save; confirm_and_save('代码', suggested_amount=35.5, actual_amount=40.0)"
```

### 5. Record a Sell / 部分卖出
Records a partial sell transaction (Type=Sell, Status=On). The product **continues** to participate in calculations. `Total Shares` is reduced by the sold shares.

```bash
source .venv/bin/activate
uv run python -c "from dca_va_tracker.main import record_sell; record_sell('代码', actual_amount=500.0, shares=25.0)"
```

`shares` is optional — if omitted, it will be estimated from the current quote.

### 6. Sell All / 清仓
Marks a product as fully sold (Type=Sell, Status=Off). Future calculations will **skip** this product. `Total Shares` is set to 0.

```bash
source .venv/bin/activate
uv run python -c "from dca_va_tracker.main import sell_all; sell_all('代码', actual_amount=1000.0, shares=50.0)"
```

`actual_amount` and `shares` are optional — they are recorded for reference only.

## Setup & Credentials

The Google Service Account JSON must be located at `credentials/service_account.json` inside the skill directory.
