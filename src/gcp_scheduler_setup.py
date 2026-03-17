"""
Month 1 — 自动化调度配置
双轨制：
  A) Windows Task Scheduler（本地，立即可用）
  B) Cloud Scheduler + Cloud Run Job（云端，可选）

用法:
    python gcp_scheduler_setup.py --local     # 只配置 Windows Task Scheduler
    python gcp_scheduler_setup.py --cloud     # 只配置 Cloud Scheduler（需 gcloud CLI）
    python gcp_scheduler_setup.py             # 两者都配置
"""
import subprocess
import sys
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("SchedulerSetup")

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
PYTHON_EXE    = sys.executable
PIPELINE_SCRIPT = os.path.join(BASE_DIR, "gcp_daily_pipeline.py")
GCP_PROJECT   = "opportune-scope-428322-v3"
REGION        = "asia-southeast1"


# ─── A: Windows Task Scheduler ────────────────────────────────────────────────

def setup_windows_scheduler():
    """
    创建 Windows 计划任务：
      - SingularityQuant_DailyPipeline: 周一至周五 15:45 运行完整管道
      - SingularityQuant_WeeklyTrain:  每周日 09:00 触发 BigQuery ML 再训练
    """
    tasks = [
        {
            "name": "SingularityQuant_DailyPipeline",
            "cmd": f'"{PYTHON_EXE}" "{PIPELINE_SCRIPT}"',
            "schedule": "WEEKLY",
            "days": "MON,TUE,WED,THU,FRI",
            "time": "15:45",
            "desc": "奇点量化 每日盘后管道（注入+特征+打分）",
        },
        {
            "name": "SingularityQuant_WeeklyTrain",
            "cmd": f'"{PYTHON_EXE}" "{os.path.join(BASE_DIR, "gcp_burn_money.py")}" --confirm',
            "schedule": "WEEKLY",
            "days": "SUN",
            "time": "09:00",
            "desc": "奇点量化 每周 BigQuery ML 再训练",
        },
    ]

    for t in tasks:
        cmd = [
            "schtasks", "/create", "/f",
            "/tn", t["name"],
            "/tr", t["cmd"],
            "/sc", t["schedule"],
            "/d", t["days"],
            "/st", t["time"],
            "/rl", "HIGHEST",
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, shell=False)
            if result.returncode == 0:
                logger.info(f"[WIN-SCHED] 已创建: {t['name']} @ {t['time']} ({t['days']})")
            else:
                logger.error(f"[WIN-SCHED] 创建失败: {t['name']}\n{result.stderr}")
        except Exception as e:
            logger.error(f"[WIN-SCHED] 异常: {e}")

    logger.info("[WIN-SCHED] 验证已创建的任务:")
    subprocess.run(["schtasks", "/query", "/tn", "SingularityQuant_DailyPipeline", "/fo", "LIST"])


# ─── B: Cloud Scheduler (需要 gcloud CLI 已登录) ──────────────────────────────

def deploy_cloud_run_job():
    """
    将 gcp_daily_pipeline.py 打包为 Cloud Run Job。
    需要 Docker 和 gcloud CLI。
    """
    dockerfile_path = os.path.join(BASE_DIR, "Dockerfile.pipeline")
    if not os.path.exists(dockerfile_path):
        # 自动生成最小化 Dockerfile
        with open(dockerfile_path, "w") as f:
            f.write(f"""FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements_gcp.txt
CMD ["python", "gcp_daily_pipeline.py"]
""")
        logger.info(f"[CLOUD] Dockerfile.pipeline 已生成: {dockerfile_path}")

    image = f"gcr.io/{GCP_PROJECT}/singularity-pipeline:latest"

    logger.info(f"[CLOUD] 构建并推送镜像: {image}")
    subprocess.run(["gcloud", "builds", "submit", "--tag", image, BASE_DIR], check=True)

    logger.info("[CLOUD] 创建 Cloud Run Job: singularity-daily-pipeline")
    subprocess.run([
        "gcloud", "run", "jobs", "create", "singularity-daily-pipeline",
        "--image", image,
        "--region", REGION,
        "--project", GCP_PROJECT,
        "--memory", "1Gi",
        "--task-timeout", "1800",  # 30 分钟超时
    ], check=True)
    logger.info("[CLOUD] Cloud Run Job 创建完成")


def setup_cloud_scheduler():
    """创建 Cloud Scheduler 任务触发 Cloud Run Job（每个交易日 15:45 CST = 07:45 UTC）"""
    jobs = [
        {
            "name": "singularity-daily-pipeline",
            "schedule": "45 7 * * 1-5",  # UTC 07:45 = CST 15:45，周一至周五
            "description": "奇点量化 每日盘后管道",
            "uri": (
                f"https://{REGION}-run.googleapis.com/apis/run.googleapis.com/v1"
                f"/namespaces/{GCP_PROJECT}/jobs/singularity-daily-pipeline:run"
            ),
        },
    ]

    for j in jobs:
        cmd = [
            "gcloud", "scheduler", "jobs", "create", "http", j["name"],
            "--schedule", j["schedule"],
            "--uri", j["uri"],
            "--time-zone", "UTC",
            "--location", REGION,
            "--project", GCP_PROJECT,
            "--message-body", "{}",
            "--oauth-service-account-email",
            f"scheduler-sa@{GCP_PROJECT}.iam.gserviceaccount.com",
            "--description", j["description"],
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"[CLOUD-SCHED] 已创建: {j['name']} @ {j['schedule']} UTC")
            else:
                # 可能已存在，尝试更新
                cmd[4] = "update"
                subprocess.run(cmd, check=True)
                logger.info(f"[CLOUD-SCHED] 已更新: {j['name']}")
        except Exception as e:
            logger.error(f"[CLOUD-SCHED] 异常: {e}")


def generate_gcp_requirements():
    """生成 GCP 专用 requirements 文件（用于 Cloud Run 镜像构建）"""
    reqs = [
        "akshare>=1.18.35",
        "google-cloud-bigquery>=3.40.1",
        "google-cloud-aiplatform>=1.140.0",
        "google-cloud-storage>=3.9.0",
        "pandas>=2.0.0",
        "numpy>=1.26.0",
        "python-dotenv>=1.2.2",
        "db-dtypes>=1.0.0",         # BigQuery → pandas 类型转换
        "pyarrow>=14.0.0",          # BigQuery parquet 传输
    ]
    path = os.path.join(BASE_DIR, "requirements_gcp.txt")
    with open(path, "w") as f:
        f.write("\n".join(reqs) + "\n")
    logger.info(f"[SETUP] requirements_gcp.txt 已生成: {path}")


if __name__ == "__main__":
    mode_local = "--local" in sys.argv or "--local" in sys.argv or len(sys.argv) == 1
    mode_cloud = "--cloud" in sys.argv or len(sys.argv) == 1

    generate_gcp_requirements()

    if mode_local:
        logger.info("=== 配置 Windows Task Scheduler ===")
        setup_windows_scheduler()

    if mode_cloud:
        logger.info("=== 配置 Cloud Run Job + Cloud Scheduler ===")
        try:
            deploy_cloud_run_job()
            setup_cloud_scheduler()
        except Exception as e:
            logger.warning(f"Cloud 配置需要 gcloud CLI 和 Docker: {e}")
            logger.info("提示: 先运行 'gcloud auth login' 和 'gcloud auth configure-docker'")
