"""
奇点量化 — 多源数据路由器
解决东方财富 API 被限流/封锁问题。

优先级:
  实时全市场: 新浪财经(akshare) → baostock日线 → 本地缓存
  单股历史:   baostock → akshare历史 → 本地缓存

特性:
  - 5分钟内存缓存，避免重复请求
  - 指数退避重试（最多3次）
  - 失败自动切下一个源
  - 每次成功都刷新本地磁盘缓存（地堡备份）
  - 列名标准化（不同源输出统一格式）
"""
import logging
import os
import time
import functools
import pandas as pd
import numpy as np

logger = logging.getLogger("DataRouter")

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(BASE_DIR, "full_market_cache.csv")
CACHE_TTL  = 300   # 内存缓存5分钟

# 标准列（所有源归一化到此格式）
STD_COLS = ["代码", "名称", "最新价", "涨跌幅", "成交额", "成交量", "换手率"]

_mem_cache: dict = {}   # {"realtime": (timestamp, df)}


# ─── 工具 ─────────────────────────────────────────────────────────────────────

def _retry(fn, attempts=3, base_wait=2.0):
    """指数退避重试，失败抛最后一次异常"""
    last_exc = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as e:
            last_exc = e
            wait = base_wait * (2 ** i)
            logger.warning(f"[RETRY {i+1}/{attempts}] {fn.__name__ if hasattr(fn,'__name__') else '?'}: {e}，{wait:.0f}s 后重试")
            time.sleep(wait)
    raise last_exc


def _cache_valid(key: str) -> bool:
    if key not in _mem_cache:
        return False
    ts, _ = _mem_cache[key]
    return (time.time() - ts) < CACHE_TTL


def _save_cache(df: pd.DataFrame):
    try:
        df.to_csv(CACHE_FILE, index=False, encoding="utf-8-sig")
    except Exception as e:
        logger.debug(f"缓存写入失败: {e}")


def _load_cache() -> pd.DataFrame:
    if os.path.exists(CACHE_FILE):
        try:
            df = pd.read_csv(CACHE_FILE, encoding="utf-8-sig", dtype=str).fillna("0")
            logger.warning(f"[CACHE] 使用本地磁盘缓存: {CACHE_FILE} ({len(df)} 行)")
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=STD_COLS)


# ─── 数据源实现 ───────────────────────────────────────────────────────────────

def _from_sina() -> pd.DataFrame:
    """新浪财经全市场实时行情（akshare stock_zh_a_spot）"""
    import akshare as ak
    df = ak.stock_zh_a_spot()
    if df is None or df.empty:
        raise ValueError("新浪接口返回空数据")
    # 新浪列名映射到标准列
    rename = {
        "代码": "代码", "名称": "名称",
        "最新价": "最新价", "涨跌幅": "涨跌幅",
        "成交额": "成交额", "成交量": "成交量",
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
    df["换手率"] = np.nan   # 新浪无换手率
    logger.info(f"[SINA] 获取 {len(df)} 支股票实时行情")
    return df


def _from_baostock_batch() -> pd.DataFrame:
    """
    baostock 当日 K 线批量拉取沪深全市场（约 5000 支）
    适合盘后 15:45 调用，返回当日收盘数据
    """
    import baostock as bs
    rs_login = bs.login()
    if rs_login.error_code != "0":
        raise ConnectionError(f"baostock login 失败: {rs_login.error_msg}")

    try:
        # 获取所有 A 股代码
        rs_list = bs.query_all_stock(day=pd.Timestamp.now().strftime("%Y-%m-%d"))
        codes = []
        while rs_list.error_code == "0" and rs_list.next():
            row = rs_list.get_row_data()
            codes.append(row[0])   # sh.600519 格式

        today = pd.Timestamp.now().strftime("%Y-%m-%d")
        fields = "date,code,open,high,low,close,volume,amount,turn,pctChg"
        records = []
        # 批量查询（每次最多1支，baostock 无批量接口，但速度较快）
        # 限制500支防止超时，盘后全量用 gcp_injector 的新浪源
        for code in codes[:500]:
            rs = bs.query_history_k_data_plus(
                code, fields,
                start_date=today, end_date=today,
                frequency="d", adjustflag="3"
            )
            while rs.error_code == "0" and rs.next():
                records.append(rs.get_row_data())

        if not records:
            raise ValueError("baostock 当日数据为空（可能是非交易日）")

        df = pd.DataFrame(records, columns=fields.split(","))
        df["code"] = df["code"].str.replace(r"^(sh|sz)\.", "", regex=True)
        df = df.rename(columns={
            "code": "代码", "close": "最新价", "pctChg": "涨跌幅",
            "amount": "成交额", "volume": "成交量", "turn": "换手率",
        })
        # 补全名称列（baostock 无名称）
        df["名称"] = ""
        logger.info(f"[BAOSTOCK] 批量获取 {len(df)} 支股票当日 K 线")
        return df

    finally:
        bs.logout()


def _from_sina_single(symbol: str) -> pd.DataFrame:
    """新浪单股实时行情（akshare）"""
    import akshare as ak
    # stock_zh_a_spot 全量里筛选，或用实时接口
    df = ak.stock_bid_ask_em(symbol=symbol)
    return df


def _from_baostock_hist(symbol: str, start_date: str = "20250101") -> pd.DataFrame:
    """baostock 单股历史 K 线（含换手率、涨跌幅）"""
    import baostock as bs
    # baostock 要求 YYYY-MM-DD 格式
    if len(start_date) == 8 and "-" not in start_date:
        start_date = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:]}"
    login_rs = bs.login()
    if login_rs is None or login_rs.error_code != "0":
        raise ConnectionError(f"baostock login 失败: {getattr(login_rs, 'error_msg', 'None')}")
    try:
        code = f"sh.{symbol}" if symbol.startswith("6") else f"sz.{symbol}"
        rs = bs.query_history_k_data_plus(
            code,
            "date,code,open,high,low,close,volume,amount,turn,pctChg",
            start_date=start_date,
            frequency="d", adjustflag="3"
        )
        if rs is None:
            raise ValueError(f"baostock 返回 None，symbol={symbol}")
        records = []
        while rs.error_code == "0" and rs.next():
            records.append(rs.get_row_data())
        df = pd.DataFrame(records, columns=[
            "日期", "代码", "开盘", "最高", "最低", "收盘",
            "成交量", "成交额", "换手率", "涨跌幅"
        ])
        df["收盘"] = pd.to_numeric(df["收盘"], errors="coerce")
        df["涨跌幅"] = pd.to_numeric(df["涨跌幅"], errors="coerce")
        df["换手率"] = pd.to_numeric(df["换手率"], errors="coerce")
        logger.info(f"[BAOSTOCK] {symbol} 历史 K 线 {len(df)} 行")
        return df
    finally:
        bs.logout()


def _from_akshare_hist(symbol: str, start_date: str = "20250101") -> pd.DataFrame:
    """akshare 单股历史 K 线（备用）"""
    import akshare as ak
    start = start_date.replace("-", "")
    df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start, adjust="qfq")
    df = df.rename(columns={"收盘": "收盘", "涨跌幅": "涨跌幅", "成交额": "成交额", "换手率": "换手率"})
    return df


# ─── 公开 API ─────────────────────────────────────────────────────────────────

def get_realtime_quotes(force_refresh: bool = False) -> pd.DataFrame:
    """
    获取全市场实时行情（标准化格式）。
    内存缓存5分钟，自动多源切换，优先顺序：新浪财经 -> baostock。
    """
    if not force_refresh and _cache_valid("realtime"):
        logger.info("[CACHE] 使用内存缓存实时行情")
        return _mem_cache["realtime"][1]

    sources = [
        ("新浪财经", _from_sina),
        ("baostock批量", _from_baostock_batch),
    ]

    for name, fn in sources:
        try:
            logger.info(f"[ROUTER] 尝试数据源: {name}")
            df = _retry(fn, attempts=2, base_wait=3.0)
            # 标准化数值列
            for col in ["最新价", "涨跌幅", "成交额", "成交量", "换手率"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
            _mem_cache["realtime"] = (time.time(), df)
            _save_cache(df)
            logger.info(f"[ROUTER] 成功: {name} → {len(df)} 行")
            return df
        except Exception as e:
            logger.warning(f"[ROUTER] {name} 失败: {e}")

    # 所有源失败 → 磁盘缓存兜底
    logger.error("[ROUTER] 所有实时数据源失败，使用磁盘缓存")
    return _load_cache()


def get_stock_history(symbol: str, start_date: str = "20250101") -> pd.DataFrame:
    """
    获取单股历史 K 线（标准化格式）。
    baostock 优先（含换手率），akshare 备用。
    """
    sources = [
        ("baostock历史", lambda: _from_baostock_hist(symbol, start_date)),
        ("akshare历史", lambda: _from_akshare_hist(symbol, start_date)),
    ]
    for name, fn in sources:
        try:
            logger.info(f"[ROUTER] {symbol} 历史数据: 尝试 {name}")
            df = _retry(fn, attempts=2, base_wait=2.0)
            if not df.empty:
                logger.info(f"[ROUTER] {symbol} → {name}: {len(df)} 行")
                return df
        except Exception as e:
            logger.warning(f"[ROUTER] {name} 失败: {e}")

    logger.error(f"[ROUTER] {symbol} 历史数据所有源失败")
    return pd.DataFrame()


def get_sector_quotes() -> list:
    """
    获取板块热力数据。
    新浪板块 → 东方财富板块（若恢复）→ 空列表
    """
    try:
        import akshare as ak
        df = ak.stock_board_industry_name_em()
        top = df.sort_values("涨跌幅", ascending=False).head(8) if "涨跌幅" in df.columns else df.head(8)
        return top[["板块名称", "涨跌幅"]].rename(
            columns={"板块名称": "名称"}
        ).to_dict(orient="records")
    except Exception as e:
        logger.warning(f"[ROUTER] 板块数据失败: {e}")
        return []


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    print("=== 数据路由器自检 ===")
    df = get_realtime_quotes()
    print(f"全市场行情: {len(df)} 行")
    print(df.head(3).to_string())
    print()
    df2 = get_stock_history("600519")
    print(f"600519 历史: {len(df2)} 行")
    print(df2.tail(3).to_string())
