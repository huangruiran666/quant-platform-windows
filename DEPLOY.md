# Deployment Guide

This repository is a desktop-first project. The supported cloud deployment target is the lightweight Flask service in `main.py`, not the Tkinter GUI in `dashboard.py`.

## Local Desktop Mode

```bash
pip install -r requirements_gcp.txt
python dashboard.py
```

## Cloud Service Shell

The cloud entry point exposes:

- `GET /`
- `GET /healthz`

Use this when you want a deployable status shell or smoke-test target for Railway or Render.

## Railway

```bash
railway login
railway up
```

The repository already includes:

- `railway.toml`
- `Procfile`
- `main.py`

Expected start command:

```bash
gunicorn main:app --bind 0.0.0.0:$PORT
```

## Render

Suggested settings:

- Build command: `pip install -r requirements_gcp.txt`
- Start command: `gunicorn main:app --bind 0.0.0.0:$PORT`

## Environment Variables

Optional runtime configuration:

```text
AZURE_OPENAI_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_DEPLOYMENT=
GOOGLE_APPLICATION_CREDENTIALS=
GCP_PROJECT=
```

## Important Notes

- Do not try to launch the Tkinter GUI on headless cloud infrastructure.
- Keep secrets in platform environment variables, never in committed files.
- For analyst workflows, local execution remains the primary mode.
