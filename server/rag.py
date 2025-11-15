import chromadb
import os
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from datetime import datetime

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

# 🎯 PROPER ENV VARIABLE HANDLING
chroma_api_key = os.getenv('CHROMA_API_KEY')

if not chroma_api_key:
    raise ValueError("Missing CHROMA_API_KEY in your .env file")

print("🔑 Connecting to Chroma Cloud...")

# CloudClient works with just the API key!
chroma_client = chromadb.CloudClient(api_key=chroma_api_key)

# Get or create collection
collection = chroma_client.get_or_create_collection(
    name="rag_documents",
    metadata={"description": "RAG chatbot document store"}
)

print("✅ Connected to Chroma Cloud successfully!")

# Initialize embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def add_document(doc_id, source_name, text, chunk_size=512, chunk_overlap=50, file_size=None):
    """Add document to vector store with chunking"""
    # Split text into chunks
    chunks = chunk_text(text, chunk_size, chunk_overlap)
    
    # Generate embeddings
    embeddings = embedder.encode(chunks)
    
    # Create document IDs
    doc_ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
    
    # Get current timestamp
    uploaded_at = datetime.now().isoformat()
    
    # Add to Chroma with enhanced metadata
    collection.add(
        embeddings=embeddings.tolist(),
        documents=chunks,
        metadatas=[{
            "source": source_name,
            "doc_id": doc_id,
            "chunk_index": i,
            "total_chunks": len(chunks),
            "file_size": file_size,
            "uploaded_at": uploaded_at
        } for i in range(len(chunks))],
        ids=doc_ids
    )
    
    return len(chunks)

def chunk_text(text, chunk_size=512, chunk_overlap=50):
    """Split text into overlapping chunks"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - chunk_overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        
        if i + chunk_size >= len(words):
            break
            
    return chunks

def retrieve(query, top_k=3):
    """Retrieve relevant document chunks"""
    # Generate query embedding
    query_embedding = embedder.encode([query]).tolist()[0]
    
    # Search in Chroma
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    
    hits = []
    if results['documents']:
        for i, doc in enumerate(results['documents'][0]):
            hits.append({
                "content": doc,
                "metadata": results['metadatas'][0][i],
                "score": 1.0 - (i * 0.1)  # Simple scoring
            })
    
    return hits

def assemble_context(hits):
    """Assemble context from retrieved hits"""
    if not hits:
        return ""
    
    context_parts = []
    for i, hit in enumerate(hits):
        context_parts.append(f"📄 Excerpt from {hit['metadata']['source']}:\n{hit['content']}\n")
    
    return "\n".join(context_parts)

def get_document_stats():
    """Get statistics about stored documents"""
    count = collection.count()
    return {
        "total_chunks": count,
        "collection": "rag_documents"
    }

def clear_documents():
    """Clear all documents from vector store"""
    try:
        # Safe way to clear - check if there are any documents first
        count = collection.count()
        if count > 0:
            # Get all IDs and delete them
            results = collection.get(limit=10000)  # Get all documents
            if results['ids']:
                collection.delete(ids=results['ids'])
            return {"message": f"Cleared {count} documents from vector store"}
        else:
            return {"message": "Vector store was already empty"}
    except Exception as e:
        print(f"Note: Could not clear documents: {e}")
        return {"message": "Vector store is empty or couldn't be cleared"}