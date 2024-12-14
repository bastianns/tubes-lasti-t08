// src/services/authService.ts

import axiosInstance from '../utils/axios';
import { LoginCredentials, LoginResponse } from '../interfaces/auth';

export const authService = {
  login: async (credentials: LoginCredentials): Promise<string> => {
    try {
      const response = await axiosInstance.post<LoginResponse>('/login', credentials);
      const token = response.data.token;
      localStorage.setItem('token', token);
      return token;
    } catch (error) {
      throw new Error('Invalid credentials');
    }
  },

  logout: async (): Promise<void> => {
    try {
      await axiosInstance.post('/logout');
    } finally {
      localStorage.removeItem('token');
    }
  },

  getToken: (): string | null => {
    return localStorage.getItem('token');
  },
};