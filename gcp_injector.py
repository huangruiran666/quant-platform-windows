
import os
import pandas as pd
from google.cloud import bigquery
from google.api_core import exceptions
import logging
from data_router import get_realtime_quotes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GCP_Injector")

# 初始化
project_id = "opportune-scope-428322-v3"
dataset_id = "A_Share_Singularity"
table_id = "historical_factors"
client = bigquery.Client(project=project_id)

def ensure_dataset_exists():
    dataset_ref = client.dataset(dataset_id)
    try:
        client.get_dataset(dataset_ref)
        logger.info(f"✅ Dataset {dataset_id} exists.")
    except exceptions.NotFound:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "asia-southeast1"
        client.create_dataset(dataset)
        logger.info(f"✨ Created new dataset: {dataset_id}")

# data_router 已输出标准中文列名，这里统一转英文供 BigQuery 使用
_BQ_COLS = {
    "代码": "code", "名称": "name", "最新价": "close",
    "涨跌幅": "pct_change", "成交额": "amount",
    "成交量": "volume", "换手率": "turnover",
}

def inject_data():
    ensure_dataset_exists()
    full_table_id = f"{project_id}.{dataset_id}.{table_id}"

    try:
        logger.info("📡 Fetching A-share data via DataRouter...")
        df = get_realtime_quotes(force_refresh=True)
        if df.empty:
            raise ValueError("DataRouter: 所有数据源均不可用")

        # 列名转英文
        df = df.rename(columns={k: v for k, v in _BQ_COLS.items() if k in df.columns})
        # 全量5000+，不截断
        df["trade_date"] = pd.Timestamp.now().date().isoformat()
        df["update_time"] = pd.Timestamp.now()

        # 写入策略：WRITE_APPEND 追加，按 update_time 分区，3个月积累历史数据
        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_APPEND",
            autodetect=True,
            time_partitioning=bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY,
                field="update_time",
            ),
        )
        
        logger.info(f"🔥 Injecting to {full_table_id}...")
        job = client.load_table_from_dataframe(df, full_table_id, job_config=job_config)
        job.result() # 等待完成
        logger.info("✅ GCP Infusion Successful.")
        
    except Exception as e:
        logger.error(f"❌ GCP Injector Error: {e}")

if __name__ == "__main__":
    inject_data()
