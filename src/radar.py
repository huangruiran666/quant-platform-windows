import pandas as pd
import numpy as np
from clients import get_azure_openai, DEPLOYMENT
from data_router import get_realtime_quotes

def get_market_radar():
    """
    全市场扫描器：从 A股 5000+ 股票中寻找活跃标的
    """
    print("📡 [RADAR]: Scanning 5000+ A-share stocks via DataRouter...")
    try:
        df = get_realtime_quotes()
        for col in ['涨跌幅', '成交额', '换手率']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        # 剔除 ST
        df = df[~df['名称'].astype(str).str.contains("ST", na=False)]
        # 涨幅过滤
        df = df[(df['涨跌幅'] > 1) & (df['涨跌幅'] < 8)]
        # 换手率过滤（新浪源可能为 NaN，跳过此过滤）
        if df['换手率'].notna().any():
            df = df[df['换手率'] > 3]
        top_list = df.sort_values(by=['成交额', '涨跌幅'], ascending=False).head(5)
        
        return top_list[['代码', '名称', '最新价', '涨跌幅', '换手率', '成交额']]
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()

def ai_portfolio_evaluator(stock_list):
    """
    让 GPT-4o 对筛选出的 5 只股票进行组合打分
    """
    print(f"🧠 [AI-MANAGER]: Sending TOP-5 Shortlist to Southeast Asia Brain...")
    
    summary = stock_list.to_string()
    
    prompt = f"""
    你是 Ruiran 的量化投资经理。这是我们今天初步筛选出的 5 只 A股 活跃标的：
    {summary}
    
    请结合你的 A股 市场经验（包含 T+1、主力资金流向和情绪周期）对这 5 只股进行深度评估：
    1. 哪一只最具备持续爆发潜力？
    2. 哪一只可能是“诱多陷阱”？
    3. 给出一个包含仓位建议的【明日操作指南】（中文）。
    
    请输出一份专业的 A股 奇点量化日报。
    """
    
    try:
        response = get_azure_openai().chat.completions.create(
            model=DEPLOYMENT,
            messages=[
                {"role": "system", "content": "你是一名精通 A股 全市场扫描和波段策略的顶级量化分析师。"},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI 决策失败: {str(e)}"

if __name__ == "__main__":
    print("="*60)
    print("✨ RUIRAN SINGULARITY QUANT: A-SHARE FULL MARKET SCANNER ✨")
    print("="*60)
    
    # 1. 全市场雷达扫描
    candidates = get_market_radar()
    
    if not candidates.empty:
        print(f"\n✅ [FOUND]: {len(candidates)} Active Stocks found.")
        print(candidates)
        
        # 2. 调用东南亚 AI 大脑进行组合评估
        report = ai_portfolio_evaluator(candidates)
        
        print("\n" + "#"*60)
        print("📊 [DAILY AI QUANT REPORT]")
        print("#"*60)
        print(report)
        print("#"*60)
    else:
        print("❌ [WARN]: No suitable stocks found today. Market might be in a cooling period.")
