import axios from 'axios';

const DJANGO_BASE = 'http://localhost:8000/api/v1';
const FASTAPI_BASE = 'http://localhost:8100';

export const apiClient = axios.create({ baseURL: DJANGO_BASE });

export const serviceClient = axios.create({ baseURL: FASTAPI_BASE });

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
