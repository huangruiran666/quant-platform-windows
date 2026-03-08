
import os
import sys
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CamberBatch")

def main():
    print("="*65)
    print("📊 CAMBER BATCH FACTOR AUDIT — 盘后因子智能审计 🌌")
    print("="*65)
    
    # 1. 加载最新的行情数据
    cache_path = os.path.join(os.path.dirname(__file__), "../full_market_cache.csv")
    if not os.path.exists(cache_path):
        logger.error(f"找不到行情缓存: {cache_path}")
        return

    try:
        df = pd.read_csv(cache_path).head(10) # 选取前10个作为样本进行分析
        summary = df[['名称', '最新价', '涨跌幅', '成交额']].to_string()
    except Exception as e:
        logger.error(f"读取数据失败: {e}")
        return

    # 2. 构建专家指令
    prompt = f"这是今天的 A 股头部活跃标的数据采样：\n{summary}\n\n" \
             f"基于这些数据，请以资深量化研究员的身份分析：\n" \
             f"1. 目前成交额集中度是否过高？\n" \
             f"2. 动能因子（涨跌幅）和流动性因子（成交额）哪个更具解释力？\n" \
             f"3. 给出明天开盘的调仓建议建议。"

    # 3. 提交至 Camber 专家
    print("🚀 [BATCH]: 正在将 75GB 离线数据与分析任务提交至 Camber 科学计算云...")
    # 这里通过系统调用 Camber CLI，你也可以改用 SDK 调用
    os.system(f'camber agent ask data_expert "{prompt}"')

if __name__ == "__main__":
    main()
