import os
import uuid
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
from flask_cors import CORS
from werkzeug.utils import secure_filename
from rag import add_document, retrieve, assemble_context, get_document_stats, clear_documents
from parsers import extract_text

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

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
os.makedirs("chroma_store", exist_ok=True)

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
        if not text.strip():
            return jsonify({"error": "No text extracted from file", "success": False}), 400

        # Add to RAG system
        doc_id = str(uuid.uuid4())[:8]
        chunks_count = add_document(doc_id=doc_id, source_name=filename, text=text)

        return jsonify({
            "success": True, 
            "message": f"Successfully processed {filename} into {chunks_count} chunks",
            "document": {
                "id": doc_id,
                "name": filename,
                "size": os.path.getsize(path),
                "chunks": chunks_count
            }
        })
    except Exception as e:
        return jsonify({"error": f"Processing failed: {str(e)}", "success": False}), 500

@app.route("/api/documents", methods=["GET"])
def get_documents():
    """Get list of uploaded documents"""
    try:
        documents = []
        uploads_dir = "uploads"
        if os.path.exists(uploads_dir):
            for filename in os.listdir(uploads_dir):
                filepath = os.path.join(uploads_dir, filename)
                if os.path.isfile(filepath):
                    documents.append({
                        "id": str(uuid.uuid4())[:8],
                        "name": filename,
                        "size": os.path.getsize(filepath),
                        "uploadedAt": os.path.getctime(filepath)
                    })
        return jsonify({"success": True, "documents": documents})
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route("/api/clear", methods=["POST"])
def clear_all():
    """Clear all documents and chat history"""
    try:
        # Clear uploads directory
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

def clear_on_startup():
    """Clear previous documents on server startup"""
    print("🧹 Clearing previous documents...")
    uploads_dir = "uploads"
    if os.path.exists(uploads_dir):
        for filename in os.listdir(uploads_dir):
            filepath = os.path.join(uploads_dir, filename)
            if os.path.isfile(filepath):
                os.remove(filepath)
    
    clear_documents()
    print("✅ Previous documents cleared")

if __name__ == "__main__":
    # Clear documents on startup for fresh development
    clear_on_startup()
    
    print("🚀 Starting RAG Chatbot Server...")
    print("📚 Document processing: PDF, DOCX, TXT")
    print("🔍 Vector store: ChromaDB")
    print("🤖 AI: OpenRouter DeepSeek")
    print("🌐 API running on: http://localhost:5000")
    app.run(debug=True, port=5000)