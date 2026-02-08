# Saudi Judge - القاضي السعودي

A fine-tuned **Qwen3-14B** model that predicts judicial rulings for Saudi court cases. Given the facts of a case, it generates the court's reasoning and verdict text for both first-instance and appeal courts.

To use the model please visit: **[القاضي السعودي — Saudi Judge](https://judge-deployment.vercel.app/)**

## Model Capabilities

- **First-instance courts**: takes case facts (الوقائع) and generates reasoning (الأسباب) and verdict text (نص الحكم).
- **Appeal courts**: takes the full first-instance judgment plus appeal facts and generates the appeal court's reasoning and verdict.
- Supports the thinking/reasoning mode inherited from Qwen3, visible in the chat UI as a collapsible "thinking" block.

### Training Data

The model was trained on **43,000+** judicial decisions scraped from the [Saudi Ministry of Justice judicial decisions portal](https://laws.moj.gov.sa/ar/JudicialDecisionsList/1?pageNumber=1&pageSize=12&viewType=grid&courtTypes=1&sortingBy=3), plus **~15,000** reasoning-augmented math examples, yes it is unrelated to our case but it is used to retain the reasoning capability of the model. The raw verdicts went through an extensive cleaning pipeline before training:

1. **Header normalization** — recognizing and standardizing section headers (الوقائع / الأسباب / نص الحكم) across dozens of aliases, bracketed forms, and corrupted variants.
2. **NER anonymization** — replacing person names, organizations, and locations with placeholders (`[PER-1]`, `[ORG-2]`, `[LOC-3]`) using CAMeL Tools NER, with special handling for judge signatures, proxy numbers, and invoice numbers.
3. **Text normalization** — Unicode reformatting, encoding fixes, tatweel stripping, Eastern-to-Western Arabic numeral conversion, Arabic comma/period structuring, and duplicate paragraph detection.
4. **Quality filtering** — NVIDIA NeMo Curator pipelines for deduplication and content-quality scoring.
5. **ChatML conversion** — structuring each case into user/assistant message pairs with task-specific instructions for first-instance and appeal court scenarios.

### Training Setup

| | |
|---|---|
| Base model | [Qwen3-14B](https://huggingface.co/Qwen/Qwen3-14B) (4-bit QLoRA via Unsloth) |
| Method | SFT with TRL |
| Quantization | AWQ 4-bit via llm-compressor for inference |
| HF model | [`aljalajil/saudi-judge-awq`](https://huggingface.co/aljalajil/saudi-judge-awq) |

## Deployment

Chat UI + API proxy for the **saudi-judge-awq** model running on a RunPod vLLM endpoint.

## Project Structure

```
├── api/index.py          # FastAPI backend (Vercel-compatible)
├── index.html            # Chat UI (Arabic RTL, streaming, think-tag support)
├── banned_tokens.json    # Token IDs suppressed via logit_bias
├── vercel.json           # Vercel build & route config
├── pyproject.toml        # Python dependencies
├── runpod_endpoint.py    # Standalone CLI test script
├── fix_config.py         # Patches HF config.json for vLLM compat
└── quantize_awq_llm-compressor.ipynb  # AWQ quantization notebook to use in vLLM
```

## Local Development

```powershell
& .venv\Scripts\Activate.ps1
$env:RUNPOD_API_KEY = "your-runpod-api-key"
$env:ENDPOINT_ID = "your-endpoint-id"
uvicorn api.index:app --reload --port 8000
```

Open http://localhost:8000/

## Vercel Deployment

1. Push to GitHub.
2. Import repo in Vercel — set **Root Directory** to this folder.
3. Add env vars: `RUNPOD_API_KEY`, `ENDPOINT_ID`.
4. Deploy.

## RunPod Endpoint Settings

Settings configured in the RunPod UI (not in code). Non-default values we rely on:

| Setting | Value |
|---|---|
| Engine | vLLM |
| GPU memory | 48 GB |
| Idle timeout | 60 s |
| Container image | `madiatorlabs/worker-v1-vllm:v0.15.2` |
| Allowed CUDA | 12.8 |

Environment variables (set on the endpoint, not committed):

| Variable | Value |
|---|---|
| MODEL_NAME | `aljalajil/saudi-judge-awq` |
| MAX_MODEL_LEN | `8192` |
| MAX_NUM_SEQS | `32` |
| ENABLE_LOG_REQUESTS | `true` |

Any settings not listed here are left at RunPod defaults.

## AWQ Quantization (for vLLM usage)

`quantize_awq_llm-compressor.ipynb` quantizes the 14B Qwen3 model to AWQ 4-bit using **llm-compressor**. Takes ~30-45 minutes on an A100 (40 GB) pod.

## Config Fix

`fix_config.py` downloads the model's `config.json` from Hugging Face and strips `scale_dtype` / `zp_dtype` fields that older vLLM workers don't support. Run it, then upload the patched file back to the repo.

## Banned Tokens

`banned_tokens.json` contains token IDs that are suppressed at generation time via `logit_bias: -100`. The API loads this file on startup and passes it to every chat completion request.

## Note
Cold start is mostly ~2 minutes.
When the model keeps generating open a new page.
