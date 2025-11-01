# 🤖 RAG-Based Chatbot

A powerful, full-stack Retrieval-Augmented Generation (RAG) chatbot that allows you to upload documents and have intelligent conversations about their content. Built with modern web technologies and AI integration.

![RAG Chatbot](https://img.shields.io/badge/AI-Powered-blue) ![React](https://img.shields.io/badge/React-18.2+-61DAFB) ![Flask](https://img.shields.io/badge/Flask-Python-green)

## ✨ Features

- **📄 Multi-Format Document Support** - Upload and process PDF, DOCX, and TXT files
- **🧠 Intelligent RAG Pipeline** - Semantic search with ChromaDB vector store
- **💬 Smart Conversations** - AI-powered chat using DeepSeek models
- **🎨 Modern UI** - Beautiful, responsive React interface with Tailwind CSS
- **⚡ Real-time Processing** - Instant document ingestion and querying
- **📱 Mobile Friendly** - Fully responsive design for all devices
- **🔒 Secure** - Local document processing with optional cloud AI

## 🛠️ Tech Stack

### Frontend
- **React 18** - Modern UI framework
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful icons
- **Axios** - HTTP client for API calls

### Backend
- **Flask** - Python web framework
- **ChromaDB** - Vector database for embeddings
- **Sentence Transformers** - Text embeddings
- **PyPDF2 & python-docx** - Document parsing
- **OpenAI Client** - DeepSeek AI integration

### AI/ML
- **DeepSeek** - Primary LLM via OpenRouter
- **RAG Pipeline** - Retrieval-Augmented Generation
- **Embeddings** - all-MiniLM-L6-v2 model

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.8+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/rag-chatbot.git
   cd rag-chatbot
   ```

2. **Setup Backend**
   ```bash
   cd server
   python -m venv venv

   # On Windows
   venv\Scripts\activate
   # On Mac/Linux
   source venv/bin/activate

   pip install -r requirements.txt
   ```

3. **Setup Frontend**
   ```bash
   cd frontend
   npm install
   ```

4. **Environment Configuration**
   Create `server/.env`:
   ```
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ```

5. **Run the Application**
   ```bash
   # Terminal 1 - Backend
   cd server
   python app.py

   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

6. **Access the Application**
   Open http://localhost:5173 in your browser

## 📁 Project Structure
```
RAG-Based_Chatbot/
├── frontend/                 # React application
│   ├── src/
│   │   ├── assets/          # Static assets (images, icons)
│   │   ├── hooks/           # Custom React hooks
│   │   ├── services/        # API services and utilities
│   │   ├── styles/          # Additional CSS styles
│   │   ├── App.jsx          # Main application component
│   │   ├── index.css        # Global styles
│   │   ├── main.jsx         # Application entry point
│   │   └── test.jsx         # Test component
│   ├── public/              # Public assets
│   ├── package.json         # Frontend dependencies
│   ├── vite.config.js       # Vite configuration
│   ├── tailwind.config.js   # Tailwind CSS configuration
│   └── postcss.config.js    # PostCSS configuration
├── server/                  # Flask backend
│   ├── app.py               # Main Flask application
│   ├── rag.py               # RAG pipeline logic
│   ├── parsers.py           # Document parsing utilities
│   ├── requirements.txt     # Python dependencies
│   ├── uploads/             # Document storage directory
│   ├── chroma_store/        # ChromaDB vector database
│   └── .env                 # Environment variables
├── chroma_store/            # Global ChromaDB storage
├── .gitignore               # Git ignore rules
├── package.json             # Root package configuration
├── requirements.txt         # Root Python dependencies
└── README.md                # Project documentation
```

## 💡 Usage

1. **Upload Documents**: Drag and drop or click to upload PDF, DOCX, or TXT files
2. **Ask Questions**: Use suggested questions or type your own queries
3. **Get AI-Powered Answers**: Receive context-aware responses based on your documents
4. **Start Fresh**: Use "New Chat" to clear conversation and documents
