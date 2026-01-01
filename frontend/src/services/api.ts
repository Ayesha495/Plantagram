import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Base URL for your Django backend
// Use your computer's local IP address, not localhost
// Find it by running: ipconfig (Windows) or ifconfig (Mac/Linux)
const API_BASE_URL = 'http://192.168.100.13/api';  // Replace with YOUR IP

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
});

// Request interceptor - Add auth token to every request
api.interceptors.request.use(
  async (config) => {
    try {
      const token = await AsyncStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      console.error('Error getting token:', error);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle token refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired - redirect to login
      await AsyncStorage.removeItem('access_token');
      await AsyncStorage.removeItem('refresh_token');
      // You'll handle redirect in your component
    }
    return Promise.reject(error);
  }
);

export default api;