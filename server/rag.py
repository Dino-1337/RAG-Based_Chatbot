import os
import chromadb
from sentence_transformers import SentenceTransformer
import hashlib
from typing import List, Dict

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_store")
collection = chroma_client.get_or_create_collection(name="documents")

# Initialize embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def chunk_text(text: str, chunk_size: int = 512, chunk_overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - chunk_overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)
        if i + chunk_size >= len(words):
            break
    
    return chunks

def add_document(doc_id: str, source_name: str, text: str) -> int:
    """Add document to vector store and return number of chunks"""
    # Clean and chunk text
    cleaned_text = ' '.join(text.split())
    chunks = chunk_text(cleaned_text)
    
    if not chunks:
        return 0
    
    # Generate embeddings and store in ChromaDB
    embeddings = embedding_model.encode(chunks).tolist()
    
    # Create unique IDs for each chunk
    chunk_ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
    
    # Prepare metadata
    metadatas = [{
        "doc_id": doc_id,
        "source": source_name,
        "chunk_index": i,
        "chunk_size": len(chunk.split())
    } for i, chunk in enumerate(chunks)]
    
    # Add to ChromaDB
    collection.add(
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
        ids=chunk_ids
    )
    
    return len(chunks)

def retrieve(query: str, top_k: int = 5) -> List[Dict]:
    """Retrieve relevant document chunks for a query"""
    # Generate query embedding
    query_embedding = embedding_model.encode([query]).tolist()[0]
    
    # Search in ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )
    
    hits = []
    if results['documents']:
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        )):
            hits.append({
                "content": doc,
                "metadata": metadata,
                "score": 1 - distance,  # Convert distance to similarity score
                "rank": i + 1
            })
    
    return hits

def assemble_context(hits: List[Dict]) -> str:
    """Assemble retrieved chunks into context"""
    if not hits:
        return ""
    
    context_parts = []
    for hit in hits:
        source = hit['metadata']['source']
        chunk_idx = hit['metadata']['chunk_index']
        content = hit['content']
        
        context_parts.append(f"[From {source}, part {chunk_idx + 1}]: {content}")
    
    return "\n\n".join(context_parts)

def get_document_stats():
    """Get statistics about stored documents"""
    return collection.count()

def clear_documents():
    """Clear all documents from vector store"""
    global collection
    chroma_client.delete_collection(name="documents")
    collection = chroma_client.get_or_create_collection(name="documents")