import pandas as pd
import numpy as np
from clients import get_azure_openai, DEPLOYMENT
from data_router import get_stock_history

def get_a_share_data(symbol="600519"):
    """
    获取 A股 行情并计算技术指标
    """
    print(f"📈 [DATA]: Fetching {symbol} via DataRouter...")
    df = get_stock_history(symbol, start_date="20250101")
    # 统一收盘价列名
    if "收盘" not in df.columns and "close" in df.columns:
        df = df.rename(columns={"close": "收盘"})
    
    # 计算 MA5, MA20
    df['ma5'] = df['收盘'].rolling(window=5).mean()
    df['ma20'] = df['收盘'].rolling(window=20).mean()
    
    # 计算涨跌幅
    df['change_pct'] = df['收盘'].pct_change() * 100
    
    # 提取最近 3 天的关键数据
    latest_data = df.tail(3).to_dict(orient='records')
    return latest_data

def ai_expert_decision(symbol, data_summary):
    """
    调用东南亚 GPT-4o 节点进行深度决策
    """
    print(f"🧠 [AI-AGENT]: Consulting Southeast Asia GPT-4o Brain...")
    
    prompt = f"""
    你是一个专业的 A股 量化分析专家。
    标的: {symbol}
    最近三日量化指标: {data_summary}
    
    请基于以下 A股 逻辑进行分析：
    1. T+1 交易制度下的波段机会。
    2. 成交量与均线的配合（如缩量回踩或放量突破）。
    3. 情绪周期建议（如该股是否处于加速期或退潮期）。
    
    最后请给出明确的【决策建议】：(买入 / 持有 / 减仓 / 卖出) 并简述理由（使用中文）。
    """
    
    try:
        response = get_azure_openai().chat.completions.create(
            model=DEPLOYMENT,
            messages=[
                {"role": "system", "content": "你是一名精通 A股 市场和量化策略的高级基金经理。"},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI 决策失败: {str(e)}"

if __name__ == "__main__":
    # 示例：贵州茅台 (600519) 或 平安银行 (000001)
    target_stock = "600519" 
    data = get_a_share_data(target_stock)
    decision = ai_expert_decision(target_stock, data)
    
    print("\n" + "="*50)
    print(f"📊 [RUIRAN QUANT REPORT] FOR {target_stock}")
    print("="*50)
    print(decision)
    print("="*50)
