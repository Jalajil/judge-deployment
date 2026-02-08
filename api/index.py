import json
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "configured": client is not None,
    }
