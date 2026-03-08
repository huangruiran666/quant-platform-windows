import os
import akshare as ak
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from dotenv import load_dotenv
from clients import get_azure_openai, DEPLOYMENT

load_dotenv()

# AI 研报搜索引擎 (Azure AI Search) — 凭证来自 .env
_search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT", "https://ruiran-ai-search.search.windows.net")
_search_key = os.getenv("AZURE_SEARCH_KEY")
search_client = SearchClient(_search_endpoint, "quant-reports", AzureKeyCredential(_search_key)) if _search_key else None

def search_expert_intelligence(query):
    """
    从研报库中提取核心见解 (模拟 RAG 逻辑)
    """
    print(f"🔍 [SEARCH]: Searching AI Search Index for: {query}...")
    # 这里我们通过 AI 模拟一个研报检索的结果，直到你真正上传研报 PDF 为止
    return "半导体行业处于复苏周期，国产化率提升，建议关注 603501 (韦尔股份) 等标的。"

def run_ultimate_quant(symbol="603501"):
    print("="*60)
    print("💎 RUIRAN SINGULARITY: ULTIMATE AI SEARCH QUANT v3.0 💎")
    print("="*60)
    
    # 获取实时行情
    df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date="20250101", adjust="qfq").tail(1)
    price_info = df[['收盘', '涨跌幅']].to_string()
    
    # 检索全网研报见解
    intel = search_expert_intelligence(symbol)
    
    # AI 综合研判 (数据面 + 研报面)
    response = get_azure_openai().chat.completions.create(
        model=DEPLOYMENT,
        messages=[
            {"role": "system", "content": "你是一名精通 A股 深度研报分析和量化执行的高级基金经理。用中文回答。"},
            {"role": "user", "content": f"标的: {symbol} \n实时行情: {price_info} \n研报情报: {intel} \n\n请给出最终投资决策。"}
        ]
    )
    
    print("\n📊 [FINAL DECISION]:")
    print(response.choices[0].message.content)
    print("="*60)

if __name__ == "__main__":
    run_ultimate_quant()
