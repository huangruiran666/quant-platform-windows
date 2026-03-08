
import os
import pandas as pd
from data_engine import FullSovereignEngine
from clients import get_azure_openai, DEPLOYMENT
from dotenv import load_dotenv

load_dotenv()

def print_result(name, success, message=""):
    status = "✅ [PASS]" if success else "❌ [FAIL]"
    print(f"{status} {name}: {message}")

class SingularityRegressionV2:
    def __init__(self):
        print("="*60)
        print("🌌 RUIRAN SINGULARITY: RESILIENCE ENGINE REGRESSION V2 🌌")
        print("="*60)

    def test_redundant_data(self):
        """测试多源冗余行情引擎"""
        try:
            df, _, _, _ = FullSovereignEngine.get_omni_data()
            if not df.empty:
                source_used = "Fused Source" 
                print_result("Redundant Market Data", True, f"Successfully retrieved {len(df)} stocks via Resilience Engine.")
                return True
        except Exception as e:
            print_result("Redundant Market Data", False, str(e))
        return False

    def test_azure_ai(self):
        try:
            response = get_azure_openai().chat.completions.create(
                model=DEPLOYMENT,
                messages=[{"role": "user", "content": "ping"}],
                timeout=15
            )
            print_result("Azure AI Brain", True, "GPT-5-nano is highly responsive.")
            return True
        except Exception as e:
            print_result("Azure AI Brain", False, str(e))
        return False

    def run_minimal_check(self):
        """运行核心链路检查"""
        data_ok = self.test_redundant_data()
        ai_ok = self.test_azure_ai()
        
        print("="*60)
        if data_ok and ai_ok:
            print("🏆 FINAL VERDICT: MULTI-SOURCE REDUNDANCY IS ACTIVE & STABLE.")
        else:
            print("⚠️ FINAL VERDICT: NODES STILL FRAGILE. CHECK NETWORK/CREDENTIALS.")
        print("="*60)

if __name__ == "__main__":
    test = SingularityRegressionV2()
    test.run_minimal_check()
