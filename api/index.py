import json
import os
from pathlib import Path
from time import monotonic

import httpx
from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from openai import OpenAI
from pydantic import BaseModel

RUNPOD_API_KEY = os.environ.get("RUNPOD_API_KEY")
ENDPOINT_ID = os.environ.get("ENDPOINT_ID")
MODEL_NAME = "aljalajil/saudi-judge-awq"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
with open(PROJECT_ROOT / "banned_tokens.json") as f:
    LOGIT_BIAS = {str(tid): -100 for tid in json.load(f)}

client = None
if RUNPOD_API_KEY and ENDPOINT_ID:
    client = OpenAI(
        api_key=RUNPOD_API_KEY,
        base_url=f"https://api.runpod.ai/v2/{ENDPOINT_ID}/openai/v1",
    )

app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


class ChatRequest(BaseModel):
    message: str


def stream_response(message: str):
    if not client:
        yield "data: Error: API not configured\n\n"
        yield "data: [DONE]\n\n"
        return

    stream = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "أنت القاضي السعودي، مساعد قانوني متخصص في الأنظمة والقوانين السعودية. أجب بشكل مفصل ودقيق باللغة العربية."
            },
            {
                "role": "user",
                "content": message
            }
        ],
        temperature=0.3,
        frequency_penalty=1.1,
        # presence_penalty=1.1, Could be used alongside frequency_penalty to prevent repetition by nudging the model to use new words and topics.
        logit_bias=LOGIT_BIAS,
        stream=True
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield f"data: {chunk.choices[0].delta.content}\n\n"

    yield "data: [DONE]\n\n"


@app.get("/")
async def root():
    return FileResponse(PROJECT_ROOT / "index.html")


@app.post("/api/chat")
async def chat(request: ChatRequest):
    return StreamingResponse(
        stream_response(request.message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


_http = httpx.AsyncClient(timeout=5)
_health_cache: dict = {"ts": 0.0, "val": {"worker_status": "no_workers"}}
_CACHE_TTL = 5.0


@app.get("/api/health")
async def health():
    if not client:
        return {"worker_status": "no_workers"}

    now = monotonic()
    if now - _health_cache["ts"] < _CACHE_TTL:
        return _health_cache["val"]

    try:
        resp = await _http.get(
            f"https://api.runpod.ai/v2/{ENDPOINT_ID}/health",
            headers={"Authorization": f"Bearer {RUNPOD_API_KEY}"},
        )
        workers = resp.json().get("workers", {})
    except Exception:
        return {"worker_status": "no_workers"}

    if workers.get("idle", 0) + workers.get("ready", 0) + workers.get("running", 0) > 0:
        result = {"worker_status": "ready"}
    elif workers.get("initializing", 0) > 0:
        result = {"worker_status": "initializing"}
    else:
        result = {"worker_status": "no_workers"}

    _health_cache.update(ts=now, val=result)
    return result
