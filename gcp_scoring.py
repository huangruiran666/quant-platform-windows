"""
Month 3 — Vertex AI 端点每日打分
由 gcp_daily_pipeline.py 自动调用，也可单独运行。

流程:
  1. 从 BigQuery features_daily 取最新一天特征
  2. 批量提交到 Vertex AI 在线端点
  3. 按预测收益率排序，过滤掉换手率 < 2% 的冷门股
  4. 写出 cloud_decision.json（供 dashboard 展示）
  5. 追加写入 BigQuery daily_predictions 表（用于回测复盘）

用法:
    python gcp_scoring.py            # 对今日数据打分
    python gcp_scoring.py --dry-run  # 只查询数据，不调用端点
"""
import json
import logging
import os
import sys
from datetime import datetime

import pandas as pd
from clients import get_bq_client, GCP_PROJECT

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("Scoring")

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
ENDPOINT_FILE = os.path.join(BASE_DIR, "endpoint_config.json")
DECISION_FILE = os.path.join(BASE_DIR, "cloud_decision.json")
DRY_RUN       = "--dry-run" in sys.argv

FEATURE_COLS = [
    "ma5", "ma10", "ma20",
    "mom_5d", "mom_10d", "mom_20d",
    "vol_10d", "vol_20d",
    "turnover", "avg_turnover_5d", "avg_turnover_20d",
    "amount_ratio",
    "rsi_14", "relative_strength",
    "golden_cross",
]

PRED_TABLE = f"{GCP_PROJECT}.A_Share_Singularity.daily_predictions"


def fetch_todays_features() -> pd.DataFrame:
    """从 BigQuery 取最新交易日的特征数据"""
    client = get_bq_client()
    query = f"""
        SELECT
            code, name, close, pct_change, turnover, rsi_14,
            {', '.join(FEATURE_COLS)}
        FROM `{GCP_PROJECT}.A_Share_Singularity.features_daily`
        WHERE trade_date = (
            SELECT MAX(trade_date)
            FROM `{GCP_PROJECT}.A_Share_Singularity.features_daily`
        )
        AND rsi_14 IS NOT NULL
        AND ma20 IS NOT NULL
        AND turnover > 0
    """
    df = client.query(query).to_dataframe()
    logger.info(f"[FETCH] 读取 {len(df):,} 支股票特征（最新交易日）")
    return df


def batch_predict(endpoint, df: pd.DataFrame) -> list:
    """分批调用端点，避免超出单次请求限制（最大 1.5MB）"""
    instances = df[FEATURE_COLS].fillna(0).to_dict(orient="records")
    predictions = []
    batch_size = 200  # 每次 200 条，约 50KB

    for i in range(0, len(instances), batch_size):
        batch = instances[i : i + batch_size]
        resp = endpoint.predict(instances=batch)
        preds = resp.predictions
        # AutoML 回归输出格式: [{"value": 1.23}] 或直接 [1.23]
        for p in preds:
            if isinstance(p, dict):
                predictions.append(p.get("value", 0.0))
            elif isinstance(p, list):
                predictions.append(p[0] if p else 0.0)
            else:
                predictions.append(float(p))

        logger.info(f"[PREDICT] 已完成 {min(i+batch_size, len(instances)):,}/{len(instances):,}")

    return predictions


def save_to_bq(df_scores: pd.DataFrame):
    """追加写入 BigQuery daily_predictions 表"""
    client = get_bq_client()
    from google.cloud import bigquery

    df_scores["prediction_date"] = datetime.now().date().isoformat()
    df_scores["predicted_at"] = datetime.now().isoformat()

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND",
        autodetect=True,
    )
    client.load_table_from_dataframe(df_scores, PRED_TABLE, job_config=job_config).result()
    logger.info(f"[BQ] {len(df_scores)} 条预测结果写入 {PRED_TABLE}")


def score_today():
    if not os.path.exists(ENDPOINT_FILE):
        logger.error("endpoint_config.json 不存在，请先运行 gcp_deploy_endpoint.py --deploy")
        return

    with open(ENDPOINT_FILE) as f:
        cfg = json.load(f)

    # 1. 取今日特征
    df = fetch_todays_features()
    if df.empty:
        logger.warning("[SCORE] 今日无特征数据，可能是非交易日或注入未完成")
        return

    if DRY_RUN:
        logger.info(f"[DRY-RUN] 读取到 {len(df)} 条数据，跳过端点调用")
        return

    # 2. 调用端点
    from google.cloud import aiplatform
    aiplatform.init(project=GCP_PROJECT, location="asia-southeast1")
    endpoint = aiplatform.Endpoint(cfg["endpoint_resource_name"])

    predictions = batch_predict(endpoint, df)
    df["ai_score"] = predictions

    # 3. 筛选：过滤 ST、换手率过低、模型分过低
    df_valid = df[
        ~df["name"].astype(str).str.contains("ST", na=False)
        & (df["turnover"] > 2.0)
        & (df["rsi_14"].between(30, 80))  # 避免极端超买超卖
    ].copy()

    top_picks = df_valid.nlargest(10, "ai_score")[
        ["code", "name", "close", "pct_change", "turnover", "rsi_14", "ai_score"]
    ]

    logger.info(f"[SCORE] Top 10 AI 选股结果:")
    for _, r in top_picks.iterrows():
        logger.info(
            f"  {r['code']} {r['name']:8s} | 现价={r['close']:.2f} | "
            f"今涨={r['pct_change']:.2f}% | RSI={r['rsi_14']:.1f} | AI分={r['ai_score']:.4f}"
        )

    # 4. 写出 cloud_decision.json
    result = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "source": "vertex_ai_endpoint",
        "model": cfg.get("model_resource_name", ""),
        "action": f"AI推荐 {len(top_picks)} 支",
        "report": top_picks.to_string(index=False),
        "candidates": top_picks[["code", "name", "ai_score"]].rename(
            columns={"ai_score": "CORE_SCORE"}
        ).to_dict(orient="records"),
    }
    with open(DECISION_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    logger.info(f"[SCORE] 决策快照已写出 → {DECISION_FILE}")

    # 5. 存 BigQuery 留作回测复盘
    save_to_bq(top_picks)

    return top_picks


if __name__ == "__main__":
    score_today()
