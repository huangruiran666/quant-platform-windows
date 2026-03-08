"""
Month 2 — Vertex AI AutoML Tabular 训练启动器
消费计划:
  Run #1 (4月初):  budget_hours=24 → $38.40  使用30天积累数据
  Run #2 (4月中):  budget_hours=8  → $12.80  调整特征集，验证泛化

用法:
    python gcp_automl_launcher.py --run 1   # Run #1, 24小时, $38.40
    python gcp_automl_launcher.py --run 2   # Run #2, 8小时,  $12.80
    python gcp_automl_launcher.py --list    # 列出所有已训练模型及评估指标
"""
import sys
import json
import logging
import os
from datetime import datetime
from clients import GCP_PROJECT

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AutoML_Launcher")

REGION      = "asia-southeast1"
DATASET_BQ  = f"bq://{GCP_PROJECT}.A_Share_Singularity.features_daily"
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
MODELS_FILE = os.path.join(BASE_DIR, "automl_models.json")

# 特征列配置（与 gcp_feature_engineer.py 和 gcp_scoring.py 保持一致）
FEATURE_COLS = {
    "ma5":              "numeric",
    "ma10":             "numeric",
    "ma20":             "numeric",
    "mom_5d":           "numeric",
    "mom_10d":          "numeric",
    "mom_20d":          "numeric",
    "vol_10d":          "numeric",
    "vol_20d":          "numeric",
    "turnover":         "numeric",
    "avg_turnover_5d":  "numeric",
    "avg_turnover_20d": "numeric",
    "amount_ratio":     "numeric",
    "rsi_14":           "numeric",
    "relative_strength":"numeric",
    "golden_cross":     "categorical",
}

RUN_CONFIG = {
    1: {"budget_hours": 24, "cost": 38.40, "desc": "Run #1 — 全特征集，30天数据"},
    2: {"budget_hours": 8,  "cost": 12.80, "desc": "Run #2 — 精选特征集，验证泛化"},
}


def check_data_readiness() -> int:
    """检查 features_daily 表数据量是否足够"""
    from clients import get_bq_client
    client = get_bq_client()
    query = f"""
        SELECT
            COUNT(DISTINCT trade_date) AS days,
            COUNT(*) AS rows,
            MIN(trade_date) AS from_date,
            MAX(trade_date) AS to_date
        FROM `{GCP_PROJECT}.A_Share_Singularity.features_daily`
    """
    row = list(client.query(query).result())[0]
    logger.info(
        f"[DATA CHECK] {row.days} 交易日, {row.rows:,} 行, "
        f"日期范围: {row.from_date} ~ {row.to_date}"
    )
    if row.days < 15:
        logger.warning(f"[DATA CHECK] 数据量不足（{row.days}天 < 建议15天）")
    return row.days


def launch_automl(run_id: int = 1):
    from google.cloud import aiplatform

    cfg = RUN_CONFIG[run_id]
    logger.info(
        f"{'='*60}\n"
        f"AutoML {cfg['desc']}\n"
        f"预计费用: ${cfg['cost']:.2f}  训练时长: {cfg['budget_hours']}h\n"
        f"{'='*60}"
    )

    days = check_data_readiness()
    if days < 10:
        logger.error("数据不足10天，请先运行 gcp_daily_pipeline.py 积累数据")
        sys.exit(1)

    aiplatform.init(project=GCP_PROJECT, location=REGION)

    run_tag = f"run{run_id}_{datetime.now().strftime('%Y%m%d_%H%M')}"

    # 1. 创建 BQ 数据集引用
    logger.info(f"[1/3] 创建 Vertex AI Dataset: {run_tag}")
    dataset = aiplatform.TabularDataset.create(
        display_name=f"a_share_features_{run_tag}",
        bq_source=DATASET_BQ,
    )
    logger.info(f"Dataset created: {dataset.resource_name}")

    # 2. 配置训练任务
    feature_cols = dict(FEATURE_COLS)
    if run_id == 2:
        # Run #2: 只用 Run #1 中重要性较高的特征（训练后手动确认）
        drop_low_importance = ["vol_20d", "mom_10d", "avg_turnover_20d"]
        feature_cols = {k: v for k, v in feature_cols.items() if k not in drop_low_importance}

    job = aiplatform.AutoMLTabularTrainingJob(
        display_name=f"singularity_automl_{run_tag}",
        optimization_prediction_type="regression",
        optimization_objective="minimize-rmse",
        column_specs=feature_cols,
    )

    # 3. 启动训练
    logger.info(f"[2/3] 启动 AutoML 训练 (budget={cfg['budget_hours']}h)... 去睡一觉吧")
    model = job.run(
        dataset=dataset,
        target_column="next_day_return",
        budget_milli_node_hours=cfg["budget_hours"] * 1000,
        model_display_name=f"a_share_predictor_{run_tag}",
        training_fraction_split=0.8,
        validation_fraction_split=0.1,
        test_fraction_split=0.1,
        predefined_split_column_name=None,
    )
    logger.info(f"[2/3] 训练完成: {model.resource_name}")

    # 4. 获取评估指标
    logger.info("[3/3] 获取模型评估指标...")
    try:
        evals = model.list_model_evaluations()
        for ev in evals:
            metrics = dict(ev.metrics)
            logger.info(f"评估指标: {json.dumps(metrics, indent=2, default=str)}")
    except Exception as e:
        logger.warning(f"评估指标获取失败: {e}")
        metrics = {}

    # 5. 保存模型信息
    models_log = []
    if os.path.exists(MODELS_FILE):
        with open(MODELS_FILE) as f:
            models_log = json.load(f)

    entry = {
        "run_id": run_id,
        "run_tag": run_tag,
        "budget_hours": cfg["budget_hours"],
        "cost_usd": cfg["cost"],
        "model_resource_name": model.resource_name,
        "dataset_resource_name": dataset.resource_name,
        "metrics": metrics,
        "trained_at": datetime.now().isoformat(),
    }
    models_log.append(entry)
    with open(MODELS_FILE, "w") as f:
        json.dump(models_log, f, indent=2, default=str)

    logger.info(f"模型信息已保存到 {MODELS_FILE}")
    logger.info(f"下一步: python gcp_deploy_endpoint.py  (Month 3 部署上线)")
    return model


def list_models():
    """列出所有已训练模型"""
    if not os.path.exists(MODELS_FILE):
        logger.info("未找到 automl_models.json，尚未训练任何模型")
        return
    with open(MODELS_FILE) as f:
        models = json.load(f)
    logger.info(f"共 {len(models)} 个已训练模型:")
    for m in models:
        logger.info(
            f"  Run#{m['run_id']} | {m['run_tag']} | "
            f"${m['cost_usd']} | {m.get('metrics', {})}"
        )


if __name__ == "__main__":
    if "--list" in sys.argv:
        list_models()
    else:
        run_id = 1
        if "--run" in sys.argv:
            idx = sys.argv.index("--run")
            run_id = int(sys.argv[idx + 1])
        if run_id not in RUN_CONFIG:
            print(f"无效 run id: {run_id}，可选: {list(RUN_CONFIG.keys())}")
            sys.exit(1)
        cfg = RUN_CONFIG[run_id]
        print(f"\n即将启动 AutoML {cfg['desc']}")
        print(f"预计费用: ${cfg['cost']:.2f}，训练时长约 {cfg['budget_hours']} 小时")
        confirm = input("确认启动? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("已取消")
            sys.exit(0)
        launch_automl(run_id)
