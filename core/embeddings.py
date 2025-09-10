# core/embeddings.py
import os
import requests

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1"

MODEL = "openai/text-embedding-3-small"

def get_embedding(text: str):
    """
    Get embedding vector for a given text chunk.
    Returns a list[float].
    """
    if not API_KEY:
        raise ValueError("OPENROUTER_API_KEY not found")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "input": text
    }

    resp = requests.post(f"{BASE_URL}/embeddings", headers=headers, json=payload, timeout=60)
    if resp.status_code != 200:
        raise RuntimeError(f"Embedding API error {resp.status_code}: {resp.text}")

    data = resp.json()
    return data["data"][0]["embedding"]

def get_embedding_dimension():
    """Return embedding dimension for this model."""
    return 1536  # text-embedding-3-small has 1536 dims
