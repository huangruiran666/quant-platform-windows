"""
Month 3 — Vertex AI 在线预测端点部署
将 AutoML 最优模型部署为 REST API，供 dashboard 实时调用。

n1-standard-2 端点: $0.0735/h × 24h × 30天 ≈ $52.92/月
建议 Month 3 前 24 天部署 → $42.34，控制在预算内

用法:
    python gcp_deploy_endpoint.py --deploy     # 部署端点（一次性，$42+）
    python gcp_deploy_endpoint.py --status     # 查看端点状态
    python gcp_deploy_endpoint.py --undeploy   # 月底关闭端点（停止计费）
    python gcp_deploy_endpoint.py --test       # 测试端点（发送样本请求）
"""
import sys
import json
import os
import logging
from datetime import datetime
from clients import GCP_PROJECT

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("DeployEndpoint")

REGION          = "asia-southeast1"
ENDPOINT_NAME   = "singularity-predictor-endpoint"
BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
MODELS_FILE     = os.path.join(BASE_DIR, "automl_models.json")
ENDPOINT_FILE   = os.path.join(BASE_DIR, "endpoint_config.json")
MACHINE_TYPE    = "n1-standard-2"  # $0.0735/h — 最小可用规格


def _load_best_model_resource():
    """从 automl_models.json 加载评估最优的模型资源名"""
    if not os.path.exists(MODELS_FILE):
        raise FileNotFoundError(
            "未找到 automl_models.json，请先运行 gcp_automl_launcher.py 完成训练"
        )
    with open(MODELS_FILE) as f:
        models = json.load(f)
    if not models:
        raise ValueError("automl_models.json 中没有模型记录")
    # 取最后一次训练的模型（可扩展为按 RMSE 排序）
    best = models[-1]
    logger.info(
        f"选用模型: Run#{best['run_id']} | {best['run_tag']} | "
        f"trained_at={best['trained_at']}"
    )
    return best["model_resource_name"]


def deploy():
    from google.cloud import aiplatform
    aiplatform.init(project=GCP_PROJECT, location=REGION)

    model_resource = _load_best_model_resource()
    model = aiplatform.Model(model_resource)

    logger.info(f"[1/3] 创建端点: {ENDPOINT_NAME}")
    endpoint = aiplatform.Endpoint.create(
        display_name=ENDPOINT_NAME,
        project=GCP_PROJECT,
        location=REGION,
    )
    logger.info(f"端点创建完成: {endpoint.resource_name}")

    logger.info(
        f"[2/3] 部署模型 → {MACHINE_TYPE}（预计 5-10 分钟）\n"
        f"      计费立即开始，月费约 $53，请 Month 3 末记得 --undeploy"
    )
    model.deploy(
        endpoint=endpoint,
        machine_type=MACHINE_TYPE,
        min_replica_count=1,
        max_replica_count=1,
        traffic_percentage=100,
        deployed_model_display_name=f"singularity_{datetime.now().strftime('%Y%m%d')}",
    )
    logger.info("[2/3] 部署完成")

    config = {
        "endpoint_resource_name": endpoint.resource_name,
        "endpoint_name": endpoint.name,
        "model_resource_name": model_resource,
        "machine_type": MACHINE_TYPE,
        "deployed_at": datetime.now().isoformat(),
        "estimated_monthly_cost_usd": 52.92,
    }
    with open(ENDPOINT_FILE, "w") as f:
        json.dump(config, f, indent=2)
    logger.info(f"[3/3] 端点配置已保存 → {ENDPOINT_FILE}")
    logger.info("下一步: python gcp_scoring.py  或  启动 dashboard 使用实时打分")


def status():
    if not os.path.exists(ENDPOINT_FILE):
        logger.info("endpoint_config.json 不存在，端点尚未部署")
        return
    with open(ENDPOINT_FILE) as f:
        cfg = json.load(f)

    from google.cloud import aiplatform
    aiplatform.init(project=GCP_PROJECT, location=REGION)
    endpoint = aiplatform.Endpoint(cfg["endpoint_resource_name"])

    deployed = endpoint.list_models()
    logger.info(f"端点: {cfg['endpoint_resource_name']}")
    logger.info(f"部署时间: {cfg['deployed_at']}")
    logger.info(f"预估月费: ${cfg['estimated_monthly_cost_usd']}")
    logger.info(f"已部署模型数: {len(deployed)}")
    for dm in deployed:
        logger.info(f"  - {dm.display_name} | traffic={dm.traffic_percentage}%")


def undeploy():
    if not os.path.exists(ENDPOINT_FILE):
        logger.info("endpoint_config.json 不存在，无需操作")
        return
    with open(ENDPOINT_FILE) as f:
        cfg = json.load(f)

    from google.cloud import aiplatform
    aiplatform.init(project=GCP_PROJECT, location=REGION)
    endpoint = aiplatform.Endpoint(cfg["endpoint_resource_name"])

    logger.info(f"[UNDEPLOY] 正在下线端点: {cfg['endpoint_resource_name']}")
    endpoint.undeploy_all()
    endpoint.delete()
    os.remove(ENDPOINT_FILE)
    logger.info("[UNDEPLOY] 端点已删除，计费停止")


def test_endpoint():
    if not os.path.exists(ENDPOINT_FILE):
        logger.error("端点尚未部署，请先运行 --deploy")
        return
    with open(ENDPOINT_FILE) as f:
        cfg = json.load(f)

    from google.cloud import aiplatform
    aiplatform.init(project=GCP_PROJECT, location=REGION)
    endpoint = aiplatform.Endpoint(cfg["endpoint_resource_name"])

    # 发送样本实例（茅台历史均值水平）
    sample = [{
        "ma5": 1680.0, "ma10": 1670.0, "ma20": 1660.0,
        "mom_5d": 1.2, "mom_10d": 2.1, "mom_20d": 3.5,
        "vol_10d": 1.8, "vol_20d": 1.9,
        "turnover": 0.35, "avg_turnover_5d": 0.32, "avg_turnover_20d": 0.30,
        "amount_ratio": 1.1,
        "rsi_14": 58.0, "relative_strength": 0.5,
        "golden_cross": "1.0",
    }]

    response = endpoint.predict(instances=sample)
    logger.info(f"[TEST] 样本预测结果: {response.predictions}")
    logger.info("[TEST] 端点工作正常")


if __name__ == "__main__":
    if "--deploy" in sys.argv:
        confirm = input(
            "即将部署 Vertex AI 在线预测端点，计费约 $53/月。确认? (yes/no): "
        ).strip().lower()
        if confirm != "yes":
            sys.exit(0)
        deploy()
    elif "--status" in sys.argv:
        status()
    elif "--undeploy" in sys.argv:
        confirm = input("确认下线端点并停止计费? (yes/no): ").strip().lower()
        if confirm != "yes":
            sys.exit(0)
        undeploy()
    elif "--test" in sys.argv:
        test_endpoint()
    else:
        print(__doc__)
