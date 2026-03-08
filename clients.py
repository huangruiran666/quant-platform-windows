
"""
奇点量化 — 云端客户端单例工厂
所有模块统一从这里获取 Azure / GCP / Datadog 客户端。
凭证全部来自 .env 或 Doppler，禁止在源码中硬编码。
"""
import os
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5-nano")
GCP_PROJECT = "opportune-scope-428322-v3"


from datetime import date
import json

# 配额管理文件路径
QUOTA_FILE = os.path.join(os.path.dirname(__file__), "daily_quota.json")

def check_ai_quota():
    """检查并更新每日 AI 调用配额，防止额度瞬间烧光"""
    today = str(date.today())
    limit = 50 # 每日最大 50 次 AI 分析
    
    try:
        if os.path.exists(QUOTA_FILE):
            with open(QUOTA_FILE, 'r') as f:
                data = json.load(f)
        else:
            data = {}
            
        if data.get("date") != today:
            data = {"date": today, "count": 0}
            
        if data["count"] >= limit:
            print(f"🛑 [QUOTA EXCEEDED]: 今日 AI 调用已达上限 ({limit})，已触发自动熔断。")
            return False
            
        data["count"] += 1
        with open(QUOTA_FILE, 'w') as f:
            json.dump(data, f)
        return True
    except Exception as e:
        print(f"⚠️ [QUOTA ERROR]: {e}")
        return True # 出错时默认允许，防止阻塞业务

@lru_cache(maxsize=1)
def get_azure_openai():
    """全局共享的 AzureOpenAI 客户端"""
    if not check_ai_quota():
        return None
    from openai import AzureOpenAI
    return AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version=os.getenv("AZURE_API_VERSION", "2024-08-01-preview"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    )


@lru_cache(maxsize=1)
def get_bq_client():
    """全局共享的 BigQuery 客户端"""
    from google.cloud import bigquery
    return bigquery.Client(project=GCP_PROJECT)


@lru_cache(maxsize=1)
def get_cosmos_client():
    """全局共享的 Cosmos DB 客户端"""
    from azure.cosmos import CosmosClient
    url = os.getenv("COSMOS_ENDPOINT", "https://ruiran-quant-db.documents.azure.com:443/")
    key = os.getenv("COSMOS_KEY")
    if not key:
        return None
    return CosmosClient(url, key)


@lru_cache(maxsize=1)
def get_statsd():
    """获取 Datadog StatsD 客户端，上报量化指标"""
    try:
        from datadog import initialize, statsd
        options = {
            'statsd_host': os.getenv('DATADOG_AGENT_HOST', 'localhost'),
            'statsd_port': 8125
        }
        initialize(**options)
        return statsd
    except ImportError:
        class MockStatsd:
            def gauge(self, *args, **kwargs): pass
            def increment(self, *args, **kwargs): pass
            def timing(self, *args, **kwargs): pass
        return MockStatsd()
