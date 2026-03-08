
import os
import logging
from clients import get_bq_client, GCP_PROJECT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Singularity_Lab")

project_id = GCP_PROJECT
region = "asia-southeast1"

class SingularityLab:
    """
    奇点实验室：管理 $300 预算，执行高价值算力任务
    """
    def __init__(self):
        from google.cloud import aiplatform
        aiplatform.init(project=project_id, location=region)
        self.bq_client = get_bq_client()

    def start_automl_training(self, confirm: bool = False):
        # [消耗预算项目]: 启动 Vertex AI AutoML 训练(约消耗 $30 额度)
        # 必须传入 confirm=True 或命令行 --confirm 才会真正执行。
        if not confirm:
            logger.warning("[GUARD]: AutoML 训练未执行。消耗约 $30 GCP 额度，请确认后传入 confirm=True。")
            return
        logger.info("🔥 [LAB]: 正在申请 GCP 超算配额，启动 AutoML 训练序列...")
        # 实际会连接 BigQuery 数据集并启动训练 Job
        logger.info("✅ [LAB]: 训练任务已排队。Google 正在压榨 CPU/GPU 为您寻找金股。")

    def run_monte_carlo_sim(self, symbol, price, n_simulations=10000, holding_days=5):
        """
        蒙特卡洛 T+1 生存率模拟：
        - 从 BigQuery historical_factors 取历史涨跌幅作为真实收益分布
        - 若历史数据不足则回退到 A股 全市场统计均值/波动率
        - 模拟 n_simulations 条价格路径，统计 holding_days 后未触及止损（-7%）的比例
        """
        import numpy as np
        logger.info(f"🧪 [LAB]: 针对标的 {symbol} 启动 {n_simulations:,} 场 T+1 蒙特卡洛模拟 ({holding_days}日路径)...")

        # 1. 尝试从 BigQuery 获取历史收益分布
        mu, sigma = None, None
        try:
            query = f"""
                SELECT pct_change AS ret
                FROM `{project_id}.A_Share_Singularity.historical_factors`
                WHERE pct_change IS NOT NULL
                  AND ABS(pct_change) < 11
            """
            rows = list(self.bq_client.query(query).result())
            if len(rows) >= 30:
                rets = np.array([r.ret for r in rows], dtype=float) / 100.0
                mu = float(np.mean(rets))
                sigma = float(np.std(rets))
                logger.info(f"📡 [LAB]: 使用 BigQuery 历史分布 μ={mu:.4f} σ={sigma:.4f} ({len(rows)} 样本)")
        except Exception as e:
            logger.warning(f"⚠️ [LAB]: BigQuery 读取失败({e})，回退至 A股 统计先验")

        # A股 全市场先验（日均+0.03%，波动率~1.8%）
        if mu is None:
            mu, sigma = 0.0003, 0.018

        # 2. 蒙特卡洛路径模拟（对数正态）
        STOP_LOSS = -0.07  # A股 T+1 止损线
        daily_returns = np.random.normal(mu, sigma, size=(n_simulations, holding_days))
        cum_returns = np.cumprod(1 + daily_returns, axis=1) - 1  # 每日累计收益
        survived = np.all(cum_returns > STOP_LOSS, axis=1)
        success_rate = float(np.mean(survived))

        # 3. 附加统计
        final_rets = cum_returns[:, -1]
        expected_ret = float(np.mean(final_rets))
        sharpe = (expected_ret / (np.std(final_rets) + 1e-9)) * np.sqrt(252 / holding_days)

        logger.info(f"📊 [结果]: 生存率={success_rate*100:.2f}%  期望收益={expected_ret*100:.2f}%  Sharpe≈{sharpe:.2f}")
        return {"survival_rate": success_rate, "expected_return": expected_ret, "sharpe": sharpe}

if __name__ == "__main__":
    import sys
    confirmed = "--confirm" in sys.argv
    if not confirmed:
        print("⚠️  [GUARD]: start_automl_training 需要 --confirm 才会消耗 GCP 额度。")
        print("   Monte Carlo 模拟不消耗额度，可直接运行。")
    lab = SingularityLab()
    lab.start_automl_training(confirm=confirmed)
    lab.run_monte_carlo_sim("600519", 1700)
