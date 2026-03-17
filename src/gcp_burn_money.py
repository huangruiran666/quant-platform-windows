"""
Main module for gcp_burn_money.py.
"""

from clients import get_bq_client, GCP_PROJECT

def start_burn():
    print(f"🔥 [GCP]: Upgrading to XGBoost Model (BOOSTED_TREE_REGRESSOR)...")
    # 使用 XGBoost 增强非线性预测能力，设置更大的树深度和学习率
    # 注意：训练数据来自 features_daily（英文列名），标签为 next_day_return
    sql = f"""
    CREATE OR REPLACE MODEL `{GCP_PROJECT}.A_Share_Singularity.market_predictor_v2`
    OPTIONS(
      model_type='BOOSTED_TREE_REGRESSOR',
      input_label_cols=['next_day_return'],
      max_iterations=50,
      learn_rate=0.1,
      booster_type='GBTREE',
      subsample=0.8
    ) AS
    SELECT
        next_day_return,
        pct_change, close, amount, turnover, volume,
        ma5, ma20, rsi_14, amount_ratio, relative_strength, golden_cross
    FROM `{GCP_PROJECT}.A_Share_Singularity.features_daily`
    WHERE next_day_return IS NOT NULL
    """
    try:
        client = get_bq_client()
        query_job = client.query(sql)
        query_job.result()  # 等待训练完成
        print("📡 [GCP]: Supercomputing cluster (XGBoost) is now training your A-share alpha model...")
        print("✅ [SUCCESS]: High-performance burn sequence initiated. Moving to non-linear intelligence.")
    except Exception as e:
        print(f"⚠️ [NOTICE]: {e}")

if __name__ == "__main__":
    import sys
    if "--confirm" not in sys.argv:
        print("⚠️  [GUARD]: 此操作将在 GCP BigQuery 上启动 XGBoost ML 训练，消耗云账单额度。")
        print("   确认执行请添加 --confirm 参数：")
        print("   python gcp_burn_money.py --confirm")
        sys.exit(0)
    start_burn()
