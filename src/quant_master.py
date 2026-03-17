"""
Main module for quant_master.py.
"""

import os
import sys
import pandas as pd
import json
from data_engine import FullSovereignEngine
from sentiment_beast import SentimentBeast
from clients import get_azure_openai, DEPLOYMENT
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class SingularityMassiveCore:
    def __init__(self):
        self.beast = SentimentBeast()

    def run_surgical_audit(self, target_stock=None):
        print(f"🌌 [SYSTEM]: 正在启动全维度审计 -> {target_stock if target_stock else '全量'}")
        
        # 调用 V23 最新引擎
        df_full, sectors, macro, vitals = FullSovereignEngine.get_omni_data()
        sentiment = self.beast.get_market_sentiment()
        
        if df_full.empty:
            print("❌ [FATAL]: 无法获取数据矩阵。")
            return

        # 定向定位
        if target_stock:
            df_target = df_full[df_full['名称'].astype(str).str.contains(target_stock)].head(1)
            if df_target.empty: df_target = df_full.head(3)
        else:
            df_target = df_full.head(5)

        result = {}
        try:
            payload = df_target.to_json(orient='records', force_ascii=False)
            prompt = f"环境:{macro}\n情绪:{sentiment}\n标的:{payload}\n请给出 10 字以内 [action] 指令和 500 字 [report]。格式: JSON"

            response = get_azure_openai().chat.completions.create(
                model=DEPLOYMENT,
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=1000,
            )
            raw = response.choices[0].message.content
            try:
                res = json.loads(raw)
                action = res.get("action", "执行审计")
                report = res.get("report", raw)
            except Exception:
                action = "建议观察"; report = raw

            result = {
                "time": datetime.now().strftime("%H:%M:%S"),
                "action": action,
                "report": report,
                "sentiment": sentiment,
                "macro": macro,
                "candidates": df_target[['名称', 'CORE_SCORE']].to_dict(orient='records'),
            }
            # 保留文件快照供外部工具使用
            try:
                with open(os.path.join(BASE_DIR, "cloud_decision.json"), "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
            print(f"✅ [DONE]: 决策完成 -> {action}")
        except Exception as e:
            print(f"❌ [AI ERROR]: {e}")
        return result

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    core = SingularityMassiveCore()
    core.run_surgical_audit(target)
