import axios from 'axios';

export const apiClient = axios.create({ baseURL: '/api/v1' });

export const serviceClient = axios.create({ baseURL: '/service' });

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

