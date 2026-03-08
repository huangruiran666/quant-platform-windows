"""
Month 1 — BigQuery 特征工程
每日注入完成后运行，在 BQ 里计算 MA/RSI/动量/量比等因子，
生成带 next_day_return 标签的 features_daily 表供 AutoML 使用。
"""
import logging
from clients import get_bq_client, GCP_PROJECT

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("FeatureEngineer")

DATASET      = "A_Share_Singularity"
RAW_TABLE    = f"{GCP_PROJECT}.{DATASET}.historical_factors"
FEAT_TABLE   = f"{GCP_PROJECT}.{DATASET}.features_daily"

FEATURE_SQL = f"""
CREATE OR REPLACE TABLE `{FEAT_TABLE}` AS
WITH base AS (
    SELECT
        trade_date,
        CAST(code       AS STRING)  AS code,
        name,
        CAST(close      AS FLOAT64) AS close,
        CAST(pct_change AS FLOAT64) AS pct_change,
        CAST(amount     AS FLOAT64) AS amount,
        CAST(turnover   AS FLOAT64) AS turnover,
        CAST(volume     AS FLOAT64) AS volume,
    FROM `{RAW_TABLE}`
    WHERE close IS NOT NULL AND CAST(close AS FLOAT64) > 0
),
windowed AS (
    SELECT *,
        -- 均线
        AVG(close) OVER w5   AS ma5,
        AVG(close) OVER w10  AS ma10,
        AVG(close) OVER w20  AS ma20,
        -- 价格动量
        (close - LAG(close, 5)  OVER wc) / NULLIF(LAG(close, 5)  OVER wc, 0) * 100 AS mom_5d,
        (close - LAG(close, 10) OVER wc) / NULLIF(LAG(close, 10) OVER wc, 0) * 100 AS mom_10d,
        (close - LAG(close, 20) OVER wc) / NULLIF(LAG(close, 20) OVER wc, 0) * 100 AS mom_20d,
        -- 波动率
        STDDEV(pct_change) OVER w10 AS vol_10d,
        STDDEV(pct_change) OVER w20 AS vol_20d,
        -- 成交量因子
        AVG(amount) OVER w5  AS avg_amount_5d,
        AVG(amount) OVER w20 AS avg_amount_20d,
        amount / NULLIF(AVG(amount) OVER w20, 0) AS amount_ratio,
        -- 换手率均值
        AVG(turnover) OVER w5  AS avg_turnover_5d,
        AVG(turnover) OVER w20 AS avg_turnover_20d,
        -- RSI 原料（简化：14日平均涨跌）
        AVG(CASE WHEN pct_change > 0 THEN pct_change ELSE 0.0 END) OVER w14 AS avg_gain_14,
        AVG(CASE WHEN pct_change < 0 THEN ABS(pct_change) ELSE 0.0 END) OVER w14 AS avg_loss_14,
        -- 市场整体当日均值（横截面特征）
        AVG(pct_change) OVER wd   AS market_avg_pct,
        STDDEV(pct_change) OVER wd AS market_std_pct,
        -- 标签：次日涨跌幅
        LEAD(pct_change, 1) OVER wc AS next_day_return,
    FROM base
    WINDOW
        wc  AS (PARTITION BY code ORDER BY trade_date),
        wd  AS (PARTITION BY trade_date),
        w5  AS (PARTITION BY code ORDER BY trade_date ROWS BETWEEN 4  PRECEDING AND CURRENT ROW),
        w10 AS (PARTITION BY code ORDER BY trade_date ROWS BETWEEN 9  PRECEDING AND CURRENT ROW),
        w14 AS (PARTITION BY code ORDER BY trade_date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW),
        w20 AS (PARTITION BY code ORDER BY trade_date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW)
)
SELECT
    *,
    -- RSI_14
    100 - (100 / (1 + NULLIF(avg_gain_14, 0) / NULLIF(avg_loss_14, 1e-10))) AS rsi_14,
    -- 金叉信号
    CASE WHEN ma5 > ma20 THEN 1.0 ELSE 0.0 END AS golden_cross,
    -- 相对强弱（个股动量 vs 市场均值）
    (pct_change - market_avg_pct) / NULLIF(market_std_pct, 0) AS relative_strength
FROM windowed
WHERE
    ma20 IS NOT NULL
    AND next_day_return IS NOT NULL
    AND ABS(next_day_return) < 11  -- 过滤涨跌停极端值，避免污染标签
    AND turnover > 0
"""

class FeatureEngineer:
    def __init__(self):
        self.client = get_bq_client()

    def compute_features(self):
        logger.info(f"[FEAT]: 开始计算特征，目标表: {FEAT_TABLE}")
        try:
            job = self.client.query(FEATURE_SQL)
            job.result()  # 等待完成
            # 查询行数确认
            count_job = self.client.query(f"SELECT COUNT(*) AS n FROM `{FEAT_TABLE}`")
            rows = list(count_job.result())
            n = rows[0].n if rows else 0
            logger.info(f"[FEAT]: 特征表更新完成，共 {n:,} 行。")
        except Exception as e:
            logger.error(f"[FEAT]: 特征计算失败: {e}")
            raise

    def get_latest_stats(self) -> dict:
        """返回最新一天的特征表统计，用于健康检查"""
        query = f"""
            SELECT
                MAX(trade_date) AS latest_date,
                COUNT(DISTINCT trade_date) AS total_days,
                COUNT(DISTINCT code) AS total_stocks,
                ROUND(AVG(rsi_14), 2) AS avg_rsi,
                ROUND(AVG(next_day_return), 4) AS avg_next_day_return
            FROM `{FEAT_TABLE}`
        """
        row = list(self.client.query(query).result())[0]
        stats = dict(row)
        logger.info(f"[FEAT]: 最新统计 -> {stats}")
        return stats


if __name__ == "__main__":
    fe = FeatureEngineer()
    fe.compute_features()
    fe.get_latest_stats()
