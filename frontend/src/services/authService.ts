// src/services/authService.ts
import api from '../utils/axios';

interface LoginCredentials {
  username: string;
  password: string;
}

interface LoginResponse {
  token: string;
}

export const authService = {
  login: async (credentials: LoginCredentials): Promise<LoginResponse> => {
    console.log('Attempting login with:', credentials);
    try {
      const response = await api.post<LoginResponse>('/login', credentials);
      console.log('Login response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Login error in service:', error);
      throw error;
    }
  },

  logout: async () => {
    try {
      // Call the logout endpoint with the token from localStorage
      await api.post('/logout');
      // Clear the token from localStorage
      localStorage.removeItem('token');
      return true;
    } catch (error) {
      console.error('Logout error:', error);
      // Still remove token even if API call fails
      localStorage.removeItem('token');
      throw error;
    }
  }
};