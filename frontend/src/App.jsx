import { useState, useEffect } from 'react';
import { Send, Upload, File, X, Menu, MessageSquare, Trash2, FileText, Plus, ChevronRight, Search } from 'lucide-react';
import { apiService } from './services/api';

// Sidebar Component
const Sidebar = ({ documents, handleClearChat, onUploadFiles, onClearDocuments, isOpen, onToggle }) => {
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
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onToggle}
        />
      )}

      <div className={`
        fixed lg:static inset-y-0 left-0 z-50
        w-72 sm:w-80 bg-white border-r border-gray-200
        transform transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        flex flex-col
      `}
      style={{ height: '100vh' }}
      >
        <div className="p-4 sm:p-6 border-b border-gray-200 flex-shrink-0">
          <div className="flex items-center justify-between mb-4 sm:mb-6">
            <div className="flex items-center space-x-2 sm:space-x-3">
              <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center">
                <MessageSquare className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
              </div>
              <div>
                <h1 className="text-base sm:text-lg font-semibold text-gray-900">RAG Assistant</h1>
                <p className="text-xs text-gray-500">Document Intelligence</p>
              </div>
            </div>
            <button onClick={onToggle} className="lg:hidden">
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>

          <button
            onClick={handleClearChat}
            className="w-full py-2.5 sm:py-3 px-4 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-xl font-medium hover:from-blue-600 hover:to-indigo-700 transition-all duration-200 flex items-center justify-center space-x-2 shadow-lg shadow-blue-500/30"
          >
            <Plus className="w-4 h-4" />
            <span className="text-sm sm:text-base">New Chat</span>
          </button>
        </div>

        <div className="p-4 sm:p-6 border-b border-gray-200 flex-shrink-0">
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`
              relative border-2 border-dashed rounded-xl p-4 sm:p-6 transition-all duration-200
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
              <div className="w-10 h-10 sm:w-12 sm:h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-2 sm:mb-3">
                <Upload className="w-4 h-4 sm:w-5 sm:h-5 text-blue-600" />
              </div>
              <p className="text-xs sm:text-sm font-medium text-gray-700 mb-1">
                Drop files here
              </p>
              <p className="text-xs text-gray-500">
                or click to browse
              </p>
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 sm:p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xs sm:text-sm font-semibold text-gray-700 uppercase tracking-wide">
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
            <div className="text-center py-6 sm:py-8">
              <div className="w-12 h-12 sm:w-16 sm:h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <FileText className="w-6 h-6 sm:w-7 sm:h-7 text-gray-400" />
              </div>
              <p className="text-xs sm:text-sm text-gray-500">No documents uploaded</p>
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
                      <p className="text-xs sm:text-sm font-medium text-gray-900 truncate">
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
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-3 sm:mb-4`}>
      <div className={`flex items-end space-x-2 max-w-[90%] sm:max-w-[85%] md:max-w-[75%] ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
        {!isUser && (
          <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center flex-shrink-0">
            <MessageSquare className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-white" />
          </div>
        )}
        <div className="flex-1 min-w-0">
          <div
            className={`
              px-3 py-2 sm:px-4 sm:py-3 rounded-2xl
              ${isUser 
                ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-br-md' 
                : 'bg-white border border-gray-200 text-gray-900 rounded-bl-md shadow-sm'
              }
            `}
          >
            <p className="text-xs sm:text-sm leading-relaxed whitespace-pre-wrap break-words">{message.text}</p>
          </div>
          <p className={`text-xs text-gray-500 mt-1 px-2 ${isUser ? 'text-right' : 'text-left'}`}>
            {message.timestamp}
          </p>
        </div>
        {isUser && (
          <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-gradient-to-br from-gray-700 to-gray-900 flex items-center justify-center flex-shrink-0">
            <span className="text-white text-xs sm:text-sm font-medium">U</span>
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
    e?.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input);
      setInput('');
    }
  };

  const suggestedQuestions = [
  "What is this document mainly about?",
  "Can you summarize the key points?",
  "What are the main topics covered?",
  "Are there any recommendations?",
  ]

  return (
    <div className="flex-1 flex flex-col bg-gray-50" style={{ height: '100vh', width: '100%' }}>
      <div className="bg-white border-b border-gray-200 px-4 sm:px-6 py-3 sm:py-4 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 sm:space-x-3">
            <button
              onClick={onToggleSidebar}
              className="lg:hidden p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <Menu className="w-5 h-5 text-gray-600" />
            </button>
            <div>
              <h2 className="text-base sm:text-lg font-semibold text-gray-900">Chat</h2>
              <p className="text-xs sm:text-sm text-gray-500">
                {documentCount > 0 
                  ? `${documentCount} document${documentCount > 1 ? 's' : ''} loaded`
                  : 'No documents loaded'
                }
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-4 sm:py-6">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center max-w-2xl px-4 w-full">
              <div className="w-16 h-16 sm:w-20 sm:h-20 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-3xl flex items-center justify-center mx-auto mb-4 sm:mb-6 shadow-xl shadow-blue-500/30">
                <MessageSquare className="w-8 h-8 sm:w-10 sm:h-10 text-white" />
              </div>
              <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-2 sm:mb-3">
                Welcome to RAG Assistant
              </h2>
              <p className="text-sm sm:text-base text-gray-600 mb-6 sm:mb-8">
                Upload documents and start asking questions. I'll help you find the information you need.
              </p>

              <div className="space-y-3">
                <p className="text-xs sm:text-sm font-medium text-gray-700 mb-3">Try asking:</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-3">
                  {suggestedQuestions.map((question, index) => (
                    <button
                      key={index}
                      onClick={() => onSendMessage(question)}
                      disabled={isLoading}
                      className="p-3 sm:p-4 bg-white border border-gray-200 rounded-xl hover:border-blue-300 hover:bg-blue-50/50 transition-all duration-200 text-left group disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <p className="text-xs sm:text-sm text-white-700 group-hover:text-blue-700">
                        {question}
                      </p>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="w-full max-w-4xl mx-auto">
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            {isLoading && (
              <div className="flex justify-start mb-4">
                <div className="flex items-end space-x-2">
                  <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
                    <MessageSquare className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-white" />
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

      <div className="bg-white border-t border-gray-200 px-4 sm:px-6 py-3 sm:py-4 flex-shrink-0">
        <div className="max-w-4xl mx-auto w-full">
          <div className="flex items-end space-x-2 sm:space-x-3">
            <div className="flex-1">
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
                className="w-full px-3 sm:px-4 py-2 sm:py-3 bg-gray-50 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-sm text-gray-900"
                style={{ minHeight: '44px', maxHeight: '120px' }}
              />
            </div>
            <button
              onClick={handleSubmit}
              disabled={!input.trim() || isLoading}
              className="p-2 sm:p-3 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-xl hover:from-blue-600 hover:to-indigo-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-blue-500/30 flex-shrink-0"
            >
              <Send className="w-4 h-4 sm:w-5 sm:h-5" />
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2 text-center">
            Press Enter to send • Shift+Enter for new line
          </p>
        </div>
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
      const response = await apiService.getDocuments();
      if (response.success) {
        const docs = response.documents.map(doc => ({
          id: doc.id,
          name: doc.name,
          size: formatFileSize(doc.size),
          uploadedAt: new Date(doc.uploadedAt * 1000).toLocaleDateString()
        }));
        setDocuments(docs);
      } else {
        console.error('Failed to load documents:', response.error);
      }
    } catch (error) {
      console.error('Failed to load documents:', error);
    }
  };

  const getAIResponse = async (userMessage) => {
    try {
      const response = await apiService.sendMessage(userMessage);
      if (response.success) {
        return response.message;
      } else {
        return "I'm having trouble processing your request right now. Please try again.";
      }
    } catch (error) {
      console.error('Error getting AI response:', error);
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

  const handleClearChat = async () => {
    try {
      // Clear frontend state immediately - EMPTY arrays
      setMessages([]);
      setDocuments([]);
    
      // Call backend to clear stored documents and vector store
      const response = await fetch('http://localhost:5000/api/clear', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
    
      const result = await response.json();
    
      if (result.success) {
        // DON'T add any message - just leave messages empty
      // This will show the homepage with suggested questions
        console.log("New chat started - returning to homepage");
      }   else {
        console.error('Failed to clear documents: ' + result.error);
      }
    } catch (error) {
      console.error('Error clearing chat:', error);
    }
  };

  const handleUploadFiles = async (files) => {
    for (const file of files) {
      try {
        const response = await apiService.uploadDocument(file);
        if (response.success) {
          const newDocument = {
            id: response.document.id,
            name: response.document.name,
            size: formatFileSize(response.document.size),
            uploadedAt: new Date(response.document.uploadedAt * 1000).toLocaleDateString()
          };
          setDocuments(prev => [...prev, newDocument]);
        } else {
          console.error('Upload failed:', response.error);
          alert(`Failed to upload ${file.name}: ${response.error}`);
        }
      } catch (error) {
        console.error('Upload error:', error);
        alert(`Failed to upload ${file.name}: ${error.message}`);
      }
    }
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
    <div className="flex" style={{ height: '100vh', width: '100vw', overflow: 'hidden' }}>
      <Sidebar
        documents={documents}
        handleClearChat={handleClearChat}
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