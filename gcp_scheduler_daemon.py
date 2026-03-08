"""
奇点量化 — 后台调度守护进程
无需管理员权限，开机自启，在后台安静运行。

任务表:
  周一至周五 15:45  →  gcp_daily_pipeline（注入+特征+打分）
  每周日    09:00   →  gcp_burn_money（BigQuery ML 再训练）
  每天      00:05   →  日志清理（保留最近30天）

此脚本由 start_singularity.vbs 静默启动，无控制台窗口。
"""
import schedule
import time
import logging
import os
import sys
from datetime import datetime

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "daemon.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [DAEMON] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("Daemon")


def job_daily_pipeline():
    """每个交易日盘后：注入 + 特征 + 打分"""
    now = datetime.now()
    # 跳过周末（schedule 库不支持直接设置 MON-FRI，用代码过滤）
    if now.weekday() >= 5:  # 5=Saturday, 6=Sunday
        logger.info("今日为周末，跳过日常管道")
        return
    logger.info("=== 启动日常管道 ===")
    try:
        from gcp_daily_pipeline import run
        run()
    except Exception as e:
        logger.error(f"日常管道异常: {e}", exc_info=True)


def job_weekly_train():
    """每周日：BigQuery ML 再训练"""
    logger.info("=== 启动每周 BigQuery ML 再训练 ===")
    try:
        from gcp_burn_money import start_burn
        start_burn()
    except Exception as e:
        logger.error(f"每周训练异常: {e}", exc_info=True)


def job_log_cleanup():
    """每天凌晨清理30天前的 pipeline.log 超长部分"""
    try:
        pipeline_log = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pipeline.log")
        if not os.path.exists(pipeline_log):
            return
        with open(pipeline_log, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if len(lines) > 5000:
            with open(pipeline_log, "w", encoding="utf-8") as f:
                f.writelines(lines[-5000:])
            logger.info(f"日志已裁剪至最近 5000 行")
    except Exception:
        pass


def run():
    logger.info("=" * 50)
    logger.info("奇点量化调度守护进程启动")
    logger.info(f"Python: {sys.executable}")
    logger.info(f"工作目录: {os.path.dirname(os.path.abspath(__file__))}")
    logger.info("=" * 50)

    # 注册任务
    schedule.every().day.at("15:45").do(job_daily_pipeline)
    schedule.every().sunday.at("09:00").do(job_weekly_train)
    schedule.every().day.at("00:05").do(job_log_cleanup)

    logger.info("已注册任务:")
    logger.info("  - 每日 15:45  →  日常管道（周末自动跳过）")
    logger.info("  - 每周日 09:00 →  BigQuery ML 再训练")
    logger.info("  - 每日 00:05  →  日志清理")
    logger.info("守护进程运行中，每60秒轮询一次...")

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    # 改变工作目录到脚本所在位置
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    run()
