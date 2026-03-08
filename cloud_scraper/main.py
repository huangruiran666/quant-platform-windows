
import os
import akshare as ak
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def scrape():
    # 高并发抓取逻辑
    try:
        df = ak.stock_zh_a_spot_em().head(10)
        return jsonify(df.to_dict(orient="records"))
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

