
import logging
from clients import get_azure_openai, DEPLOYMENT

logger = logging.getLogger("SentimentBeast")


class SentimentBeast:
    """
    情绪猛兽：抓取今日真实财经新闻，经 Azure OpenAI 计算市场贪婪指数（1-100）
    """

    def _fetch_headlines(self) -> list:
        """从 akshare 获取今日 CCTV 财经资讯标题，失败时返回空列表"""
        try:
            import akshare as ak
            from datetime import date
            df = ak.news_cctv(date=date.today().strftime("%Y%m%d"))
            if df is not None and not df.empty:
                for col in ["summary", "摘要", "content", "内容", "title", "标题"]:
                    if col in df.columns:
                        return df[col].dropna().astype(str).head(6).tolist()
        except Exception as e:
            logger.warning(f"[SENTIMENT]: 实时新闻抓取失败({e})，将使用空输入")
        return []

    def get_market_sentiment(self) -> str:
        logger.info("[SENTIMENT]: 正在抓取今日财经资讯...")
        headlines = self._fetch_headlines()
        if not headlines:
            logger.warning("[SENTIMENT]: 无法获取实时新闻，返回中性默认值 65")
            return "65"

        prompt = (
            "分析以下今日财经新闻，给出 1-100 的市场贪婪指数（1=极度恐惧，100=极度贪婪），"
            "只返回一个整数：\n" + "\n".join(f"- {h}" for h in headlines)
        )
        try:
            response = get_azure_openai().chat.completions.create(
                model=DEPLOYMENT,
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=10,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"[SENTIMENT]: AI 调用失败({e})")
            return "65"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    beast = SentimentBeast()
    print(f"当前市场情绪分: {beast.get_market_sentiment()}")
