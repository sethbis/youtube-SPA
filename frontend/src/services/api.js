import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authService = {
  register: (name, email, password) => api.post('/users', { name, email, password }),
  login: (email, password) => api.post('/login', { email, password }),
  getUser: (id) => api.get(`/users/${id}`),
};

export const videoService = {
  getVideos: (params = {}) => api.get('/videos', { params }),
  getVideoById: (id) => api.get(`/videos/${id}`),
  uploadVideo: (formData) => api.post('/videos', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  updateVideo: (id, data) => api.put(`/videos/${id}`, data),
  deleteVideo: (id) => api.delete(`/videos/${id}`),
};

export const commentService = {
  getComments: (videoId) => api.get(`/videos/${videoId}/comments`),
  addComment: (videoId, content) => api.post(`/videos/${videoId}/comments`, { content }),
};

export default api;
