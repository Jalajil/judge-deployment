# Saudi Judge Deployment

A legal AI assistant specialized in Saudi Arabian laws and regulations.

## Local Development

```bash
# Install dependencies
uv sync

# Run the server
uv run uvicorn server:app --reload
```

Then open `chat_ui.html` in your browser.

## Vercel Deployment

The `api/`, `public/`, and `vercel.json` are configured for Vercel deployment.

1. Push to GitHub
2. Import repo in Vercel (set root directory to this folder)
3. Add environment variables: `RUNPOD_API_KEY`, `ENDPOINT_ID`
4. Deploy
