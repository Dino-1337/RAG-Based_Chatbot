// Generate or retrieve session ID
const getOrCreateSessionId = () => {
  let sessionId = localStorage.getItem('rag_session_id');
  if (!sessionId) {
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('rag_session_id', sessionId);
  }
  return sessionId;
};

// Get current session ID without creating new one
const getCurrentSessionId = () => {
  return localStorage.getItem('rag_session_id');
};

// Use environment variable for API base URL
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

export const apiService = {
  // Send chat message
  async sendMessage(message) {
    const sessionId = getOrCreateSessionId();
    const response = await fetch(`${API_BASE}/chat?session_id=${sessionId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });
    return response.json();
  },

  // Upload document
  async uploadDocument(file) {
    const sessionId = getOrCreateSessionId();
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE}/upload?session_id=${sessionId}`, {
      method: 'POST',
      body: formData,
    });
    return response.json();
  },

  // Get documents list
  async getDocuments() {
    const sessionId = getOrCreateSessionId();
    const response = await fetch(`${API_BASE}/documents?session_id=${sessionId}`);
    return response.json();
  },

  // Clear documents for SPECIFIC session
  async clearSessionDocuments(sessionId) {
    const response = await fetch(`${API_BASE}/clear?session_id=${sessionId}`, {
      method: 'POST',
    });
    return response.json();
  },

  // Health check
  async healthCheck() {
    const sessionId = getOrCreateSessionId();
    const response = await fetch(`${API_BASE}/health?session_id=${sessionId}`);
    return response.json();
  },

  // Session management
  getCurrentSessionId,
  getOrCreateSessionId
};