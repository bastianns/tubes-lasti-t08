// src/context/AuthContext.tsx

import { createContext, useContext, useState, useEffect } from 'react';
import { AuthContextType, AuthProviderProps, AuthState, LoginCredentials } from '../interfaces/auth';
import { authService } from '../services/authService';

const defaultAuthState: AuthState = {
  isAuthenticated: false,
  token: null,
  loading: true,
  error: null,
};

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [state, setState] = useState<AuthState>(defaultAuthState);

  useEffect(() => {
    const token = authService.getToken();
    if (token) {
      setState({
        isAuthenticated: true,
        token,
        loading: false,
        error: null,
      });
    } else {
      setState(prev => ({ ...prev, loading: false }));
    }
  }, []);

  const login = async (credentials: LoginCredentials) => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      const token = await authService.login(credentials);
      setState({
        isAuthenticated: true,
        token,
        loading: false,
        error: null,
      });
    } catch (error) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error.message : 'An error occurred',
      }));
      throw error;
    }
  };

  const logout = async () => {
    try {
      setState(prev => ({ ...prev, loading: true }));
      await authService.logout();
    } finally {
      setState({
        isAuthenticated: false,
        token: null,
        loading: false,
        error: null,
      });
    }
  };

  return (
    <AuthContext.Provider value={{ ...state, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};