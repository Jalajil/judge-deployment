# Saudi Judge — vLLM Deployment

Chat UI + API proxy for the **saudi-judge-awq** model running on a RunPod vLLM endpoint.

## Project Structure

```
deploy/runpod/vllm/
├── api/index.py          # FastAPI backend (Vercel-compatible)
├── index.html            # Chat UI (Arabic RTL, streaming, think-tag support)
├── banned_tokens.json    # Token IDs suppressed via logit_bias
├── vercel.json           # Vercel build & route config
├── pyproject.toml        # Python dependencies
├── runpod_endpoint.py    # Standalone CLI test script
├── fix_config.py         # Patches HF config.json for vLLM compat
├── quantize_awq_llm-compressor.ipynb  # AWQ quantization notebook
└── RUNPOD.md             # RunPod endpoint settings reference
```

## Local Development

From the project root:

```powershell
& .venv311\Scripts\Activate.ps1
$env:RUNPOD_API_KEY = "your-runpod-api-key"
$env:ENDPOINT_ID = "your-endpoint-id"
cd deploy\runpod\vllm
uvicorn api.index:app --reload --port 8001
```

Open http://localhost:8001/

## Vercel Deployment

1. Push to GitHub.
2. Import repo in Vercel — set **Root Directory** to `deploy/runpod/vllm`.
3. Add env vars: `RUNPOD_API_KEY`, `ENDPOINT_ID`.
4. Deploy.

## RunPod Endpoint Settings

Endpoint settings are configured in the RunPod UI (not in code). See [RUNPOD.md](RUNPOD.md) for full details.

| Setting | Value |
|---|---|
| Engine | vLLM |
| GPU memory | 48 GB |
| Idle timeout | 25 s |
| Container image | `madiatorlabs/worker-v1-vllm:v0.15.2` |
| MODEL_NAME | `aljalajil/saudi-judge-awq` |
| MAX_MODEL_LEN | 8192 |
| MAX_NUM_SEQS | 32 |
| Allowed CUDA | 12.8 |

## AWQ Quantization

`quantize_awq_llm-compressor.ipynb` quantizes the 14B Qwen3 model to AWQ 4-bit using **llm-compressor**. Requires an A100 (40 GB+) pod and takes ~30-45 minutes.

## Config Fix

`fix_config.py` downloads the model's `config.json` from Hugging Face and strips `scale_dtype` / `zp_dtype` fields that older vLLM workers don't support. Run it, then upload the patched file back to the repo.

## Banned Tokens

`banned_tokens.json` contains token IDs that are suppressed at generation time via `logit_bias: -100`. The API loads this file on startup and passes it to every chat completion request.
