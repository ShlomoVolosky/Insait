# Insurance Vehicle-Info API

A small HTTP API that, given an Israeli license plate, returns vehicle details
(manufacturer, model, year, color). This is **Part A** of the Insait home
assignment. Built with FastAPI on a hexagonal (ports & adapters) architecture.

## Requirements

- Python 3.12

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run locally

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

- Health check: `GET /health` → `{"status": "ok"}`

## Tests

```bash
pytest
```
# Insait, stage 2 - phase A
