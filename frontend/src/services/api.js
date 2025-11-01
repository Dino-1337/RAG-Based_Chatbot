const API_BASE = 'http://localhost:5000/api';

export const apiService = {
  // Send chat message
  async sendMessage(message) {
    const response = await fetch(`${API_BASE}/chat`, {
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
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      body: formData,
    });
    return response.json();
  },

  // Get documents list
  async getDocuments() {
    const response = await fetch(`${API_BASE}/documents`);
    return response.json();
  },

  // Health check
  async healthCheck() {
    const response = await fetch(`${API_BASE}/health`);
    return response.json();
  }
};