# Runpod Endpoint Settings (vLLM)

Endpoint settings are configured in the Runpod UI (not in code). This documents the non-default values we rely on.

## Engine

- **Engine**: vLLM

## Hardware / Runtime

- **GPU memory**: 48 GB
- **Idle timeout**: 25 seconds

## Container

- **Image**: `madiatorlabs/worker-v1-vllm:v0.15.2`

## Environment variables (set in Runpod)

These are configured on the endpoint (not committed as secrets). For local runs, set the same values in your environment.

- **MODEL_NAME**: `aljalajil/saudi-judge-awq`
- **MAX_MODEL_LEN**: `8192`
- **MAX_NUM_SEQS**: `32`
- **ENABLE_LOG_REQUESTS**: `true` (added)
- **DISABLE_LOG_REQUESTS**: removed

## Advanced

- **Allowed CUDA versions**: `12.8`

## Notes

- Any settings not listed here are left at Runpod defaults.

