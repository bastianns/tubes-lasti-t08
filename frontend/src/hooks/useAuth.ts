// src/hooks/useAuth.ts
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/authService';

export const useAuth = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const login = async (username: string, password: string) => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await authService.login({ username, password });
      
      if (response && response.token) {
        localStorage.setItem('token', response.token);
        navigate('/dashboard');
      } else {
        setError('Invalid response from server');
      }
    } catch (err: any) {
      let errorMessage = 'Failed to login. Please try again.';
      
      // Handle specific error cases
      if (err.response) {
        switch (err.response.status) {
          case 401:
            errorMessage = 'Invalid username or password';
            break;
          case 404:
            errorMessage = 'Service not available';
            break;
          case 500:
            errorMessage = 'Server error. Please try again later';
            break;
          default:
            errorMessage = err.response.data?.message || errorMessage;
        }
      }
      
      setError(errorMessage);
      throw err; // Re-throw to be handled by the component if needed
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
      localStorage.removeItem('token');
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      navigate('/login');
    }
  };

  return { login, logout, isLoading, error, setError };
};