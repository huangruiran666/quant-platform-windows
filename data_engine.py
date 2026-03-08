
import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime
from data_router import get_realtime_quotes, get_sector_quotes
from clients import get_statsd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OmniMatrix_v23")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class FullSovereignEngine:
    """
    全维度数据引擎：为全息指挥舱提供宏观、行业、个股及算力快照
    接入 GitHub Student Pack (Datadog & Scrapy Cloud) 增强。
    """
    COLS = ['代码', '名称', '最新价', '涨跌幅', '成交额', 'CORE_SCORE']

    @staticmethod
    def _compute_core_score(df: pd.DataFrame) -> pd.Series:
        """
        真实因子合成分（0-100）：
          - 涨跌幅 30%  — 价格动能
          - 换手率 30%  — 市场活跃度
          - 成交额 40%  — 流动性/资金关注度
        """
        weights = [('涨跌幅', 0.30), ('换手率', 0.30), ('成交额', 0.40)]
        score = pd.Series(0.0, index=df.index)
        for col, w in weights:
            if col in df.columns:
                s = pd.to_numeric(df[col], errors='coerce').fillna(0)
                score += s.rank(pct=True) * w * 100
        return score.clip(0, 100)

    @staticmethod
    def get_omni_data():
        logger.info("📡 [OMNI]: 正在启动全维度数据采集协议...")
        statsd = get_statsd() # 📡 Datadog 监控
        
        # 初始化基础结构
        df_stocks = pd.DataFrame(columns=FullSovereignEngine.COLS)
        sectors = [{"名称":"扫描中", "涨跌幅":0}]
        macro = {}
        vitals = {}

        # 1. 获取全盘个股（多源路由，自动切换 Zyte/Sina/Local）
        df_raw = get_realtime_quotes()
        if df_raw is not None and not df_raw.empty:
            df_raw['CORE_SCORE'] = FullSovereignEngine._compute_core_score(df_raw)
            
            # 🚀 [DATADOG]: 推送市场平均因子分
            avg_score = df_raw['CORE_SCORE'].mean()
            statsd.gauge('quant.core_score.avg', avg_score)
            statsd.increment('quant.engine.run')
            
            df_stocks = df_raw[df_raw.columns.intersection(FullSovereignEngine.COLS)].copy()
            for c in FullSovereignEngine.COLS:
                if c not in df_stocks.columns:
                    df_stocks[c] = 0.0
            logger.info(f"✅ [SUCCESS]: 实时数据就绪，{len(df_stocks)} 支")
        else:
            df_stocks = pd.DataFrame([{"代码":"000001","名称":"数据断连","最新价":0,"涨跌幅":0,"成交额":0,"CORE_SCORE":0}])

        # 2. 获取板块热力
        sectors = get_sector_quotes() or sectors

        # 3. 真实宏观数据
        macro = FullSovereignEngine._fetch_macro(df_stocks)

        # 4. 真实算力体征（延迟探针）
        vitals = FullSovereignEngine._measure_vitals()
        
        # 🚀 [DATADOG]: 推送算力延迟
        try:
            latency = float(vitals.get("AZURE_LATENCY", "0ms").replace("ms", ""))
            statsd.timing('quant.azure.latency', latency)
        except: pass

        return df_stocks, sectors, macro, vitals

    @staticmethod
    def _fetch_macro(df_stocks: pd.DataFrame) -> dict:
        macro = {"USD_CNH": "---", "A50_FUT": "---", "NAS100": "---", "US10Y_BOND": "---"}
        try:
            a50 = df_stocks[df_stocks['代码'].astype(str) == '513050']
            if not a50.empty:
                macro["A50_FUT"] = str(a50.iloc[0].get('最新价', '---'))
        except Exception: pass
        return macro

    @staticmethod
    def _measure_vitals() -> dict:
        import time, os, requests
        vitals = {"AZURE_LATENCY": "---ms", "GCP_PROJECT": "opportune-scope-428322-v3", "ENERGY_TIER": "ACTIVE"}
        try:
            endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
            if endpoint:
                t0 = time.time()
                requests.head(endpoint, timeout=5)
                ms = int((time.time() - t0) * 1000)
                vitals["AZURE_LATENCY"] = f"{ms}ms"
        except Exception: pass
        return vitals

if __name__ == "__main__":
    stocks, _, _, _ = FullSovereignEngine.get_omni_data()
    print(stocks.head())
