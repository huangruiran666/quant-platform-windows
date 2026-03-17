"""
Month 1+ — 每日自动化管道
运行顺序: 注入全量行情 → BigQuery 特征工程 → [Month 3] Vertex AI 打分 → 写出决策
建议每个交易日 15:45 触发（收盘 15:30 后 15 分钟）

用法:
    python gcp_daily_pipeline.py          # 完整运行
    python gcp_daily_pipeline.py --dry-run # 只检查连通性，不写入
"""
import logging
import sys
import os
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "pipeline.log"),
            encoding="utf-8",
        ),
    ],
)
logger = logging.getLogger("DailyPipeline")

DRY_RUN = "--dry-run" in sys.argv


def step_inject():
    from gcp_injector import inject_data
    if DRY_RUN:
        logger.info("[DRY-RUN] 跳过注入")
        return
    logger.info("[1/3] 注入今日 A股 全量行情 → BigQuery...")
    inject_data()


def step_features():
    from gcp_feature_engineer import FeatureEngineer
    if DRY_RUN:
        logger.info("[DRY-RUN] 跳过特征工程")
        return
    logger.info("[2/3] 运行 BigQuery SQL 特征工程...")
    fe = FeatureEngineer()
    fe.compute_features()


def step_score():
    endpoint_cfg = os.path.join(os.path.dirname(os.path.abspath(__file__)), "endpoint_config.json")
    if not os.path.exists(endpoint_cfg):
        logger.info("[3/3] endpoint_config.json 不存在，跳过打分（Month 3 部署后生效）")
        return
    if DRY_RUN:
        logger.info("[DRY-RUN] 跳过打分")
        return
    logger.info("[3/3] Vertex AI 端点打分...")
    from gcp_scoring import score_today
    score_today()


def run():
    now = datetime.now()
    logger.info(f"{'='*60}")
    logger.info(f"奇点量化 日盘后管道  {now.strftime('%Y-%m-%d %H:%M:%S')}  DRY_RUN={DRY_RUN}")
    logger.info(f"{'='*60}")

    try:
        step_inject()
        step_features()
        step_score()
        elapsed = (datetime.now() - now).total_seconds()
        logger.info(f"管道完成，耗时 {elapsed:.1f}s")
    except Exception as e:
        logger.error(f"管道异常终止: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    run()
