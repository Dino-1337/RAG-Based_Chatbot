import chromadb
import os
import time
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

# 🎯 PROPER ENV VARIABLE HANDLING
chroma_api_key = os.getenv('CHROMA_API_KEY')

if not chroma_api_key:
    raise ValueError("Missing CHROMA_API_KEY in your .env file")

print("🔑 Connecting to Chroma Cloud...")

# CloudClient works with just the API key!
chroma_client = chromadb.CloudClient(api_key=chroma_api_key)

print("✅ Connected to Chroma Cloud successfully!")

def cleanup_old_sessions(max_age_hours=2):
    """Delete sessions older than specified hours"""
    try:
        collections = chroma_client.list_collections()
        current_time = time.time()
        deleted_count = 0
        
        for collection in collections:
            if collection.name.startswith("rag_documents_session_"):
                # Extract timestamp: session_1731758072345_abc123
                parts = collection.name.split('_')
                if len(parts) >= 3 and parts[2].isdigit():
                    session_time = int(parts[2]) / 1000  # Convert milliseconds to seconds
                    
                    # Check if session is older than max_age_hours
                    if current_time - session_time > max_age_hours * 60 * 60:
                        chroma_client.delete_collection(collection.name)
                        deleted_count += 1
                        print(f"🧹 Deleted old session: {collection.name}")
        
        if deleted_count > 0:
            print(f"✅ Cleaned up {deleted_count} old sessions")
            
    except Exception as e:
        print(f"⚠️ Session cleanup failed: {e}")

def get_user_collection(session_id):
    """Get or create collection for specific session"""
    # Run cleanup before creating new collections
    cleanup_old_sessions(max_age_hours=2)
    
    collection_name = f"rag_documents_{session_id}"
    return chroma_client.get_or_create_collection(
        name=collection_name,
        metadata={"description": f"RAG documents for session {session_id}"}
    )

def add_document(doc_id, source_name, text, session_id="default", chunk_size=512, chunk_overlap=50, file_size=None):
    """Add document to vector store with chunking"""
    collection = get_user_collection(session_id)
    
    # Split text into chunks
    chunks = chunk_text(text, chunk_size, chunk_overlap)
    
    # Create document IDs
    doc_ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
    
    # Add to Chroma - it will automatically generate embeddings
    collection.add(
        documents=chunks,
        metadatas=[{
            "source": source_name,
            "doc_id": doc_id,
            "chunk_index": i,
            "total_chunks": len(chunks),
            "file_size": file_size,
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

def retrieve(query, session_id="default", top_k=3):
    """Retrieve relevant document chunks"""
    collection = get_user_collection(session_id)
    
    # Search in Chroma - it will automatically embed the query
    results = collection.query(
        query_texts=[query],
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

def get_document_stats(session_id="default"):
    """Get statistics about stored documents"""
    collection = get_user_collection(session_id)
    count = collection.count()
    return {
        "total_chunks": count,
        "collection": f"rag_documents_{session_id}"
    }

def clear_documents(session_id="default"):
    """Clear all documents from vector store for specific session"""
    try:
        collection = get_user_collection(session_id)
        # Get all document IDs and delete them
        results = collection.get()
        if results['ids']:
            collection.delete(ids=results['ids'])
        return {"message": f"Cleared documents for session {session_id}"}
    except Exception as e:
        print(f"Note: Could not clear documents for session {session_id}: {e}")
        return {"message": f"Vector store for session {session_id} is empty or couldn't be cleared"}

# Run cleanup on module import (server startup)
print("🧹 Running initial session cleanup...")
cleanup_old_sessions(max_age_hours=2)