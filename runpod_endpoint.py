from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

# 1. Set your values
RUNPOD_API_KEY = os.environ["RUNPOD_API_KEY"]
ENDPOINT_ID = os.environ["ENDPOINT_ID"]
MODEL_NAME = "aljalajil/saudi-judge-awq"

# 2. Create OpenAI-compatible client pointing to Runpod
client = OpenAI(
    api_key=RUNPOD_API_KEY,
    base_url=f"https://api.runpod.ai/v2/{ENDPOINT_ID}/openai/v1"
)

# 3. Send a chat completion request
# Create a streaming chat completion request
stream = client.chat.completions.create(
    model=MODEL_NAME,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a short poem about stars."}
    ],
    temperature=0.7,
    max_tokens=200,
    stream=True  # Enable streaming
)

# Print the streaming response
print("Response: ", end="", flush=True)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
print()