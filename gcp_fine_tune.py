
from google.cloud import storage
from google.cloud import aiplatform
import json

project_id = "opportune-scope-428322-v3"
bucket_name = "ruiran-quant-training-2026"
region = "us-central1"

def setup_fine_tuning():
    # 1. 创建存储桶
    storage_client = storage.Client(project=project_id)
    try:
        bucket = storage_client.create_bucket(bucket_name, location=region)
        print(f"✅ [GCP]: Storage Bucket {bucket_name} created.")
    except Exception as e:
        print(f"⚠️ [NOTICE]: {e}")

    # 2. 生成精调数据 (模拟 A股 逻辑对)
    training_data = [
        {"input_text": "当 A股 出现千股跌停，缩量触底时，量化策略应如何反应？", "output_text": "应立即进入“冰点博弈”模式，寻找具有强力护盘资金的头部蓝筹，分批次进行左侧左侧建仓。"},
        {"input_text": "如何利用 300 美元 GCP 额度最大化量化收益？", "output_text": "开启全市场暴力回测与 BigQuery ML 模型训练，将资金转化为高胜率因子。"}
    ]
    
    file_path = "tuning_data.jsonl"
    with open(file_path, "w", encoding="utf-8") as f:
        for entry in training_data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    # 3. 上传数据
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob("training_v1.jsonl")
    blob.upload_from_filename(file_path)
    print(f"🔥 [GCP]: Training data uploaded. Ready to burn $300 on Fine-tuning!")

if __name__ == "__main__":
    import sys
    if "--confirm" not in sys.argv:
        print("⚠️  [GUARD]: 此操作将创建 GCS 存储桶并上传训练数据，准备消耗 Vertex AI 微调额度。")
        print("   确认执行请添加 --confirm 参数：")
        print("   python gcp_fine_tune.py --confirm")
        sys.exit(0)
    setup_fine_tuning()

