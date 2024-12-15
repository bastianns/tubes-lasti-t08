// src/utils/axios.ts
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000', // Make sure this matches your Flask server port
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to all requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;  // Add this - very important!
    }
    console.log('Making request to:', config.url, config.data);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for debugging
api.interceptors.response.use(
  (response) => {
    console.log('Response:', response.data);
    return response;
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      const currentPath = window.location.pathname;
      
      // Check if the current path is not the login page
      if (currentPath !== '/login') {
        console.log("Redirecting to login...");
        // Clear any stored tokens or session information
        localStorage.removeItem('token');
        
        // Redirect to the login page
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;