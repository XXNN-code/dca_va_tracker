"""DCA Tracker 配置常量"""

DEFAULT_K = 2
DEFAULT_STRATEGY = "DCA"

MARKET_CONFIG = {
    "China": {"currency": "CNY", "account": "支付宝"},
    "Canada": {"currency": "CAD", "account": "Wealthsimple"},
}

SHEET_NAME = "Invest_Tracker"
WORKSHEET_NAME = "Records"

SHEET_COLUMNS = [
    "Date", "Type", "Name", "Ticker", "Market", "Category", "ISIN",
    "Quote", "Currency", "Fees", "Shares", "Total Amount",
    "Account", "Strategy", "M", "MA", "k",
    "Suggested Amount", "Max Amount", "n", "Total Shares", "Status",
]

CREDENTIALS_PATH = "credentials/service_account.json"
