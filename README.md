# AI-Powered Document Assistant (RAG System)

A Retrieval-Augmented Generation (RAG) system that allows users to upload multiple documents and query them in natural language. The system uses vector embeddings to efficiently retrieve relevant sections and leverages a large language model to generate concise, context-aware responses.

---

## Workflow Summary

1. **Upload** → PDF/TXT/DOCX files.  
2. **Extract text** → using `text_processing.py`.  
3. **Clean & chunk** → split text into manageable pieces.  
4. **Embed chunks** → generate embeddings with HuggingFace/OpenAI.  
5. **Store in FAISS** → handled by `vectorstore.py`.  
6. **Retriever** → find top-k relevant chunks for a query.  
7. **RAG Chain** → combine query + retrieved context.  
8. **LLM** → generate response.  
9. **Display** → Streamlit UI with avatars & styling.  
10. **History** → maintain past context-aware chat.

---

## Features

- Multi-document summarization  
- Structured information extraction  
- Conversational memory for context across queries  
- Scalable handling of long documents  
- Fast and accurate knowledge discovery

---

## Key Technologies

- Python  
- LangChain  
- FAISS  
- Deepseek v3 (free via OpenRouter)  
- Streamlit  
- PDF/TXT parsing (subject to availability, may change)

---

## Impact / Value

- Enables fast and accurate information retrieval from large document collections  
- Reduces manual review time and simplifies knowledge extraction  
- Serves as a foundation for building intelligent assistants, search engines, or reporting tools

---