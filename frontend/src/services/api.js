import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
const API_TIMEOUT = parseInt(process.env.REACT_APP_API_TIMEOUT) || 5000;

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log(`Making request to: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('Response error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const apiService = {
  // System status
  async getStatus() {
    const response = await api.get('/api/status');
    return response.data;
  },

  // Health check
  async getHealth() {
    const response = await api.get('/health');
    return response.data;
  },

  // Clips API
  async getClips(params = {}) {
    const response = await api.get('/api/clips', { params });
    return response.data;
  },

  async getClip(clipId) {
    const response = await api.get(`/api/clips/${clipId}`);
    return response.data;
  },

  async deleteClip(clipId) {
    const response = await api.delete(`/api/clips/${clipId}`);
    return response.data;
  },

  // Research API  
  async getSightings(params = {}) {
    const response = await api.get('/api/research/sightings', { params });
    return response.data;
  },

  async getTrends(params = {}) {
    const response = await api.get('/api/research/trends', { params });
    return response.data;
  },

  // Settings API
  async getSettings() {
    const response = await api.get('/api/settings');
    return response.data;
  },

  async updateSettings(settings) {
    const response = await api.post('/api/settings', settings);
    return response.data;
  },

  // Stream API
  async getStreamStatus() {
    const response = await api.get('/api/stream/status');
    return response.data;
  },

  async startStream() {
    const response = await api.post('/api/stream/start');
    return response.data;
  },

  async stopStream() {
    const response = await api.post('/api/stream/stop');
    return response.data;
  },

  // Generic API call
  async call(method, endpoint, data = null, params = {}) {
    const config = { params };
    if (data) {
      config.data = data;
    }
    
    const response = await api.request({
      method,
      url: endpoint,
      ...config,
    });
    
    return response.data;
  },
};

export default api;
