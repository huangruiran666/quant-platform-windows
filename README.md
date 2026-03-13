# Singularity Quant Trading Platform

[![Python](https://img.shields.io/badge/Python-3.13-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Mode](https://img.shields.io/badge/Mode-Desktop%20First-0ea5e9)](.)

Desktop-first AI quant trading platform focused on market scanning, analyst workflows, and multi-provider integrations for A-share and broader macro research.

## What This Repo Actually Provides

- Local Tkinter command center in `dashboard.py`
- Strategy and analysis modules such as `quant_master.py`, `radar.py`, and `a_share_quant.py`
- GCP helper scripts for pipelines, scheduling, and scoring
- Scrapy-based collector under `cloud_scraper/`
- A lightweight Flask `main.py` for cloud deployment smoke checks and health endpoints

## Quick Start

```bash
git clone https://github.com/huangruiran666/quant-platform-windows.git
cd quant-platform-windows
pip install -r requirements_gcp.txt
python dashboard.py
```

If you prefer `uv`:

```bash
pip install uv
uv sync
uv run python dashboard.py
```

## Running Modes

- `python dashboard.py`: launch the local desktop cockpit
- `python main.py`: run the lightweight Flask service shell locally
- `gunicorn main:app --bind 0.0.0.0:$PORT`: deploy the Flask shell on Railway / Render

## Environment Variables

Optional integrations:

- `AZURE_OPENAI_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_DEPLOYMENT`
- `GOOGLE_APPLICATION_CREDENTIALS`
- `GCP_PROJECT`

If these are not set, parts of the project can still run with local or public data sources.

## Repository Layout

```text
quant-platform-windows/
├── dashboard.py
├── main.py
├── quant_master.py
├── radar.py
├── a_share_quant.py
├── data_engine.py
├── data_router.py
├── clients.py
├── cloud_scraper/
├── camber_expert/
├── gcp_*.py
├── Dockerfile
├── Procfile
├── render.yaml
├── railway.toml
└── requirements_gcp.txt
```

## Deployment Notes

- The desktop GUI is for local analyst use and is not suitable for headless cloud runtimes.
- Cloud deployment is intentionally limited to the Flask status shell in `main.py`.
- Platform-specific deployment details live in `DEPLOY.md`.

## Cleanup Notes

- Local chat transcripts under `src/chats/` were removed from version control.
- Repository metadata and package naming were aligned with the actual project name.
- Web deployment entry points now point to a real Flask application instead of a placeholder script.

## License

MIT
