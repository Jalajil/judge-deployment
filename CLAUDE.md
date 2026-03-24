# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Saudi Judge (القاضي السعودي) is a chat UI + API proxy for a fine-tuned Qwen3-14B model (AWQ 4-bit) that predicts Saudi court rulings. The model runs on a RunPod vLLM endpoint; this repo is the web frontend and API layer deployed to Vercel.

## Commands

```bash
# Activate venv and run locally
source .venv/Scripts/activate        # PowerShell: & .venv\Scripts\Activate.ps1
uvicorn api.index:app --reload --port 8000

# Install dependencies (uses uv)
uv sync
```

Requires env vars `RUNPOD_API_KEY` and `ENDPOINT_ID` (set in `.env` locally, in Vercel dashboard for prod).

## Architecture

**Single-page app with a FastAPI backend, both deployed to Vercel.**

- `api/index.py` - FastAPI app. Three endpoints:
  - `GET /` serves `index.html`
  - `POST /api/chat` accepts `{ message }`, streams SSE responses from the RunPod vLLM endpoint using the OpenAI client
  - `GET /api/health` proxies RunPod worker health with a 5-second in-memory cache
- `index.html` - Self-contained chat UI (HTML/CSS/JS in one file). Arabic RTL layout, dark theme, SSE streaming, collapsible `<think>` block rendering, chat persistence via localStorage.
- `banned_tokens.json` - Token IDs applied as `logit_bias: -100` on every request to suppress unwanted tokens.
- `vercel.json` - Routes all `/api/*` to the Python function, everything else to static HTML.

The API uses the OpenAI SDK pointed at RunPod's OpenAI-compatible endpoint (`https://api.runpod.ai/v2/{ENDPOINT_ID}/openai/v1`). Generation params: temperature=0.4, frequency_penalty=1.6, presence_penalty=1.1.

## Utility Scripts (not part of deployment)

- `fix_config.py` - Downloads HF model config and strips `scale_dtype`/`zp_dtype` for vLLM compatibility.
- `quantize_awq_llm-compressor.ipynb` - AWQ quantization notebook for creating the model weights.

## Writing Style

Never use em dashes in any written copy or text content. Use commas, periods, or other punctuation instead.
