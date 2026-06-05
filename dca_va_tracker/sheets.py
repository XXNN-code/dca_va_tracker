"""Google Sheets CRUD 操作"""
import gspread
from google.oauth2.service_account import Credentials

from dca_va_tracker.config import CREDENTIALS_PATH, SHEET_NAME, WORKSHEET_NAME, SHEET_COLUMNS


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_client() -> gspread.Client:
    """获取 gspread 客户端（Service Account 认证）"""
    creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
    return gspread.authorize(creds)


def init_sheet() -> str:
    """初始化 Sheet：打开已有的 Sheet，确保 Records 工作表和表头存在。

    Sheet 需要用户在 Google Drive 中手动创建并共享给服务账户。
    返回 Sheet URL。
    """
    gc = get_client()
    try:
        sh = gc.open(SHEET_NAME)
    except gspread.SpreadsheetNotFound:
        raise RuntimeError(
            f"未找到名为 '{SHEET_NAME}' 的 Google Sheet。\n"
            f"请在 Google Drive 中创建此 Sheet，并共享给服务账户。"
        )

    # 确保 Records 工作表存在
    try:
        ws = sh.worksheet(WORKSHEET_NAME)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(
            title=WORKSHEET_NAME, rows=1000, cols=len(SHEET_COLUMNS)
        )

    # 检查是否需要写入表头
    first_row = ws.row_values(1)
    if not first_row:
        ws.append_row(SHEET_COLUMNS)

    return sh.url


def _get_worksheet() -> gspread.Worksheet:
    """获取工作表（内部使用）"""
    gc = get_client()
    sh = gc.open(SHEET_NAME)
    return sh.worksheet(WORKSHEET_NAME)


def normalize_ticker(ticker, market: str | None = None) -> str:
    """标准化 Ticker。如果是中国基金（纯数字，或 Market="China"），补齐 6 位。"""
    t_str = str(ticker).strip()
    if market == "China" or (t_str.isdigit() and len(t_str) <= 6):
        return t_str.zfill(6)
    return t_str


def get_all_records() -> list[dict]:
    """读取所有记录，返回字典列表"""
    ws = _get_worksheet()
    return ws.get_all_records()


def get_unique_tickers(records: list[dict] | None = None) -> list[str]:
    """获取不重复的 Ticker 列表（保持首次出现顺序），支持传入缓存的 records"""
    if records is None:
        records = get_all_records()
    seen = set()
    tickers = []
    for r in records:
        t = r.get("Ticker", "")
        if t:
            market = r.get("Market", "")
            t_str = normalize_ticker(t, market)
            if t_str not in seen:
                seen.add(t_str)
                tickers.append(t_str)
    return tickers


def get_latest_record(ticker: str, records: list[dict] | None = None) -> dict | None:
    """获取某 Ticker 最新一条记录（最后一行），支持传入缓存的 records"""
    if records is None:
        records = get_all_records()
    
    matches = []
    for r in records:
        r_ticker = r.get("Ticker", "")
        if r_ticker:
            r_market = r.get("Market", "")
            if normalize_ticker(r_ticker, r_market) == normalize_ticker(ticker, r_market):
                matches.append(r)
    return matches[-1] if matches else None


def append_record(record: dict):
    """追加一行新记录到 Sheet"""
    ws = _get_worksheet()
    # 写入时，如果 Ticker 是中国基金，强制写入标准化后的 6 位字符串
    ticker = record.get("Ticker", "")
    market = record.get("Market", "")
    if ticker:
        record["Ticker"] = normalize_ticker(ticker, market)
    row = [str(record.get(col, "")) for col in SHEET_COLUMNS]
    ws.append_row(row, value_input_option="RAW")
