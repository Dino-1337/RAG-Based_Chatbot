import { useState, useEffect } from 'react';
import { Send, Upload, File, X, Menu, MessageSquare, Trash2, FileText, Plus, ChevronRight, Search } from 'lucide-react';

// Mock API Service
const MockApiService = {
  getDocuments: async () => {
    return [
      { id: '1', name: 'project_requirements.pdf', size: '2.4 MB', uploadedAt: '2024-01-15' },
      { id: '2', name: 'technical_specs.docx', size: '1.8 MB', uploadedAt: '2024-01-15' },
      { id: '3', name: 'user_stories.txt', size: '0.5 MB', uploadedAt: '2024-01-14' }
    ];
  },
  sendMessage: async (message, files) => {
    await new Promise(resolve => setTimeout(resolve, 800));
    const responses = {
      'what are the main project requirements?': 'Based on the uploaded documents, the main project requirements include: 1) Building a RAG chatbot with document upload capability, 2) Implementing vector embeddings for efficient retrieval, 3) Using React + Vite for the frontend with Tailwind CSS styling, and 4) Creating a professional, user-friendly interface.',
      'explain the technical architecture': 'The technical architecture consists of a frontend built with React and Vite, using Tailwind CSS for styling. The backend will implement RAG using vector embeddings to retrieve relevant document sections, which are then fed to an LLM for generating responses.',
      'what\'s the project timeline?': 'The project timeline includes: Phase 1 - UI/UX design (current phase), Phase 2 - Backend RAG implementation, Phase 3 - Integration and testing, Phase 4 - Deployment and optimization.',
    };
    return responses[message.toLowerCase()] || `I've analyzed your documents regarding "${message}". The information suggests this relates to the RAG chatbot development process. Would you like me to provide more specific details from any particular document?`;
  }
};

// Sidebar Component
const Sidebar = ({ documents, onClearChat, onUploadFiles, onClearDocuments, isOpen, onToggle }) => {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files);
    onUploadFiles(files);
  };

  const handleFileInput = (e) => {
    const files = Array.from(e.target.files);
    onUploadFiles(files);
  };

  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onToggle}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed lg:static inset-y-0 left-0 z-50
        w-80 bg-white border-r border-gray-200
        transform transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        flex flex-col
      `}>
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center">
                <MessageSquare className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-gray-900">RAG Assistant</h1>
                <p className="text-xs text-gray-500">Document Intelligence</p>
              </div>
            </div>
            <button onClick={onToggle} className="lg:hidden">
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>

          {/* New Chat Button */}
          <button
            onClick={onClearChat}
            className="w-full py-3 px-4 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-xl font-medium hover:from-blue-600 hover:to-indigo-700 transition-all duration-200 flex items-center justify-center space-x-2 shadow-lg shadow-blue-500/30"
          >
            <Plus className="w-4 h-4" />
            <span>New Chat</span>
          </button>
        </div>

        {/* Upload Area */}
        <div className="p-6 border-b border-gray-200">
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`
              relative border-2 border-dashed rounded-xl p-6 transition-all duration-200
              ${isDragging 
                ? 'border-blue-500 bg-blue-50' 
                : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
              }
            `}
          >
            <input
              type="file"
              multiple
              onChange={handleFileInput}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              accept=".pdf,.doc,.docx,.txt"
            />
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Upload className="w-5 h-5 text-blue-600" />
              </div>
              <p className="text-sm font-medium text-gray-700 mb-1">
                Drop files here
              </p>
              <p className="text-xs text-gray-500">
                or click to browse
              </p>
            </div>
          </div>
        </div>

        {/* Documents List */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
              Documents ({documents.length})
            </h2>
            {documents.length > 0 && (
              <button
                onClick={onClearDocuments}
                className="text-xs text-red-600 hover:text-red-700 font-medium"
              >
                Clear all
              </button>
            )}
          </div>

          {documents.length === 0 ? (
            <div className="text-center py-8">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <FileText className="w-7 h-7 text-gray-400" />
              </div>
              <p className="text-sm text-gray-500">No documents uploaded</p>
              <p className="text-xs text-gray-400 mt-1">Upload files to start chatting</p>
            </div>
          ) : (
            <div className="space-y-2">
              {documents.map((doc) => (
                <div
                  key={doc.id}
                  className="group p-3 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50/50 transition-all duration-200"
                >
                  <div className="flex items-start space-x-3">
                    <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                      <File className="w-4 h-4 text-blue-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {doc.name}
                      </p>
                      <p className="text-xs text-gray-500 mt-0.5">
                        {doc.size} • {doc.uploadedAt}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
};

// Message Bubble Component
const MessageBubble = ({ message }) => {
  const isUser = message.sender === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`flex items-end space-x-2 max-w-[80%] ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
        {!isUser && (
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center flex-shrink-0">
            <MessageSquare className="w-4 h-4 text-white" />
          </div>
        )}
        <div>
          <div
            className={`
              px-4 py-3 rounded-2xl
              ${isUser 
                ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-br-md' 
                : 'bg-white border border-gray-200 text-gray-900 rounded-bl-md shadow-sm'
              }
            `}
          >
            <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.text}</p>
          </div>
          <p className={`text-xs text-gray-500 mt-1 px-2 ${isUser ? 'text-right' : 'text-left'}`}>
            {message.timestamp}
          </p>
        </div>
        {isUser && (
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-gray-700 to-gray-900 flex items-center justify-center flex-shrink-0">
            <span className="text-white text-sm font-medium">U</span>
          </div>
        )}
      </div>
    </div>
  );
};

// Main Chat Interface
const ChatInterface = ({ messages, onSendMessage, isLoading, documentCount, onToggleSidebar }) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input);
      setInput('');
    }
  };

  const suggestedQuestions = [
    "What are the main project requirements?",
    "Explain the technical architecture",
    "What's the project timeline?",
    "Summarize the uploaded documents"
  ];

  return (
    <div className="flex-1 flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <button
              onClick={onToggleSidebar}
              className="lg:hidden p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <Menu className="w-5 h-5 text-gray-600" />
            </button>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Chat</h2>
              <p className="text-sm text-gray-500">
                {documentCount > 0 
                  ? `${documentCount} document${documentCount > 1 ? 's' : ''} loaded`
                  : 'No documents loaded'
                }
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-6 py-6">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center max-w-2xl">
              <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-xl shadow-blue-500/30">
                <MessageSquare className="w-10 h-10 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-3">
                Welcome to RAG Assistant
              </h2>
              <p className="text-gray-600 mb-8">
                Upload documents and start asking questions. I'll help you find the information you need.
              </p>

              {/* Suggested Questions */}
              <div className="space-y-3">
                <p className="text-sm font-medium text-gray-700 mb-3">Try asking:</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {suggestedQuestions.map((question, index) => (
                    <button
                      key={index}
                      onClick={() => onSendMessage(question)}
                      className="p-4 bg-white border border-gray-200 rounded-xl hover:border-blue-300 hover:bg-blue-50/50 transition-all duration-200 text-left group"
                    >
                      <p className="text-sm text-gray-700 group-hover:text-blue-700">
                        {question}
                      </p>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto">
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            {isLoading && (
              <div className="flex justify-start mb-4">
                <div className="flex items-end space-x-2">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
                    <MessageSquare className="w-4 h-4 text-white" />
                  </div>
                  <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-md px-4 py-3 shadow-sm">
                    <div className="flex space-x-2">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-gray-200 px-6 py-4">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
          <div className="flex items-end space-x-3">
            <div className="flex-1 relative">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit(e);
                  }
                }}
                placeholder="Ask a question about your documents..."
                rows="1"
                className="w-full px-4 py-3 pr-12 bg-gray-50 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-sm"
                style={{ minHeight: '48px', maxHeight: '120px' }}
              />
            </div>
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="p-3 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-xl hover:from-blue-600 hover:to-indigo-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-blue-500/30"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2 text-center">
            Press Enter to send • Shift+Enter for new line
          </p>
        </form>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const docs = await MockApiService.getDocuments();
      setDocuments(docs);
    } catch (error) {
      console.error('Failed to load documents:', error);
    }
  };

  const getAIResponse = async (userMessage) => {
    try {
      const response = await MockApiService.sendMessage(userMessage, uploadedFiles);
      return response;
    } catch (error) {
      return "I'm having trouble processing your request right now. Please try again.";
    }
  };

  const handleSendMessage = async (message) => {
    if (!message.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      text: message,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    const aiResponse = await getAIResponse(message);
    
    const aiMessage = {
      id: Date.now() + 1,
      text: aiResponse,
      sender: 'ai',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, aiMessage]);
    setIsLoading(false);
  };

  const handleClearChat = () => {
    setMessages([]);
  };

  const handleUploadFiles = (files) => {
    const newDocuments = files.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      size: formatFileSize(file.size),
      uploadedAt: new Date().toLocaleDateString()
    }));

    setUploadedFiles(prev => [...prev, ...files]);
    setDocuments(prev => [...prev, ...newDocuments]);
  };

  const handleClearDocuments = () => {
    setUploadedFiles([]);
    setDocuments([]);
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Sidebar 
        documents={documents}
        onClearChat={handleClearChat}
        onUploadFiles={handleUploadFiles}
        onClearDocuments={handleClearDocuments}
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
      />
      
      <ChatInterface 
        messages={messages}
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
        documentCount={documents.length}
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
      />
    </div>
  );
}

export default App;