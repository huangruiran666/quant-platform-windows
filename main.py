import os
from pathlib import Path

from flask import Flask, jsonify


BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__)


@app.get("/")
def index():
    return jsonify(
        {
            "name": "quant-platform-windows",
            "mode": "service-shell",
            "desktop_entry": "python dashboard.py",
            "health_endpoint": "/healthz",
            "repo_root": str(BASE_DIR),
            "notes": [
                "Desktop GUI workflows live in dashboard.py.",
                "This Flask app provides a deployable health and metadata endpoint for cloud platforms.",
            ],
        }
    )


@app.get("/healthz")
def healthz():
    return jsonify({"status": "ok", "service": "quant-platform-windows"})


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
