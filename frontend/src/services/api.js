// api.js

// If deployed: uses Render's VITE_API_URL
// If local: falls back to http://localhost:5000
const BACKEND_ORIGIN = import.meta.env.VITE_API_URL ?? 'http://localhost:5000';

const API_BASE = BACKEND_ORIGIN.replace(/\/$/, '') + '/api';

export const apiService = {
  async sendMessage(message) {
    const response = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    return response.json();
  },

  async uploadDocument(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      body: formData,
    });
    return response.json();
  },

  async getDocuments() {
    const response = await fetch(`${API_BASE}/documents`);
    return response.json();
  },

  async healthCheck() {
    const response = await fetch(`${API_BASE}/health`);
    return response.json();
  }
};
