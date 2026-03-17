"""
Main module for gcp_init.py.
"""

from google.cloud import bigquery
from google.api_core import exceptions

# 初始化 GCP 大数据客户端
project_id = "opportune-scope-428322-v3"
client = bigquery.Client(project=project_id)

def init_reactor():
    dataset_id = f"{project_id}.A_Share_Singularity"
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = "asia-southeast1" # 离你最近
    
    try:
        print(f"📡 [GCP]: Attempting to create BigQuery Dataset: A_Share_Singularity...")
        dataset = client.create_dataset(dataset, timeout=30)
        print(f"✅ [SUCCESS]: Dataset {dataset.dataset_id} created in GCP!")
    except exceptions.Conflict:
        print(f"✅ [EXIST]: Dataset already exists, ready for data infusion.")
    except Exception as e:
        print(f"❌ [ERROR]: {e}")

if __name__ == "__main__":
    init_reactor()

