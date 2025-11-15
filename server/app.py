import os
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI
from dotenv import load_dotenv
from flask_cors import CORS
from werkzeug.utils import secure_filename

# 🎯 FIX: Load .env from project root (one level up from server/)
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

from rag import add_document, retrieve, assemble_context, get_document_stats, clear_documents
from parsers import extract_text

# 🎯 STEP 1: Configure Flask for production static file serving
app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')
CORS(app)

# OpenRouter DeepSeek API
deepseek_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# System prompt for consistent formatting
SYSTEM_PROMPT = """
You are a helpful AI assistant that reads and summarizes documents clearly and intelligently.

🎯 Your goal:
- **Understand** the document's meaning, not just its words.
- **Summarize** key ideas, insights, and context in your own words.
- **Avoid** copying sentences or paragraphs directly from the source.

🧩 Formatting rules:
- Use clear **section headers with emojis** (e.g., 🔍 Overview, 📊 Key Points, 💡 Insights, ⚠️ Limitations).
- Use **bullet points** for clarity.
- Highlight **important terms or phrases** in bold.
- Keep **spacing clean and readable** for easy scanning.

🧠 Writing style:
- Be **concise yet complete** — focus on what truly matters.
- Maintain a **neutral, factual tone** unless instructed otherwise.
- Ensure the summary feels **human-written and well-organized**.
- If the document has data or findings, **interpret them briefly** instead of repeating numbers.

Example structure:
🔍 **Overview**
Brief 2–3 line summary of what the document is about.

📊 **Key Points**
- Main arguments, findings, or sections summarized in bullet form.

💡 **Insights / Takeaways**
- What can be learned, concluded, or applied from this content.

⚠️ **Limitations / Notes**
- Any missing information, biases, or cautions to note.

Always aim to transform the source into a **clear, insightful summary** — not a copy.
"""

# Create necessary directories
os.makedirs("uploads", exist_ok=True)

@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint"""
    stats = get_document_stats()
    return jsonify({
        "status": "healthy", 
        "service": "RAG Chatbot API",
        "documents_stored": stats,
        "provider": "OpenRouter DeepSeek + ChromaDB RAG"
    })

@app.route("/api/chat", methods=["POST"])
def chat():
    """Main chat endpoint with RAG"""
    data = request.json or {}
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        # Retrieve relevant document chunks using RAG
        hits = retrieve(user_message, top_k=3)
        context = assemble_context(hits)
        
        # Build user prompt based on whether we have context
        if context.strip():
            user_prompt = f"""Context from uploaded documents:
{context}

Question: {user_message}

Please provide a helpful answer based on the context above."""
        else:
            user_prompt = f"""Question: {user_message}

Please provide a helpful response."""

        # Get AI response
        response = deepseek_client.chat.completions.create(
            model="deepseek/deepseek-chat",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ]
        )

        reply = response.choices[0].message.content

        return jsonify({
            "success": True,
            "message": reply,
            "sender": "ai",
            "rag_used": len(hits) > 0,
            "documents_retrieved": len(hits)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/upload", methods=["POST"])
def upload():
    """Handle document upload and processing"""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded", "success": False}), 400

    f = request.files["file"]
    if f.filename == '':
        return jsonify({"error": "No file selected", "success": False}), 400

    filename = secure_filename(f.filename)
    path = os.path.join("uploads", filename)
    f.save(path)

    try:
        # Extract text from document
        text = extract_text(path)
        
        # Get file size before deleting
        file_size = os.path.getsize(path)
        
        # 🎯 DELETE THE FILE AFTER PROCESSING
        os.remove(path)
        
        if not text.strip():
            return jsonify({"error": "No text extracted from file", "success": False}), 400

        # Add to RAG system with better metadata
        doc_id = str(uuid.uuid4())[:8]
        chunks_count = add_document(
            doc_id=doc_id, 
            source_name=filename, 
            text=text,
            file_size=file_size
        )

        return jsonify({
            "success": True, 
            "message": f"✅ Document '{filename}' processed into {chunks_count} chunks",
            "document": {
                "id": doc_id,
                "name": filename,
                "chunks": chunks_count,
                "size": file_size,
                "uploadedAt": int(datetime.now().timestamp()),
                "note": "Original file deleted after processing"
            }
        })
    except Exception as e:
        # Clean up file if processing fails
        if os.path.exists(path):
            os.remove(path)
        return jsonify({"error": f"Processing failed: {str(e)}", "success": False}), 500

@app.route("/api/documents", methods=["GET"])
def get_documents():
    """Get list of processed documents from vector store"""
    try:
        # Get all documents from Chroma to extract metadata
        from rag import collection
        results = collection.get()
        
        documents_map = {}
        
        # Group chunks by document and extract metadata
        if results['metadatas']:
            for i, metadata in enumerate(results['metadatas']):
                doc_id = metadata.get('doc_id')
                source_name = metadata.get('source')
                file_size = metadata.get('file_size')
                uploaded_at = metadata.get('uploaded_at')
                
                if doc_id and source_name:
                    if doc_id not in documents_map:
                        # Convert uploaded_at to timestamp if it's a string
                        if uploaded_at and isinstance(uploaded_at, str):
                            try:
                                dt = datetime.fromisoformat(uploaded_at)
                                timestamp = int(dt.timestamp())
                            except:
                                timestamp = int(datetime.now().timestamp())
                        else:
                            timestamp = int(datetime.now().timestamp())
                        
                        documents_map[doc_id] = {
                            "id": doc_id,
                            "name": source_name,
                            "chunks": 0,
                            "size": file_size or 0,
                            "uploadedAt": timestamp
                        }
                    documents_map[doc_id]["chunks"] += 1
        
        # Convert map to list and sort by upload time (newest first)
        documents = sorted(
            list(documents_map.values()), 
            key=lambda x: x["uploadedAt"], 
            reverse=True
        )
        
        return jsonify({
            "success": True, 
            "documents": documents,
            "note": "Documents loaded from vector store"
        })
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route("/api/clear", methods=["POST"])
def clear_all():
    """Clear all documents and vector store"""
    try:
        # Clear uploads directory (temporary files)
        uploads_dir = "uploads"
        if os.path.exists(uploads_dir):
            for filename in os.listdir(uploads_dir):
                filepath = os.path.join(uploads_dir, filename)
                if os.path.isfile(filepath):
                    os.remove(filepath)
        
        # Clear ChromaDB vector store
        clear_documents()
        
        return jsonify({
            "success": True,
            "message": "All documents and vector store cleared"
        })
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

# 🎯 STEP 1: STATIC FILE SERVING FOR PRODUCTION
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    """Serve React build files in production"""
    static_dir = '../frontend/dist'
    
    # Check if requesting a specific file that exists
    if path != "" and os.path.exists(os.path.join(static_dir, path)):
        return send_from_directory(static_dir, path)
    
    # Otherwise serve the React index.html (for React Router)
    return send_from_directory(static_dir, 'index.html')

def clear_on_startup():
    """Clear previous documents on server startup"""
    print("🧹 Clearing previous documents...")
    uploads_dir = "uploads"
    if os.path.exists(uploads_dir):
        for filename in os.listdir(uploads_dir):
            filepath = os.path.join(uploads_dir, filename)
            if os.path.isfile(filepath):
                os.remove(filepath)
    
    # Clear ChromaDB vector store (this will handle the error gracefully)
    try:
        clear_documents()
        print("✅ Previous documents cleared")
    except Exception as e:
        print(f"⚠️ Could not clear vector store (might be empty): {e}")

if __name__ == "__main__":
    # 🎯 OPTIONAL: Only clear in development, not needed for production
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        print("🚀 Starting RAG Chatbot Server in PRODUCTION mode...")
    else:
        print("🚀 Starting RAG Chatbot Server in DEVELOPMENT mode...")
        clear_on_startup()  # Only clear in development
    
    print("📚 Document processing: PDF, DOCX, TXT")
    print("🔍 Vector store: Chroma Cloud")
    print("🤖 AI: OpenRouter DeepSeek")
    
    # 🎯 STEP 1: PRODUCTION SERVER CONFIG
    if os.environ.get('PORT'):
        port = int(os.environ.get('PORT', 5000))
        print(f"🌐 Production mode running on port: {port}")
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        print("🌐 Development mode running on: http://localhost:5000")
        app.run(debug=True, port=5000)