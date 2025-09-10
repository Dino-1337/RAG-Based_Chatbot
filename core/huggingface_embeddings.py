import os
import requests
from langchain_core.embeddings import Embeddings
from config.settings import HUGGINGFACE_API_TOKEN, EMBEDDING_MODEL_NAME

class HuggingFaceAPIEmbeddings(Embeddings):
    """Custom embeddings class that uses Hugging Face Inference API."""

    def __init__(self, api_token=None, model_name=EMBEDDING_MODEL_NAME):
        self.api_token = api_token or HUGGINGFACE_API_TOKEN
        self.model_name = model_name
        if not self.api_token:
            raise ValueError("Hugging Face API token is required. Set HUGGINGFACE_API_TOKEN environment variable.")

    def embed_documents(self, texts):
        """Embed a list of documents."""
        embeddings = []
        for text in texts:
            embedding = self.embed_query(text)
            embeddings.append(embedding)
        return embeddings

    def embed_query(self, text):
        """Embed a single query."""
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": text
        }

        response = requests.post(
            f"https://api-inference.huggingface.co/models/{self.model_name}",
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code != 200:
            raise RuntimeError(f"Hugging Face API error {response.status_code}: {response.text}")

        data = response.json()
        return data

    @property
    def dimension(self):
        """Return the dimension of the embeddings."""
        return 384  # all-MiniLM-L6-v2 has 384 dimensions
