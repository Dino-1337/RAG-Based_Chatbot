import os

# Hugging Face API Configuration
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN", "")

# Model Configuration
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Chunking Configuration
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_OVERLAP = 200

# Vector Store Configuration
VECTOR_DIMENSION = 384  # Dimension for all-MiniLM-L6-v2

# RAG Configuration
RETRIEVER_K = 5

# DeepSeek API Configuration (if needed)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
